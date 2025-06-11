# Trade Craft Development Makefile

.PHONY: help install test lint format run clean setup-dev

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  run         - Run the application"
	@echo "  clean       - Clean up temporary files"
	@echo "  setup-dev   - Set up development environment"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=utils --cov-report=html

lint:
	flake8 utils/ components/ pages/ app.py
	mypy utils/ --ignore-missing-imports

format:
	black utils/ components/ pages/ app.py
	isort utils/ components/ pages/ app.py

run:
	python app.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

setup-dev: install
	cp .env.example .env
	python utils/db_init.py
	python utils/sample_data.py
	@echo "Development environment set up successfully!"
	@echo "Run 'make run' to start the application"

# Database commands
init-db:
	python utils/db_init.py

sample-data:
	python utils/sample_data.py

# Docker commands (for future use)
docker-build:
	docker build -t tradecraft .

docker-run:
	docker run -p 8050:8050 tradecraft