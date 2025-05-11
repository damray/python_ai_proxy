import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
import aiohttp

from airs import scan_with_airs

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy")

OLLAMA_BASE = "http://ollama:11434"

@app.post("/api/chat")
async def handle_chat(request: Request):
    logger.info("📥 Nouvelle requête POST /api/chat reçue.")
    
    # Lire le corps
    body_bytes = await request.body()
    try:
        body_json = json.loads(body_bytes)
        logger.info("✅ JSON reçu depuis OpenWebUI.")
    except Exception:
        logger.error("❌ JSON malformé.")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    # Extraction du prompt
    prompt = ""
    try:
        messages = body_json.get("messages", [])
        prompt = next(m["content"] for m in reversed(messages) if m["role"] == "user")
        logger.info(f"🧠 Prompt extrait : {prompt}")
    except Exception:
        logger.error("❌ Format incorrect du champ 'messages'.")
        return JSONResponse(status_code=400, content={"error": "Invalid message format"})

    # Scan du prompt via AIRS
    try:
        logger.info("🔍 Envoi du prompt vers AIRS pour analyse...")
        scan = await scan_with_airs(prompt, "N/A", "N/A", "N/A")
        if scan["action"] != "allow":
            logger.warning(f"⛔ Prompt bloqué par AIRS : {scan['category']}")
            return JSONResponse(status_code=200, content={
                "message": {
                    "role": "assistant",
                    "content": f"⛔ Prompt bloqué par la sécurité AI Palo Alto Networks.\n\nCatégorie : {scan['category']}\nSuggestion : reformulez votre question."
                },
                "done": True
            })
        logger.info("✅ Prompt autorisé par AIRS.")
    except Exception as e:
        logger.error(f"❌ Erreur pendant le scan prompt : {e}")
        return JSONResponse(status_code=500, content={"error": "Prompt scan failed"})

    # Appel Ollama
    logger.info("➡️ Forward du prompt vers Ollama...")
    answer = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{OLLAMA_BASE}/api/chat", data=body_bytes, headers={"Content-Type": "application/json"}) as resp:
                if resp.status != 200:
                    error_body = await resp.text()
                    logger.error(f"❌ Erreur Ollama [{resp.status}] : {error_body}")
                    return JSONResponse(status_code=502, content={"error": "Ollama error"})

                logger.info("📡 Lecture de la réponse NDJSON de Ollama...")
                async for line in resp.content:
                    try:
                        decoded = line.decode("utf-8").strip()
                        if not decoded:
                            continue
                        data = json.loads(decoded)
                        if "message" in data and "content" in data["message"]:
                            answer += data["message"]["content"]
                    except Exception as e:
                        logger.warning(f"❌ Ligne NDJSON non interprétable : {e}")
    except Exception as e:
        logger.error(f"❌ Échec lors de l’appel à Ollama : {e}")
        return JSONResponse(status_code=500, content={"error": "Ollama call failed"})

    logger.info(f"💬 Réponse brute Ollama récupérée : {answer[:100]}...")

    # Scan de la réponse AI
    try:
        logger.info("🔍 Envoi de la réponse vers AIRS pour revalidation...")
        scan = await scan_with_airs("N/A", answer, "N/A", "N/A")
        if scan["action"] != "allow":
            logger.warning(f"⛔ Réponse bloquée par AIRS : {scan['category']}")
            return JSONResponse(status_code=200, content={
                "message": {
                    "role": "assistant",
                    "content": f"⛔ Réponse bloquée par la sécurité AI Palo Alto Networks.\n\nCatégorie : {scan['category']}\nSuggestion : reformulez votre question."
                },
                "done": True
            })
        logger.info("✅ Réponse autorisée par AIRS.")
    except Exception as e:
        logger.error(f"❌ Erreur pendant le scan réponse : {e}")
        return JSONResponse(status_code=500, content={"error": "Response scan failed"})

    # Envoi vers OpenWebUI
    logger.info("📤 Envoi final de la réponse à OpenWebUI.")
    return JSONResponse(status_code=200, content={
        "message": {
            "role": "assistant",
            "content": answer
        },
        "done": True
    })


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def fallback_forward(full_path: str, request: Request):
    logger.info(f"🔁 Proxy fallback call to: /{full_path}")
    
    method = request.method
    body = await request.body()
    headers = dict(request.headers)
    target_url = f"{OLLAMA_BASE}/{full_path}"

    async with aiohttp.ClientSession() as session:
        async with session.request(method, target_url, data=body, headers=headers) as resp:
            content = await resp.read()
            logger.info(f"✅ Fallback vers Ollama terminé avec code: {resp.status}")
            return StreamingResponse(
                content=iter([content]),
                status_code=resp.status,
                headers=resp.headers
            )