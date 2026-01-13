# Makefile for CLI utilities testing

.PHONY: help install test test-unit test-integration test-bats coverage clean benchmark benchmark-save benchmark-compare

help:
	@echo "Available commands:"
	@echo "  make install              - Install test dependencies"
	@echo "  make test                 - Run all tests"
	@echo "  make test-unit            - Run unit tests only"
	@echo "  make test-integration     - Run integration tests only"
	@echo "  make test-bats            - Run bash tests (requires bats-core)"
	@echo "  make coverage             - Run tests with coverage report"
	@echo "  make benchmark            - Run performance benchmarks"
	@echo "  make benchmark-save       - Run benchmarks and save baseline"
	@echo "  make benchmark-compare    - Run benchmarks and compare with baseline"
	@echo "  make clean                - Clean test artifacts"

install:
	pip install -r requirements-test.txt

test: test-unit test-integration

test-unit:
	pytest tests/unit -v --tb=short

test-integration:
	pytest tests/integration -v --tb=short

test-bats:
	@if command -v bats >/dev/null 2>&1; then \
		bats tests/bats/; \
	else \
		echo "Error: bats-core is not installed."; \
		echo "Install with: brew install bats-core (macOS) or apt-get install bats (Linux)"; \
		exit 1; \
	fi

coverage:
	pytest --cov=scripts --cov=bin --cov-report=term-missing --cov-report=html --cov-branch

benchmark:
	@echo "Running performance benchmarks..."
	pytest tests/benchmarks/ --benchmark-only -v

benchmark-save:
	@echo "Running benchmarks and saving baseline..."
	pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline --benchmark-autosave
	@echo "Baseline saved. Use 'make benchmark-compare' to compare future runs."

benchmark-compare:
	@echo "Running benchmarks and comparing with baseline..."
	pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%

clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .benchmarks/
	rm -rf **/__pycache__/
	rm -rf **/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
