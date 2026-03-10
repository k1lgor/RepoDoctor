# Justfile for RepoDoctor development

# Default task: list all recipes
default:
    @just --list

# Install dependencies
install:
    uv pip install -e ".[dev]"

# Format code
format:
    uv run ruff format src/ tests/

# Lint code
lint:
    uv run ruff check src/ tests/
    uv run ty check src/

# Run all tests
test:
    uv run pytest

# Run tests with coverage
coverage:
    uv run pytest --cov=src/repodoc --cov-report=html

# Build the package
build:
    uv build

# Clean up temporary files
clean:
    rm -rf .pytest_cache .ruff_cache htmlcov dist .repodoc
    find . -type d -name "__pycache__" -exec rm -rf {} +

# Run a self-scan
scan:
    uv run repodoc scan
