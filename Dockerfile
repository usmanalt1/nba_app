# Cloud Run image. Local compose builds docker/backend.Dockerfile instead; this one
# exists at the root because `gcloud run deploy --source .` only looks here.
FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/nba_app/backend/src \
    DJANGO_SETTINGS_MODULE=app.settings

WORKDIR /nba_app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        gcc \
        libmariadb-dev \
        pkg-config \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m automater && chown -R automater:automater /nba_app
USER automater

# ASGI, not runserver: the model and llm routers expose async endpoints. Cloud Run
# injects PORT, so this has to be the shell form to expand it.
CMD exec uvicorn app.asgi:application --host 0.0.0.0 --port ${PORT:-8080}
