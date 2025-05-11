Python AI Proxy with Palo Alto AIRS + Ollama + OpenWebUI
============================================================

This project implements a secure reverse proxy in Python between OpenWebUI and Ollama,
adding a real-time security layer using Palo Alto Networks AIRS.

The proxy intercepts every user prompt and model response to analyze it for
malicious or sensitive content. If approved, the prompt or response is forwarded;
otherwise, it is blocked with an appropriate explanation.

------------------------------------------------------------
Features
------------------------------------------------------------

- Scans user prompts using AIRS before reaching the LLM
- Scans model responses before returning to the user
- Transparent fallback proxy for other Ollama API routes
- Blocks toxic, malicious, or sensitive content
- Fully dockerized for fast deployment
- Compatible with OpenWebUI + Ollama models (e.g. LLaMA3)

------------------------------------------------------------
Requirements
------------------------------------------------------------

- Docker & Docker Compose
- A `.env` file with AIRS credentials:

PANW_X_PAN_TOKEN=your-token
PANW_PROFILE_ID=your-profile-id
PANW_PROFILE_NAME=your-profile-name

------------------------------------------------------------
How to Use (Quickstart)
------------------------------------------------------------

1. Clone the repository:
   git clone https://github.com/your-user/python_ai_proxy.git
   cd python_ai_proxy

2. Add a `.env` file with your AIRS credentials.

3. Build & run the stack:
   docker-compose up --build

4. Open OpenWebUI at:
   http://localhost:8080

------------------------------------------------------------
Project Structure
------------------------------------------------------------

.
├── airs.py              # AIRS integration logic
├── main.py              # FastAPI application
├── ollama.py            # Helper for Ollama calls
├── Dockerfile           # Python proxy container
├── docker-compose.yml   # Full stack definition
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (ignored by git)

------------------------------------------------------------
Example Blocked Response
------------------------------------------------------------

{
  "message": {
    "role": "assistant",
    "content": "⛔ Response blocked by Palo Alto AIRS.\n\nCategory: sensitive_content\nSuggestion: Please reformulate your prompt."
  },
  "done": true
}

------------------------------------------------------------
🧰 Tech Stack
------------------------------------------------------------

- Python 3.11
- FastAPI + Uvicorn
- aiohttp + requests
- OpenWebUI frontend
- Ollama for local models
- Palo Alto Networks AIRS

------------------------------------------------------------
📄 License
------------------------------------------------------------

MIT License — see LICENSE for details.

------------------------------------------------------------
🙏 Credits
------------------------------------------------------------

- Based on Palo Alto Networks AIRS API
- Powered by Ollama + OpenWebUI