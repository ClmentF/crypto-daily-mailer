FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Paquets système utiles pour pandas/lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install --no-cache-dir uv

# Copier les fichiers de projet pour que uv puisse lire tes dépendances
COPY pyproject.toml ./
COPY uv.lock ./        

# Installer les deps définies par uv/pyproject
RUN uv sync --frozen --no-dev

# Copier le reste du code
COPY . .

# Démarrer l’API
ENV PORT=8080
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
