# =============================================================================
# PSPD Guardian — Backend Dockerfile
# Django 5 + Gunicorn + Sentence Transformers + Qdrant Client + Ollama Client
# =============================================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies for psycopg2, build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Stage 1 — Install Python dependencies
# ---------------------------------------------------------------------------
FROM base AS deps

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — Pre-download the embedding model so it's baked into the image
# ---------------------------------------------------------------------------
FROM deps AS model-cache

RUN python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('all-MiniLM-L6-v2'); \
print('Embedding model cached successfully')"

# ---------------------------------------------------------------------------
# Stage 3 — Final runtime image
# ---------------------------------------------------------------------------
FROM model-cache AS runtime

# Copy application source
COPY backend/ /app/

# Copy entrypoint
COPY docker/entrypoint-backend.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/api/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
