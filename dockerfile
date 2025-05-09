# ------------ Build Image ------------
    FROM python:3.11-slim

    # Crée le dossier de travail
    WORKDIR /app
    
    # Copie uniquement le dossier python_proxy dans le conteneur
    COPY ./python_proxy /app/python_proxy
    
    # Définit le dossier principal pour FastAPI
    WORKDIR /app/python_proxy
    
    # Installation des dépendances nécessaires
    RUN pip install --no-cache-dir fastapi uvicorn httpx python-dotenv
    
    # Expose le port du proxy
    EXPOSE 8000
    
    # Lance l’application FastAPI
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    