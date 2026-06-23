# ── Stage 1: build the React frontend ────────────────────────────────────────
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Result: /frontend/dist

# ── Stage 2: Python backend + embedded static assets ─────────────────────────
FROM python:3.12-slim AS backend

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Use uv for fast dependency resolution
RUN pip install --no-cache-dir uv

COPY backend/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY backend/app/ ./app/

# Copy compiled frontend into a location FastAPI can serve
COPY --from=frontend-builder /frontend/dist ./static

# Bake policy docs into the image so they're available without a bind mount
COPY .data/policy ./.data/policy

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
