#!/bin/sh
set -e

# ---------------------------------------------------------------------------
# Runtime environment variable injection
#
# React bakes env vars at BUILD time. To allow runtime configuration,
# we replace the build-time placeholder with the actual BACKEND_URL.
# ---------------------------------------------------------------------------
BACKEND_URL="${REACT_APP_BACKEND_URL:-http://localhost:8001}"

echo "PSPD Guardian Frontend — Injecting BACKEND_URL: ${BACKEND_URL}"

# Replace the placeholder in all JS bundles
find /usr/share/nginx/html/static/js -name '*.js' -exec \
    sed -i "s|__BACKEND_URL_PLACEHOLDER__|${BACKEND_URL}|g" {} +

echo "Environment injection complete. Starting Nginx..."

# Execute the CMD (nginx)
exec "$@"
