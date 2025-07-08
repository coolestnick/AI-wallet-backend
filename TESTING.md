# Salt Wallet Backend Testing Guide

This guide provides comprehensive instructions for testing the Salt Wallet backend, including API endpoints, AI agents, and integrated services.

## Quick Start

### 1. Environment Setup
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Set up environment variables (optional for unit tests)
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Tests
```bash
# Run all fast tests (recommended for development)
python test_runner.py fast

# Run specific test categories
python test_runner.py unit           # Unit tests only
python test_runner.py api            # API endpoint tests
python test_runner.py agents         # AI agent tests

# Run with coverage
python test_runner.py coverage
```

## Test Categories

### 🚀 **Unit Tests** (`python test_runner.py unit`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 30 seconds)
- **Requirements**: No API keys required
- **Coverage**: Core logic, data models, utility functions

### 🌐 **Integration Tests** (`python test_runner.py integration`)
- **Purpose**: Test external API integrations
- **Speed**: Moderate (1-3 minutes)
- **Requirements**: API keys and internet connection
- **Coverage**: Real API calls to DexScreener, DefiLlama, GeckoTerminal, CoinGecko

### 🔗 **API Tests** (`python test_runner.py api`)
- **Purpose**: Test REST API endpoints
- **Speed**: Fast (< 1 minute)
- **Requirements**: No API keys required (uses mocking)
- **Coverage**: All `/api/v1/crypto/*` endpoints

### 🤖 **Agent Tests** (`python test_runner.py agents`)
- **Purpose**: Test AI agent functionality
- **Speed**: Moderate (1-2 minutes)
- **Requirements**: GEMINI_API_KEY for full testing
- **Coverage**: Crypto Advisor Agent, response generation, data integration

### ⚡ **Performance Tests** (`python test_runner.py performance`)
- **Purpose**: Test response times and concurrent handling
- **Speed**: Moderate (2-5 minutes)
- **Requirements**: No API keys required
- **Coverage**: Response times, concurrent requests, load handling

## Test Structure

```
tests/
├── conftest.py                      # Test configuration and fixtures
├── test_api.py                      # Legacy API tests
├── test_agents.py                   # Legacy agent tests
├── test_crypto_data_api.py          # New crypto data API tests
├── test_crypto_advisor_enhanced.py  # Enhanced agent tests
├── test_unified_crypto_api.py       # Unified API service tests
├── test_agent_service.py            # Agent service tests
├── test_agents_api.py               # Agent API tests
└── test_models.py                   # Data model tests
```

## Available Commands

### Using Test Runner (Recommended)
```bash
# Environment and health checks
python test_runner.py health         # Quick health check
python test_runner.py info           # Show test information

# Test execution
python test_runner.py fast           # Fast tests only (recommended for development)
python test_runner.py all            # Complete test suite
python test_runner.py unit           # Unit tests only
python test_runner.py integration    # Integration tests only
python test_runner.py api            # API endpoint tests
python test_runner.py agents         # Agent functionality tests
python test_runner.py performance    # Performance tests

# Coverage and reporting
python test_runner.py coverage       # Tests with coverage report

# Specific tests
python test_runner.py specific tests/test_crypto_data_api.py
python test_runner.py specific tests/test_crypto_data_api.py::TestCryptoDataAPI::test_health_check
```

### Using pytest Directly
```bash
# Basic test execution
pytest tests/                        # Run all tests
pytest tests/test_crypto_data_api.py # Run specific test file
pytest -v                           # Verbose output
pytest -k "test_health"              # Run tests matching pattern

# Test markers
pytest -m "api"                      # Run API tests only
pytest -m "agents"                   # Run agent tests only
pytest -m "integration"              # Run integration tests only
pytest -m "not integration"          # Skip integration tests

# Coverage reporting
pytest --cov=app --cov=agents --cov-report=html

# Parallel execution (if pytest-xdist is installed)
pytest -n auto                      # Run tests in parallel
```

## Environment Configuration

### Required Environment Variables
```bash
# AI/ML Services (Required for agent integration tests)
GEMINI_API_KEY=your_gemini_api_key_here

# External APIs (Optional - tests will be skipped if not provided)
COINGECKO_API_KEY=your-coingecko-api-key
DEXSCREENER_API_KEY=your-dexscreener-api-key  # Usually not required
DEFILLAMA_API_KEY=your-defillama-api-key      # Usually not required
GECKOTERMINAL_API_KEY=your-geckoterminal-api-key
```

### Test Environment Setup
```bash
# Create test environment file
cp .env.example .env.test

# Set test-specific configurations
export ENVIRONMENT=test
export LOG_LEVEL=DEBUG
```

## Test Scenarios

### 🧪 **Development Workflow**
```bash
# 1. Quick development check
python test_runner.py fast

# 2. Test specific component you're working on
python test_runner.py specific tests/test_crypto_data_api.py

# 3. Run full test suite before committing
python test_runner.py all
```

### 🚀 **Pre-Deployment Testing**
```bash
# 1. Full test suite with coverage
python test_runner.py coverage

# 2. Integration tests with real APIs
python test_runner.py integration

# 3. Performance validation
python test_runner.py performance
```

### 🔍 **Debugging Failed Tests**
```bash
# Run with verbose output and stop on first failure
pytest -v -x tests/test_crypto_data_api.py

# Run specific failing test with detailed output
pytest -v -s tests/test_crypto_data_api.py::TestCryptoDataAPI::test_search_tokens_success

# Run with Python debugger
pytest --pdb tests/test_crypto_data_api.py
```

## API Testing Examples

### Manual API Testing
```bash
# Start the server
uvicorn app.main:app --reload

# Test endpoints with curl
curl "http://localhost:8000/api/v1/crypto/health"
curl "http://localhost:8000/api/v1/crypto/search?query=bitcoin"
curl "http://localhost:8000/api/v1/crypto/market/overview"
curl "http://localhost:8000/api/v1/crypto/status"
```

### Using Python requests
```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/crypto/health")
print(response.json())

# Search tokens
response = requests.get("http://localhost:8000/api/v1/crypto/search", 
                       params={"query": "ethereum"})
print(response.json())

# Get market overview
response = requests.get("http://localhost:8000/api/v1/crypto/market/overview")
print(response.json())
```

## Testing Best Practices

### ✅ **Do's**
- Run `python test_runner.py fast` frequently during development
- Use mocking for external API calls in unit tests
- Test both success and error scenarios
- Include edge cases and boundary conditions
- Use descriptive test names
- Keep tests isolated and independent

### ❌ **Don'ts**
- Don't rely on external APIs for unit tests
- Don't hardcode API keys in test files
- Don't make tests dependent on specific API responses
- Don't skip error handling tests
- Don't commit test databases or temporary files

## Continuous Integration

### GitHub Actions Example
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: python test_runner.py fast
      - name: Run coverage
        run: python test_runner.py coverage
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Add project root to Python path
export PYTHONPATH="/path/to/salt_wallet/salt_backend:$PYTHONPATH"
```

#### 2. Missing Dependencies
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Install all dependencies
pip install -r requirements.txt
```

#### 3. API Key Issues
```bash
# Check if API keys are loaded
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# Skip integration tests if no API keys
python test_runner.py unit
```

#### 4. Port Conflicts
```bash
# Change test port if 8000 is in use
export TEST_PORT=8001
```

### Getting Help

1. **Check test output**: Look for specific error messages in test output
2. **Run health check**: `python test_runner.py health`
3. **Check environment**: `python test_runner.py info`
4. **Run single test**: Isolate the failing test and run it individually
5. **Check logs**: Look at application logs for additional context

## Performance Benchmarks

### Expected Performance
- **Unit tests**: < 30 seconds
- **API tests**: < 1 minute
- **Agent tests**: < 2 minutes (with API keys)
- **Integration tests**: < 3 minutes (with internet)
- **Full suite**: < 5 minutes

### Performance Monitoring
```bash
# Time test execution
time python test_runner.py fast

# Profile test performance
pytest --profile tests/

# Monitor concurrent performance
python test_runner.py performance
```

## Test Coverage Goals

- **Overall coverage**: > 80%
- **API endpoints**: > 95%
- **Core services**: > 90%
- **Agent functionality**: > 85%
- **Error handling**: > 90%

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add appropriate test markers (`@pytest.mark.api`, etc.)
4. Update this documentation if needed
5. Run full test suite before submitting PR

```bash
# Pre-commit checklist
python test_runner.py fast      # Quick check
python test_runner.py coverage  # Coverage report
python test_runner.py all       # Full validation
```