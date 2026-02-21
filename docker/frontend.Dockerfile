# =============================================================================
# PSPD Guardian — Frontend Dockerfile
# Multi-stage: Node build → Nginx static serve
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — Build the React application
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY frontend/package.json frontend/yarn.lock* /app/

# Install dependencies
RUN yarn install --frozen-lockfile --network-timeout 120000 2>/dev/null || yarn install --network-timeout 120000

# Copy source files
COPY frontend/ /app/

# Build-time environment variable — will be overridden at runtime via nginx
# This placeholder gets replaced by the entrypoint at runtime
ENV REACT_APP_BACKEND_URL=__BACKEND_URL_PLACEHOLDER__

# Build the production bundle
RUN yarn build

# ---------------------------------------------------------------------------
# Stage 2 — Serve with Nginx
# ---------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY docker/nginx-frontend.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy entrypoint that handles runtime env injection
COPY docker/entrypoint-frontend.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
