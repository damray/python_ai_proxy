# Utilise une image Python officielle légère
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier le dossier contenant le code
COPY ./python_proxy /app

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Lancer le serveur Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
