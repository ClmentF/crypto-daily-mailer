FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PORT=8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
