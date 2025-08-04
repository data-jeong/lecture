# Makefile for FastAPI Blog API

.PHONY: help install dev test lint format clean docker-up docker-down migrate

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn blog_api.app.main:app --reload --port 8000

test: ## Run tests
	pytest tests/ -v --cov=blog_api --cov-report=html

lint: ## Run linters
	flake8 blog_api/
	mypy blog_api/
	black --check blog_api/

format: ## Format code
	black blog_api/
	isort blog_api/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

seed: ## Seed database with sample data
	python -m blog_api.db.seed