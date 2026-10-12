# ==============================================================================
# AWS ECS Blue/Green Pipeline - Enterprise Makefile Toolkit
# ==============================================================================

.PHONY: help install lint test scan docker-build docker-run tf-init tf-plan tf-fmt perf-test clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install application and development dependencies
	pip install -r app/requirements.txt pytest ruff bandit pip-audit

lint: ## Run Ruff linter and code formatter checks
	ruff check app/
	ruff format --check app/

test: ## Execute full pytest unit and contract test suite
	python -m pytest app/tests -v

scan: ## Run SAST security audits (Bandit) and dependency scans
	bandit -r app/ -x app/tests -ll
	pip-audit -r app/requirements.txt

docker-build: ## Build production Docker container image locally
	docker build -t cicd-demo-app:local app/

docker-run: ## Run local container on port 8080
	docker run -p 8080:8080 --rm cicd-demo-app:local

tf-init: ## Initialize Terraform working directory
	cd terraform && terraform init -backend=false

tf-plan: ## Run Terraform plan validation
	cd terraform && terraform plan

tf-fmt: ## Format all Terraform HCL files
	cd terraform && terraform fmt -recursive

perf-test: ## Run Locust performance load test (requires ALB_URL env var)
	locust -f tests/locustfile.py --headless -u 20 -r 5 --run-time 1m --host $${ALB_URL:-http://localhost:8080}

clean: ## Clean up local caches and bytecode files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
