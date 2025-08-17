.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --doctest-modules

.PHONY: run
run: ## Run the FastAPI development server
	@echo "🚀 Starting FastAPI server"
	@uv run python -m src.simpei.main

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "🚀 Building Docker image"
	@docker build -t simpei-api .

.PHONY: docker-run
docker-run: ## Run the application in Docker with volume mounting
	@echo "🚀 Starting FastAPI server in Docker"
	@mkdir -p ./data
	@docker run -p 8000:8000 -v $(PWD)/data:/app/data simpei-api

.PHONY: docker-compose-up
docker-compose-up: ## Start the application using docker-compose
	@echo "🚀 Starting services with docker-compose"
	@mkdir -p ./data
	@docker-compose up --build

.PHONY: docker-compose-down
docker-compose-down: ## Stop docker-compose services
	@echo "🛑 Stopping docker-compose services"
	@docker-compose down

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
