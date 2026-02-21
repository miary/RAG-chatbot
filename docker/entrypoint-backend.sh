#!/bin/bash
set -e

echo "=========================================="
echo " PSPD Guardian — Backend Startup"
echo "=========================================="

# ---------------------------------------------------------------------------
# 1. Wait for PostgreSQL to be ready
# ---------------------------------------------------------------------------
echo "[1/5] Waiting for PostgreSQL at ${PG_DB_HOST:-localhost}:${PG_DB_PORT:-5432}..."
until python -c "
import psycopg2, os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('PG_DB_NAME', 'guardian_db'),
        user=os.environ.get('PG_DB_USER', 'guardian_user'),
        password=os.environ.get('PG_DB_PASSWORD', 'guardian_pass'),
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
# 2. Wait for Qdrant to be ready
# ---------------------------------------------------------------------------
echo "[2/5] Waiting for Qdrant at ${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}..."
until curl -sf "http://${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}/healthz" > /dev/null 2>&1; do
    echo "  ...Qdrant not yet available, retrying in 2s"
    sleep 2
done
echo "  Qdrant is ready."

# ---------------------------------------------------------------------------
# 3. Run Django migrations
# ---------------------------------------------------------------------------
echo "[3/5] Running Django migrations..."
python manage.py migrate --noinput
echo "  Migrations complete."

# ---------------------------------------------------------------------------
# 4. Collect static files (optional, for admin)
# ---------------------------------------------------------------------------
echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# ---------------------------------------------------------------------------
# 5. Ingest mock data into Qdrant (idempotent — upsert)
# ---------------------------------------------------------------------------
echo "[5/5] Ingesting Guardian incident data into Qdrant..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guardian_project.settings')
django.setup()
from chat.rag_service import ensure_collection, ingest_documents
from chat.mock_data import GUARDIAN_INCIDENTS
ensure_collection()
ingest_documents(GUARDIAN_INCIDENTS)
print(f'  Ingested {len(GUARDIAN_INCIDENTS)} documents.')
"

echo "=========================================="
echo " Starting Gunicorn on 0.0.0.0:8001"
echo "=========================================="

exec gunicorn guardian_project.wsgi:application \
    --bind 0.0.0.0:8001 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-300}" \
    --access-logfile - \
    --error-logfile - \
    --log-level info
