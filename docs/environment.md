# Shadow AI Development Environment

This project uses a dedicated conda environment called `shadow-ai`.

## Quick Setup

1. **Activate the environment:**
   ```bash
   conda activate shadow-ai
   ```

2. **Verify installation:**
   ```bash
   pytest --version
   ruff --version
   mypy --version
   ```

## Development Dependencies Installed

- **FastAPI** (0.110.0+): Web framework for API endpoints
- **Uvicorn**: ASGI server for FastAPI
- **Click**: CLI framework for command-line interface
- **Pytest** (8.0.0+): Testing framework
- **Pytest-cov**: Test coverage reporting
- **Pytest-asyncio**: Async testing support
- **HTTPx**: HTTP client for testing API endpoints
- **Ruff**: Fast Python linter and formatter
- **Mypy**: Static type checker

## Environment Details

- **Python Version**: 3.11.13
- **Environment Type**: Conda
- **Environment Name**: shadow-ai
- **Location**: C:\Users\arunk\.conda\envs\shadow-ai

## Command Reference

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=shadow_ai --cov-report=html

# Check code quality
ruff check .
ruff format --check .

# Type checking
mypy shadow_ai/

# Install in development mode (if needed)
pip install -e .
```
