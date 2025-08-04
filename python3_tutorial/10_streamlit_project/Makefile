# Makefile for Streamlit Dashboard

.PHONY: help install run dev test clean docker-up docker-down deploy

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run Streamlit app
	streamlit run dashboard/app.py

dev: ## Run in development mode with auto-reload
	streamlit run dashboard/app.py --server.runOnSave true

test: ## Run tests
	pytest tests/ -v

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf dashboard/.cache
	rm -rf dashboard/data/*.json

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-build: ## Build Docker image
	docker build -t streamlit-dashboard .

docker-run: ## Run Docker container
	docker run -p 8501:8501 streamlit-dashboard

deploy-cloud: ## Deploy to Streamlit Cloud
	@echo "Deploying to Streamlit Cloud..."
	@echo "1. Push code to GitHub"
	@echo "2. Go to share.streamlit.io"
	@echo "3. Connect your repository"
	@echo "4. Deploy!"

cache-clear: ## Clear Streamlit cache
	streamlit cache clear