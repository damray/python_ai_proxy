import aiohttp
import logging
import os
import uuid

AIRS_URL = "https://service.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request"

async def scan_with_airs(prompt: str, response: str = "N/A", code_prompt: str = "N/A", code_response: str = "N/A") -> dict:
    token = os.getenv("PANW_X_PAN_TOKEN")
    profile_id = os.getenv("PANW_PROFILE_ID")
    profile_name = os.getenv("PANW_PROFILE_NAME")

    if not all([token, profile_id, profile_name]):
        logging.error("❌ Variables d'environnement AIRS manquantes")
        raise ValueError("Missing AIRS environment variables")

    tr_id = str(uuid.uuid4())
    logging.info(f"🔍 Envoi vers AIRS (tr_id: {tr_id})...")

    payload = {
        "tr_id": tr_id,
        "ai_profile": {
            "profile_id": profile_id,
            "profile_name": profile_name
        },
        "metadata": {
            "app_name": "python_proxy",
            "app_user": "user_dam",
            "ai_model": "Ollama3"
        },
        "contents": [{
            "prompt": prompt if prompt.strip() else "N/A",
            "response": response if response.strip() else "N/A",
            "code_prompt": code_prompt if code_prompt.strip() else "N/A",
            "code_response": code_response if code_response.strip() else "N/A"
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-pan-token": token
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AIRS_URL, json=payload, headers=headers, timeout=30) as resp:
                body = await resp.json()
                if resp.status != 200:
                    logging.error(f"❌ Réponse AIRS NOK [{resp.status}]: {body}")
                    raise ValueError(f"Erreur AIRS: {body}")
                logging.info(f"✅ Réponse AIRS OK [{resp.status}]")
                return body

    except Exception as e:
        logging.exception("❌ Exception lors de l'appel à AIRS")
        raise e
