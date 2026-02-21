# =============================================================================
# PSPD Guardian — Makefile
# =============================================================================

.PHONY: help build up down logs restart clean status ingest

COMPOSE := docker compose

help: ## Show this help message
	@echo ""
	@echo "  PSPD Guardian — Docker Commands"
	@echo "  ================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start all services (detached)
	$(COMPOSE) up -d

up-logs: ## Start all services and follow logs
	$(COMPOSE) up

down: ## Stop all services
	$(COMPOSE) down

down-clean: ## Stop all services and remove volumes (DELETES DATA)
	$(COMPOSE) down -v

restart: ## Restart all services
	$(COMPOSE) restart

restart-backend: ## Restart only the backend
	$(COMPOSE) restart backend

logs: ## Follow all service logs
	$(COMPOSE) logs -f

logs-backend: ## Follow backend logs
	$(COMPOSE) logs -f backend

logs-frontend: ## Follow frontend logs
	$(COMPOSE) logs -f frontend

status: ## Show status of all services
	$(COMPOSE) ps

health: ## Check health of all services
	@echo "--- PostgreSQL ---"
	@$(COMPOSE) exec postgres pg_isready -U guardian_user || echo "DOWN"
	@echo "--- Qdrant ---"
	@curl -sf http://localhost:6333/healthz && echo " OK" || echo "DOWN"
	@echo "--- Backend API ---"
	@curl -sf http://localhost:8001/api/ && echo "" || echo "DOWN"
	@echo "--- Backend Services ---"
	@curl -sf http://localhost:8001/api/status/ || echo "DOWN"
	@echo "--- Frontend ---"
	@curl -sf http://localhost:3000/ > /dev/null && echo "OK" || echo "DOWN"
	@echo "--- Proxy ---"
	@curl -sf http://localhost:8080/ > /dev/null && echo "OK" || echo "DOWN"

ingest: ## Re-ingest Guardian incident data into Qdrant
	curl -X POST http://localhost:8001/api/ingest/

shell-backend: ## Open a shell in the backend container
	$(COMPOSE) exec backend bash

shell-db: ## Open psql in the PostgreSQL container
	$(COMPOSE) exec postgres psql -U guardian_user -d guardian_db

migrate: ## Run Django migrations
	$(COMPOSE) exec backend python manage.py migrate
