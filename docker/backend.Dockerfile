FROM python:3.9-slim

LABEL org.opencontainers.image.authors="UA"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/London \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_DIR=/nba_app \
    USER_NAME=automater \
    AWS_DEFAULT_REGION=eu-west-2 \
    FLASK_APP=api/app.py

# Install system dependencies (including build tools for Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        awscli \
        build-essential \
        default-mysql-client \
        default-libmysqlclient-dev \
        gcc \
        git \
        libpq-dev \
        libmariadb-dev \
        openssh-client \
        pkg-config \
        python3-dev \
        vim \
        nano && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip wheel

# Create non-root user
RUN useradd -m $USER_NAME -s /bin/bash

# Create app directory
RUN mkdir $APP_DIR && chown $USER_NAME:$USER_NAME $APP_DIR
WORKDIR $APP_DIR

# Copy requirements and install Python dependencies to system Python
COPY --chown=$USER_NAME:$USER_NAME requirements.txt .
RUN echo "Contents of requirements.txt:" && \
    cat requirements.txt && \
    echo "=== Installing packages to system Python ===" && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "=== Installation completed ===" && \
    pip list

# Copy application code
COPY --chown=$USER_NAME:$USER_NAME . .

# Switch to non-root user
USER $USER_NAME

# Make entrypoint executable
RUN chmod +x  ./scripts/entrypoint.sh

EXPOSE 5000

CMD ["python", "backend/src/manage.py", "runserver", "0.0.0.0:8000"]