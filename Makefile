# ============================================
# Fraud Detection Platform — Makefile
# ============================================

.PHONY: help up down build logs restart clean test lint seed

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------- Docker ----------

up: ## Start all services
	docker-compose up -d

up-build: ## Build and start all services
	docker-compose up -d --build

down: ## Stop all services
	docker-compose down

down-clean: ## Stop all services and remove volumes
	docker-compose down -v

build: ## Build all Docker images
	docker-compose build

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show API Gateway logs
	docker-compose logs -f api-gateway

logs-worker: ## Show Worker logs
	docker-compose logs -f worker

logs-mcp: ## Show MCP Server logs
	docker-compose logs -f mcp-server

restart: ## Restart all services
	docker-compose restart

ps: ## Show running services
	docker-compose ps

# ---------- Development ----------

dev-api: ## Run API Gateway locally
	cd services/api-gateway && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker: ## Run Worker locally
	cd services/worker && python -m app.main

dev-frontend: ## Run Frontend locally
	cd frontend && npm run dev

# ---------- Database ----------

migrate: ## Run database migrations
	cd services/api-gateway && alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="description")
	cd services/api-gateway && alembic revision --autogenerate -m "$(MSG)"

# ---------- Testing ----------

test: ## Run all tests
	cd services/api-gateway && pytest -v
	cd services/worker && pytest -v
	cd services/mcp-server && pytest -v

test-api: ## Run API Gateway tests
	cd services/api-gateway && pytest -v

test-worker: ## Run Worker tests
	cd services/worker && pytest -v

# ---------- Scripts ----------

seed: ## Seed database with sample data
	python scripts/seed-data.py

manual-input: ## Manual transaction input (usage: make manual-input USER=user_1 AMOUNT=500 LOCATION=Istanbul)
	./scripts/manual-input.sh $(USER) $(AMOUNT) $(LOCATION)

auto-test: ## Run auto test script (usage: make auto-test DURATION=60 RATE=10 ANOMALY=20)
	./scripts/auto-test.sh --duration=$(DURATION) --rate=$(RATE) --anomaly-chance=$(ANOMALY)

# ---------- Utilities ----------

clean: ## Remove all generated files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

lint: ## Run linters on all services
	cd services/api-gateway && ruff check app/
	cd services/worker && ruff check app/
	cd services/mcp-server && ruff check app/
