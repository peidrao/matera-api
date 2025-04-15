# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 👇 Copia e dá permissão ao entrypoint dentro da imagem
COPY .docker/entrypoint.sh /app/.docker/entrypoint.sh
RUN chmod +x /app/.docker/entrypoint.sh

COPY . .

ENTRYPOINT ["/app/.docker/entrypoint.sh"]
