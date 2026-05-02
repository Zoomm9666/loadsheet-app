# ── Multi-stage build для Aviation Loadsheet App ──────────────
# Stage 1: build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim

WORKDIR /app

# Системные шрифты для PDF-генерации (Liberation Sans ≈ Arial)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные Python-пакеты
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY . .

# Порт по умолчанию для Cloud Run
ENV PORT=8080
EXPOSE 8080

# Flet веб-сервер
CMD ["python", "main.py"]
