from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import aiohttp
import asyncio
import logging
from airs import scan_with_airs
from ollama import call_ollama

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.post("/api/chat")
async def handle_chat(request: Request):
    try:
        body = await request.json()
        messages = body.get("messages", [])
        user_prompt = next((msg["content"] for msg in reversed(messages) if msg.get("role") == "user"), "")

        logging.info(f"🧠 Unified prompt received: {user_prompt}")

        # 1. Analyse du prompt via AIRS
        prompt_scan = await scan_with_airs(prompt=user_prompt, response="", code_prompt="", code_response="")

        if prompt_scan.get("action") != "allow":
            logging.warning(f"⛔ Prompt bloqué par AIRS: {prompt_scan.get('category')}")
            return JSONResponse(content={
                "message": {
                    "role": "assistant",
                    "content": f"⛔ Prompt bloqué par la sécurité AI Palo Alto Networks.\n\nCatégorie : {prompt_scan.get('category')}\nSuggestion : Reformulez votre question."
                },
                "done": True
            })

        # 2. Forward vers Ollama
        logging.info("✅ Prompt autorisé par AIRS, envoi vers Ollama...")
        ollama_response = await call_ollama(body)

        # 3. Analyse de la réponse de Ollama via AIRS
        answer = ollama_response.get("message", {}).get("content", "")
        response_scan = await scan_with_airs(prompt="", response=answer, code_prompt="", code_response="")

        if response_scan.get("action") != "allow":
            logging.warning(f"⛔ Réponse bloquée par AIRS: {response_scan.get('category')}")
            return JSONResponse(content={
                "message": {
                    "role": "assistant",
                    "content": f"⛔ Réponse bloquée par la sécurité AI Palo Alto Networks.\n\nCatégorie : {response_scan.get('category')}\nSuggestion : Reformulez votre question."
                },
                "done": True
            })

        # 4. Réponse finale vers OpenWebUI
        logging.info("✅ Réponse autorisée par AIRS, réponse transmise à OpenWebUI.")
        return JSONResponse(content=ollama_response)

    except Exception as e:
        logging.exception("❌ Erreur dans le traitement /api/chat")
        return JSONResponse(content={"error": "Erreur interne dans le proxy"}, status_code=500)
