# Default recipe to display available commands
default:
    @just --list

# Install dependencies and package in development mode
install:
    poetry install

# Setup test environment
setup-tests:
    mkdir -p tests/fixtures
    poetry run python tests/setup_test_env.py

# Run tests with coverage
test: install setup-tests
    poetry run pytest --cov=audiokit --cov-report=term-missing

# Format code
format:
    poetry run black .
    poetry run isort .

# Run linting
lint:
    poetry run ruff check .

# Add a new dependency
add dep:
    poetry add {{dep}}

# Add a new development dependency
add-dev dep:
    poetry add --group dev {{dep}} 