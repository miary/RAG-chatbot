#!/bin/bash
set -e

echo "=========================================="
echo " FRDS — Backend Startup"
echo "=========================================="

# ---------------------------------------------------------------------------
# 1. Verify local models are available
# ---------------------------------------------------------------------------
echo "[1/6] Checking local embedding models..."
if [ -d "${MODELS_DIR:-/app/models}/dense" ] && [ -d "${MODELS_DIR:-/app/models}/sparse" ]; then
    echo "  Dense model:  ${MODELS_DIR:-/app/models}/dense"
    echo "  Sparse model: ${MODELS_DIR:-/app/models}/sparse"
else
    echo "  WARNING: Local models not found at ${MODELS_DIR:-/app/models}"
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
        dbname=os.environ.get('PG_DB_NAME', 'frds_db'),
        user=os.environ.get('PG_DB_USER', 'frds_user'),
        password=os.environ.get('PG_DB_PASSWORD', 'frds_pass'),
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
echo "[3/6] Waiting for Qdrant at ${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}..."
until curl -sf "http://${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}/healthz" > /dev/null 2>&1; do
    echo "  ...Qdrant not yet available, retrying in 2s"
    sleep 2
done
echo "  Qdrant is ready."

# ---------------------------------------------------------------------------
# 4. Run Django migrations
# ---------------------------------------------------------------------------
echo "[4/6] Running Django migrations..."
python manage.py migrate --noinput
echo "  Migrations complete."

# ---------------------------------------------------------------------------
# 5. Collect static files (optional, for admin)
# ---------------------------------------------------------------------------
echo "[5/6] Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# ---------------------------------------------------------------------------
# 6. Ingest data into Qdrant with local embeddings
# ---------------------------------------------------------------------------
echo "[6/6] Loading embedding models and ingesting FRDS data..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frds_project.settings')
django.setup()

print('  Loading local embedding models...')
from chat.rag_service import ensure_collection, ingest_documents, get_dense_model, get_sparse_model

# Pre-load models
dense_model = get_dense_model()
sparse_model = get_sparse_model()
print(f'  Dense model loaded (dim: {dense_model.get_sentence_embedding_dimension()})')
print(f'  Sparse model (SPLADE): {\"loaded\" if sparse_model else \"not available\"}')

from chat.mock_data import FRDS_INCIDENTS
ensure_collection()
ingest_documents(FRDS_INCIDENTS)
print(f'  Ingested {len(FRDS_INCIDENTS)} documents with hybrid embeddings.')
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
