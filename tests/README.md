# Testing Guide

## Overview

This project includes comprehensive test coverage across multiple areas:

1. **Additional Instructions** - Tests for the additional_instructions feature
2. **RAG Service** - Tests for protocol retrieval and similarity search
3. **API Endpoints** - Integration tests for FastAPI endpoints
4. **Export Formats** - Tests for ODM, FHIR, and CSV exports
5. **Basic Functionality** - Core protocol and CRF generation

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration
├── test_basic.py                    # Core functionality tests
├── test_additional_instructions.py  # Additional instructions feature
├── test_rag_service.py             # RAG database operations
├── test_api_endpoints.py           # API endpoint tests
└── test_export_formats.py          # Export format validation

examples/
├── test_rag.py                     # RAG examples
├── test_llm.py                     # LLM examples
├── test_api.py                     # API usage examples
└── ... (other example files)
```

## Running Tests

### Run All Tests

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test Files

```powershell
# Test additional instructions
pytest tests/test_additional_instructions.py -v

# Test RAG service
pytest tests/test_rag_service.py -v

# Test API endpoints
pytest tests/test_api_endpoints.py -v

# Test export formats
pytest tests/test_export_formats.py -v
```

### Run Specific Test Classes

```powershell
# Run specific test class
pytest tests/test_api_endpoints.py::TestAPIEndpoints -v

# Run specific test method
pytest tests/test_api_endpoints.py::TestAPIEndpoints::test_health_check -v
```

### Run with Custom Options

```powershell
# Run tests that require LLM API calls (expensive)
pytest tests/ -v --run-llm

# Run slow tests
pytest tests/ -v --run-slow

# Skip slow and LLM tests (default)
pytest tests/ -v

# Run only fast tests (exclude slow and LLM)
pytest tests/ -v -m "not slow and not llm"
```

### Run Tests in Parallel

```powershell
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -v -n 4
```

## Test Markers

### Custom Markers

- `@pytest.mark.llm` - Tests that require LLM API calls (OpenAI)
- `@pytest.mark.slow` - Tests that take a long time to run

### Using Markers

```python
import pytest

@pytest.mark.llm
def test_with_llm():
    """This test requires OpenAI API and will be skipped unless --run-llm is used."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """This test is slow and will be skipped unless --run-slow is used."""
    pass
```

## Test Coverage by Area

### 1. Additional Instructions (`test_additional_instructions.py`)

Tests the feature that allows custom instructions to influence protocol generation.

**Coverage:**
- ✅ Baseline generation without instructions
- ✅ Generation with custom instructions
- ✅ Instructions affecting specific sections (objectives, study design)
- ✅ Edge cases (empty, None, very long instructions)
- ✅ LLM integration tests (biomarker requirements)

**Run:**
```powershell
pytest tests/test_additional_instructions.py -v

# Include LLM tests
pytest tests/test_additional_instructions.py -v --run-llm
```

### 2. RAG Service (`test_rag_service.py`)

Tests the Retrieval-Augmented Generation database operations.

**Coverage:**
- ✅ Adding protocols to RAG database
- ✅ Retrieving similar protocols
- ✅ Getting protocols by ID
- ✅ Deleting protocols
- ✅ Search text creation

**Run:**
```powershell
pytest tests/test_rag_service.py -v
```

**Note:** These tests interact with the actual ChromaDB database at `./vector_db`. They clean up after themselves but will temporarily add/remove protocols.

### 3. API Endpoints (`test_api_endpoints.py`)

Tests all FastAPI REST endpoints.

**Coverage:**
- ✅ Health check endpoint
- ✅ Protocol generation endpoint
- ✅ Protocol generation with additional instructions
- ✅ CRF generation endpoint
- ✅ RAG seeding endpoint
- ✅ Export endpoint (ODM format)
- ✅ Input validation and error handling
- ✅ Edge cases (invalid data, missing fields)

**Run:**
```powershell
pytest tests/test_api_endpoints.py -v
```

### 4. Export Formats (`test_export_formats.py`)

Tests ODM XML, FHIR JSON, and CSV export functionality.

**Coverage:**
- ✅ ODM XML structure and validation
- ✅ FHIR JSON resource format
- ✅ CSV export with headers and data
- ✅ Minimal protocol export
- ✅ Special character handling

**Run:**
```powershell
pytest tests/test_export_formats.py -v
```

### 5. Basic Functionality (`test_basic.py`)

Tests core protocol and CRF generation.

**Coverage:**
- ✅ Trial specification validation
- ✅ Protocol generation
- ✅ CRF generation
- ✅ Validation rules

**Run:**
```powershell
pytest tests/test_basic.py -v
```

## Prerequisites

### Required Environment Variables

For tests that use LLM (with `--run-llm` flag):

```powershell
# Set OpenAI API key
$env:OPENAI_API_KEY = "sk-..."
```

### Required Dependencies

All test dependencies are in `requirements.txt`:

```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-xdist>=3.3.0  # For parallel testing
httpx>=0.24.0        # For TestClient
```

Install:
```powershell
pip install -r requirements.txt
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Writing New Tests

### Test File Template

```python
"""Tests for [feature name]."""
import pytest
from app.services.generator import ProtocolTemplateGenerator
from app.models.schemas import TrialSpecInput, TrialPhase, TrialEndpoint, EndpointType


class TestMyFeature:
    """Test suite for my feature."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ProtocolTemplateGenerator(use_llm=False, use_rag=False)
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        spec = TrialSpecInput(
            sponsor="Test Pharma",
            title="Test Study",
            indication="Test Disease",
            phase=TrialPhase.PHASE_2,
            design="randomized",
            sample_size=100,
            duration_weeks=12,
            key_endpoints=[
                TrialEndpoint(type=EndpointType.PRIMARY, name="Test Endpoint")
            ],
            inclusion_criteria=["Test criteria"],
            exclusion_criteria=["Test exclusion"],
            region="US"
        )
        
        result = self.generator.generate_structured_protocol(spec)
        
        assert result is not None
        # Add more assertions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Best Practices

1. **Use descriptive test names** - `test_generation_with_additional_instructions` not `test1`
2. **One assertion per test** - Keep tests focused
3. **Use fixtures** - Share setup code with `setup_method` or `@pytest.fixture`
4. **Clean up resources** - Use `teardown_method` to clean up test data
5. **Mark expensive tests** - Use `@pytest.mark.llm` for tests that cost money
6. **Test edge cases** - Empty strings, None values, very large inputs
7. **Use meaningful assertions** - Assert specific values, not just "not None"

## Debugging Tests

### Run with Verbose Output

```powershell
pytest tests/test_api_endpoints.py -v -s
```

The `-s` flag shows print statements.

### Run Specific Test with Debugger

```powershell
pytest tests/test_api_endpoints.py::TestAPIEndpoints::test_health_check -v --pdb
```

The `--pdb` flag drops into debugger on failure.

### VS Code Debugging

1. Set breakpoints in test files
2. Use "Python: Debug Test File" configuration
3. Or use "Python Debugger: Debug Tests in Current File" from Command Palette

## Troubleshooting

### Tests Fail Due to Missing API Key

**Error:** `openai.error.AuthenticationError`

**Solution:** Set `OPENAI_API_KEY` environment variable or skip LLM tests:
```powershell
pytest tests/ -v  # Skips LLM tests by default
```

### Tests Fail Due to Database Issues

**Error:** ChromaDB errors

**Solution:** Delete and recreate vector database:
```powershell
Remove-Item -Recurse -Force ./vector_db
# Database will be recreated on next run
```

### Tests Run Too Slowly

**Solution:** Run in parallel:
```powershell
pip install pytest-xdist
pytest tests/ -v -n 4  # 4 parallel workers
```

Or skip slow tests:
```powershell
pytest tests/ -v -m "not slow"
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Run pytest from project root:
```powershell
cd f:\CodeTests\AiPoc
pytest tests/ -v
```

## Test Coverage Reports

### Generate HTML Coverage Report

```powershell
pytest tests/ --cov=app --cov-report=html
```

Then open `htmlcov/index.html` in browser.

### Generate Terminal Coverage Report

```powershell
pytest tests/ --cov=app --cov-report=term-missing
```

Shows which lines are not covered.

### Coverage Goals

- **Overall Coverage:** Target 80%+
- **Critical Paths:** 100% (validation, data export)
- **UI/API:** 90%+
- **Utilities:** 70%+

## Summary

| Test File | Purpose | Test Count | Requires LLM | Run Time |
|-----------|---------|------------|--------------|----------|
| `test_basic.py` | Core functionality | 4 | No | Fast |
| `test_additional_instructions.py` | Additional instructions | 9 | Some | Fast/Med |
| `test_rag_service.py` | RAG operations | 6 | No | Medium |
| `test_api_endpoints.py` | API endpoints | 15+ | No | Fast |
| `test_export_formats.py` | Export formats | 15+ | No | Fast |

**Total:** 50+ tests covering all major functionality

**Quick Start:**
```powershell
# Run all fast tests (default)
pytest tests/ -v

# Run all tests including LLM (requires API key)
pytest tests/ -v --run-llm

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
```
