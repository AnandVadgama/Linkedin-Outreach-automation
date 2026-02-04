# LinkedIn Outreach Automation - Makefile
# Professional development workflow commands

.PHONY: help install install-dev setup clean test lint format check run-tests coverage

# Default target
help:
	@echo "LinkedIn Outreach Automation - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  setup          Complete project setup"
	@echo ""
	@echo "Development Commands:"
	@echo "  test           Run test suite"
	@echo "  coverage       Run tests with coverage report"
	@echo "  lint           Run code linting"
	@echo "  format         Format code with black and isort"
	@echo "  check          Run all code quality checks"
	@echo ""
	@echo "Database Commands:"
	@echo "  init-db        Initialize database"
	@echo "  test-data      Generate test data"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  clean          Remove temporary files"
	@echo "  clean-all      Remove all generated files"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .

setup: install-dev
	@echo "Setting up LinkedIn Outreach Automation..."
	cp .env.example .env
	@echo "✅ Environment file created (.env)"
	@echo "📝 Please edit .env with your LinkedIn credentials"
	python -m src.cli.main init-db
	@echo "✅ Project setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your LinkedIn credentials"
	@echo "2. Run: make test-data  (to generate sample data)"
	@echo "3. Run: python -m src.cli.main --help"

# Testing
test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

run-tests: test

# Code Quality
lint:
	python -m flake8 src/ tests/
	python -m black --check src/ tests/
	python -m isort --check-only src/ tests/

format:
	python -m black src/ tests/
	python -m isort src/ tests/
	@echo "✅ Code formatted successfully!"

check: lint test
	@echo "✅ All checks passed!"

# Database Commands
init-db:
	python -m src.cli.main init-db

test-data:
	python -m src.cli.main generate-test-data --count 25
	@echo "✅ Generated 25 test prospects!"

# CLI Shortcuts
search:
	python -m src.cli.main search-prospects --keywords "software engineer" --location "San Francisco" --limit 10 --save

stats:
	python -m src.cli.main stats

prospects:
	python -m src.cli.main list-prospects

config:
	python -m src.cli.main config

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -f .coverage
	rm -rf htmlcov/

clean-all: clean
	rm -rf data/
	rm -rf logs/
	rm -f *.db
	rm -f test.db
	@echo "✅ All generated files removed!"

# Development server simulation
demo:
	@echo "🚀 LinkedIn Outreach Automation Demo"
	@echo ""
	make test-data
	@echo ""
	make prospects
	@echo ""
	make stats
	@echo ""
	@echo "✅ Demo completed! Check the data above."

# Docker commands (future)
docker-build:
	@echo "🐳 Docker support coming in v0.2!"

docker-run:
	@echo "🐳 Docker support coming in v0.2!"

# Documentation (future) 
docs:
	@echo "📚 Documentation generation coming in v0.2!"

# Version information
version:
	@python -c "import src; print(f'LinkedIn Outreach Automation v{src.__version__}')"

# Pre-commit hooks setup
pre-commit:
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"