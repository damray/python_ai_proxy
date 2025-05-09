import aiohttp
import logging
import os

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/api/chat")

async def call_ollama(payload: dict) -> dict:
    logging.info(f"📡 Appel vers Ollama à {OLLAMA_URL}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload, timeout=120) as response:
                if response.status != 200:
                    logging.error(f"❌ Erreur Ollama [{response.status}]: {await response.text()}")
                    return {
                        "message": {
                            "role": "assistant",
                            "content": "❌ Erreur de traitement par le modèle LLM local (Ollama)."
                        },
                        "done": True
                    }

                data = await response.json()
                logging.info("🧠 Réponse LLM reçue depuis Ollama")
                return data

    except Exception as e:
        logging.exception("❌ Exception lors de l'appel à Ollama")
        return {
            "message": {
                "role": "assistant",
                "content": "❌ Exception lors de l’appel au modèle Ollama."
            },
            "done": True
        }
