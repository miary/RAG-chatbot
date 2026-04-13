#!/bin/bash
set -e

echo "=========================================="
echo " CBP Training Assistant — Backend Startup"
echo "=========================================="

# ---------------------------------------------------------------------------
# 1. Verify local models are available
# ---------------------------------------------------------------------------
echo "[1/6] Checking local embedding models..."
MODELS_PATH="${MODELS_DIR:-/app/models}"
if [ -d "$MODELS_PATH" ]; then
    echo "  Models directory: $MODELS_PATH"
    ls -la "$MODELS_PATH" 2>/dev/null | head -5 || true
else
    echo "  WARNING: Models directory not found at $MODELS_PATH"
    echo "  Models will be downloaded on first use (slower startup)"
fi

# ---------------------------------------------------------------------------
# 2. Wait for PostgreSQL to be ready
# ---------------------------------------------------------------------------
echo "[2/6] Waiting for PostgreSQL at ${PG_DB_HOST:-localhost}:${PG_DB_PORT:-5432}..."
until python -c "
import psycopg2, os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('PG_DB_NAME', 'cbp_db'),
        user=os.environ.get('PG_DB_USER', 'cbp_user'),
        password=os.environ.get('PG_DB_PASSWORD', 'cbp_pass'),
        host=os.environ.get('PG_DB_HOST', 'localhost'),
        port=os.environ.get('PG_DB_PORT', '5432'),
    )
    conn.close()
    print('PostgreSQL is ready.')
except Exception as e:
    print(f'PostgreSQL not ready: {e}')
    exit(1)
" 2>/dev/null; do
    echo "  ...PostgreSQL not yet available, retrying in 2s"
    sleep 2
done

# ---------------------------------------------------------------------------
# 3. Wait for Qdrant to be ready
# ---------------------------------------------------------------------------
echo "[3/7] Waiting for Qdrant at ${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}..."
until curl -sf "http://${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}/healthz" > /dev/null 2>&1; do
    echo "  ...Qdrant not yet available, retrying in 2s"
    sleep 2
done
echo "  Qdrant is ready."

# ---------------------------------------------------------------------------
# 4. Wait for Ollama to be ready
# ---------------------------------------------------------------------------
echo "[4/7] Waiting for Ollama at ${OLLAMA_BASE_URL:-http://localhost:11434}..."
OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
until curl -sf "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; do
    echo "  ...Ollama not yet available, retrying in 2s"
    sleep 2
done
echo "  Ollama is ready."

# ---------------------------------------------------------------------------
# 5. Run Django migrations
# ---------------------------------------------------------------------------
echo "[5/7] Running Django migrations..."
python manage.py migrate --noinput
echo "  Migrations complete."

# ---------------------------------------------------------------------------
# 6. Collect static files (optional, for admin)
# ---------------------------------------------------------------------------
echo "[6/7] Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# ---------------------------------------------------------------------------
# 7. Ingest data into Qdrant with local embeddings
# ---------------------------------------------------------------------------
echo "[7/7] Loading embedding models and ingesting CBP training data..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frds_project.settings')
django.setup()

print('  Loading local embedding models via FastEmbed...')
from chat.rag_service import ensure_collection, ingest_documents, get_dense_model, get_sparse_model

# Pre-load models
dense_model = get_dense_model()
sparse_model = get_sparse_model()

# Test embedding to get dimension
test_emb = list(dense_model.embed(['test']))[0]
print(f'  Dense model loaded (dim: {len(test_emb)})')
print(f'  Sparse model (BM25): {\"loaded\" if sparse_model else \"not available\"}')

from chat.mock_data import CBP_TRAINING_CONTENT
ensure_collection()
ingest_documents(CBP_TRAINING_CONTENT)
print(f'  Ingested {len(CBP_TRAINING_CONTENT)} CBP training documents.')
"

echo "=========================================="
echo " Starting Daphne (ASGI) on 0.0.0.0:8001"
echo " Local embeddings + WebSocket streaming"
echo "=========================================="

exec daphne \
    -b 0.0.0.0 \
    -p 8001 \
    --access-log - \
    frds_project.asgi:application
