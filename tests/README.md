# BA-QA Platform Tests

Comprehensive test suite for the BA-QA Intelligence Platform.

## 🧪 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (fast, isolated)
│   └── test_document_repository.py
├── integration/             # Integration tests (with dependencies)
└── fixtures/                # Test data and factories
```

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Run all tests with coverage
PYTHONPATH=. pytest

# Run unit tests only
PYTHONPATH=. pytest tests/unit/

# Run with verbose output
PYTHONPATH=. pytest -v

# Run without coverage (faster)
PYTHONPATH=. pytest --no-cov
```

### Run Specific Tests

```bash
# Run specific file
PYTHONPATH=. pytest tests/unit/test_document_repository.py

# Run specific test class
PYTHONPATH=. pytest tests/unit/test_document_repository.py::TestProjectOperations

# Run specific test
PYTHONPATH=. pytest tests/unit/test_document_repository.py::TestProjectOperations::test_create_project
```

## 📊 Coverage Reports

```bash
# Generate coverage report
PYTHONPATH=. pytest --cov=data --cov=agents --cov=pipeline

# Generate HTML coverage report
PYTHONPATH=. pytest --cov=data --cov-report=html

# Open HTML report
open htmlcov/index.html
```

## 🏷️ Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
PYTHONPATH=. pytest -m unit

# Run only integration tests
PYTHONPATH=. pytest -m integration

# Run only database tests
PYTHONPATH=. pytest -m db

# Run only API tests
PYTHONPATH=. pytest -m api

# Skip slow tests
PYTHONPATH=. pytest -m "not slow"
```

## ✅ Current Test Status

### Document Repository (Phase 1)
- ✅ **17 tests** covering:
  - Project CRUD operations (6 tests)
  - Document CRUD operations (6 tests)
  - Version management (3 tests)
  - Statistics (2 tests)
- ✅ **50% coverage** on `data/database.py`

### AI Client (Phase 2)
- ✅ **22 tests** covering:
  - Anthropic API calls (7 tests)
  - Gemini API calls (5 tests)
  - API key rotation (6 tests)
  - Unified AI interface (4 tests)
- ✅ **87% coverage** on `agents/ai_client.py`

### Prompt Templates (Phase 3)
- ✅ **18 tests** covering:
  - BA evaluation prompts (5 tests)
  - TC evaluation prompts (4 tests)
  - JSON parsing (2 tests)
  - Prompt formatting (4 tests)
  - Prompt consistency (3 tests)
- ✅ Validates prompt structure and content

### JSON Repair (Phase 4)
- ✅ **26 tests** covering:
  - AI JSON parsing strategies (9 tests)
  - Edge cases (9 tests)
  - Repair strategies (4 tests)
  - Real-world scenarios (4 tests)
- ✅ Validates JSON repair and recovery

### Total
- ✅ **83 unit tests** passing
- ✅ **35% overall coverage** (improving)

## 📝 Writing Tests

### Test Organization

- **Unit tests**: Fast, isolated tests with mocked dependencies
- **Integration tests**: Tests that use real database, APIs, etc.
- Use fixtures from `conftest.py` for common test data
- Follow the Arrange-Act-Assert pattern

### Example Test

```python
import pytest

@pytest.mark.unit
@pytest.mark.db
def test_create_project(db_connection, sample_project):
    """Test creating a new project."""
    from data.database import create_project

    # Arrange
    name = sample_project["name"]

    # Act
    project_id = create_project(**sample_project)

    # Assert
    assert project_id > 0
```

### Available Fixtures

- `temp_db`: Temporary database file
- `db_connection`: Database connection with schema
- `clean_db`: Clean database for each test
- `sample_project`: Sample project data
- `sample_ba_document`: Sample BA document
- `sample_tc_document`: Sample TC document
- `mock_anthropic_response`: Mocked Anthropic API response
- `mock_gemini_response`: Mocked Gemini API response

## 🎯 Next Steps

### Planned Test Coverage

1. **Phase 1 (Current)**: Document Repository ✅
2. **Phase 2**: AI Client & Prompt Testing
3. **Phase 3**: BRD Pipeline Testing
4. **Phase 4**: UI/Streamlit Testing
5. **Phase 5**: Integration Tests

### Areas to Test

- [ ] `agents/ai_client.py` - AI model calls
- [ ] `agents/prompts.py` - Prompt templates
- [ ] `pipeline/brd/orchestrator.py` - BRD pipeline
- [ ] `pipeline/brd/json_repair.py` - JSON parsing
- [ ] UI pages with Playwright/Selenium

## 🔧 Configuration

Tests are configured in `pytest.ini`. Key settings:

- Test discovery patterns
- Coverage configuration
- Marker definitions
- Logging settings

## 💡 Tips

1. **Use markers**: Organize tests with `@pytest.mark.unit`, `@pytest.mark.integration`
2. **Use fixtures**: Reuse common test data and setup
3. **Keep tests isolated**: Each test should be independent
4. **Mock external dependencies**: Use `pytest-mock` for API calls
5. **Check coverage**: Aim for >80% coverage on critical modules

## 🐛 Debugging Tests

```bash
# Run with debugging
PYTHONPATH=. pytest --pdb

# Stop on first failure
PYTHONPATH=. pytest -x

# Show local variables on failure
PYTHONPATH=. pytest -l

# Verbose output with print statements
PYTHONPATH=. pytest -v -s
```

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
