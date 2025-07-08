# Tests for AI-Enhanced Crypto Wallet Backend

## Overview
This directory contains tests for the AI-Enhanced Crypto Wallet Backend. The tests use pytest and are organized by component.

## Test Structure
- `test_portfolio_api.py`: Tests for the portfolio API endpoints
- `test_portfolio_service.py`: Tests for the portfolio service logic

## Running Tests
To run all tests, execute the following command from the project root:

```bash
python -m pytest tests/
```

To run a specific test file:

```bash
python -m pytest tests/test_portfolio_api.py
```

To run tests with coverage report:

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Test Data
The tests use mock data to avoid dependencies on external services. The mock data is defined in each test file.

## Adding New Tests
When adding new features to the backend, please add corresponding tests in this directory. Tests should be organized by component and should follow the naming convention `test_*.py`. 