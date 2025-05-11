import os
import uuid
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("airs")
logging.basicConfig(level=logging.INFO)

AIRS_URL = "https://service.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request"

async def scan_with_airs(prompt: str, response: str = "", code_prompt: str = "N/A", code_response: str = "N/A") -> dict:
    """Scan le prompt ou la réponse via AIRS."""
    token = os.getenv("PANW_X_PAN_TOKEN")
    profile_id = os.getenv("PANW_PROFILE_ID")
    profile_name = os.getenv("PANW_PROFILE_NAME")

    if not token or not profile_id or not profile_name:
        logger.error("❌ Variables d'environnement manquantes (TOKEN, PROFILE_ID, PROFILE_NAME)")
        raise ValueError("Environnement AIRS incomplet.")

    tr_id = str(uuid.uuid4())
    logger.info(f"🔍 Envoi vers AIRS (tr_id: {tr_id})...")

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
        "contents": [
            {
                "prompt": prompt or "N/A",
                "response": response or "N/A",
                "code_prompt": code_prompt or "N/A",
                "code_response": code_response or "N/A"
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-pan-token": token
    }

    try:
        res = requests.post(AIRS_URL, headers=headers, json=payload)
        if res.status_code != 200:
            logger.warning(f"❌ Réponse AIRS NOK [{res.status_code}]: {res.text}")
            return {"action": "blocked", "reason": "airs_error", "details": res.text}
        result = res.json()
        logger.info(f"✅ Réponse AIRS OK [{res.status_code}] - Action: {result.get('action')}")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur lors de la requête vers AIRS: {e}")
        return {"action": "blocked", "reason": "exception", "details": str(e)}
