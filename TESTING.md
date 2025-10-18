# FLUX Testing Guide

Comprehensive testing documentation for the FLUX orbital research system.

---

## 📊 **Test Overview**

FLUX includes **105+ comprehensive tests** covering all aspects of the system:

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| **Bedrock Client** | 20+ | LLM integration, streaming, error handling |
| **Search Tools** | 30+ | Multi-source search, parsing, failures |
| **Storage** | 25+ | Cross-platform file operations |
| **Agents** | 30+ | All 6 agents, message formatting |
| **Orbital Flow** | 13+ | Iteration logic, quality tracking |

---

## 🚀 **Running Tests**

All testing commands work identically on **Windows, Mac, and Linux**.

### **Quick Start**

```bash
# From project root
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=flux_core --cov-report=html
```

### **Specific Test Suites**

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_agents.py -v

# Specific test class
pytest tests/unit/test_agents.py::TestFlowMasterAgent -v

# Specific test method
pytest tests/unit/test_agents.py::TestFlowMasterAgent::test_initialization -v
```

### **Test Markers**

Tests are organized with markers for filtering:

```bash
# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Skip tests requiring AWS credentials
pytest -m "not requires_aws"
```

---

## 📁 **Test Structure**

```
backend/tests/
├── conftest.py                    # Fixtures and configuration
├── unit/
│   ├── test_bedrock_client.py    # AWS Bedrock client tests
│   ├── test_search_tools.py      # Multi-source search tests
│   ├── test_cross_platform.py    # Platform compatibility tests
│   └── test_agents.py            # All 6 agents tests
└── integration/
    └── test_orbital_flow.py      # Orbital iteration tests
```

---

## 🔧 **Test Configuration**

### **pytest.ini**

The test configuration in `backend/pytest.ini`:

```ini
[tool:pytest]
# Test discovery
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Asyncio support
asyncio_mode = auto

# Markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    requires_aws: marks tests requiring AWS credentials
    requires_api_keys: marks tests requiring API keys

# Coverage
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=flux_core
    --cov-report=term-missing
    --cov-report=html
    --cov-branch
```

### **conftest.py**

Provides reusable fixtures for all tests:

```python
# Test configuration
test_config = {
    "max_iterations": 3,
    "quality_threshold": 8.0,
    "improvement_threshold": 0.5,
    "mock_llm": True,
}

# Sample research state
sample_state = create_initial_state(...)

# Mock search results
mock_search_results = [...]

# Mock Bedrock client
mock_bedrock_client = Mock(...)

# Mock quality scores
mock_quality_scores = {
    "low_quality": [3.0, 4.0, 4.5],
    "improving": [5.0, 6.5, 8.0],
    "high_quality": [8.5, 9.0, 9.2],
    "plateau": [6.0, 6.2, 6.3],
}
```

---

## 🧪 **Test Categories**

### **1. Bedrock Client Tests**

**File:** `tests/unit/test_bedrock_client.py`

Tests AWS Bedrock integration:
- ✅ Client initialization
- ✅ Model invocation
- ✅ Streaming responses
- ✅ Error handling (ClientError, BotoCoreError)
- ✅ JSON parsing errors
- ✅ Conversation history tracking

**Example:**
```bash
pytest tests/unit/test_bedrock_client.py::TestBedrockClientInvoke -v
```

### **2. Search Tools Tests**

**File:** `tests/unit/test_search_tools.py`

Tests multi-source research search:
- ✅ Semantic Scholar search
- ✅ ArXiv search
- ✅ Tavily search
- ✅ Multi-source combination
- ✅ Graceful degradation
- ✅ Error handling

**Example:**
```bash
pytest tests/unit/test_search_tools.py::TestSemanticScholarSearch -v
```

### **3. Cross-Platform Tests**

**File:** `tests/unit/test_cross_platform.py`

Tests platform compatibility:
- ✅ Pathlib operations
- ✅ File read/write (text, binary, JSON)
- ✅ Async file operations (aiofiles)
- ✅ Environment variables
- ✅ Storage module
- ✅ Platform-specific tests (auto-skip on other platforms)

**Example:**
```bash
# Run all cross-platform tests
pytest tests/unit/test_cross_platform.py -v

# Run only macOS-specific tests (auto-skips on Windows/Linux)
pytest tests/unit/test_cross_platform.py::TestMacOSSpecific -v
```

### **4. Agent Tests**

**File:** `tests/unit/test_agents.py`

Tests all 6 agents:
- ✅ BaseAgent initialization and methods
- ✅ Flow Master routing logic
- ✅ Current hypothesis generation
- ✅ Source research search
- ✅ Channel experiment design
- ✅ Filter quality scoring and issue extraction
- ✅ Confluence paper writing

**Example:**
```bash
# Test specific agent
pytest tests/unit/test_agents.py::TestFilterAgent -v

# Test quality score extraction
pytest tests/unit/test_agents.py::TestFilterAgent::test_calculate_quality_score -v
```

### **5. Orbital Flow Tests**

**File:** `tests/integration/test_orbital_flow.py`

Tests complete research workflow:
- ✅ Single orbit when quality met
- ✅ Multiple orbits when quality low
- ✅ Stops at max iterations
- ✅ Stops on diminishing returns
- ✅ Quality increases each orbit
- ✅ State evolution (iteration, history)
- ✅ Component integration

**Example:**
```bash
# Run all orbital flow tests
pytest tests/integration/test_orbital_flow.py -v

# Test specific scenario
pytest tests/integration/test_orbital_flow.py::TestOrbitalIterationBehavior::test_single_orbit_when_quality_met -v
```

---

## 📈 **Coverage Reports**

### **Generate Coverage Report**

```bash
# Terminal report
pytest --cov=flux_core --cov-report=term-missing

# HTML report
pytest --cov=flux_core --cov-report=html

# Both
pytest --cov=flux_core --cov-report=term-missing --cov-report=html
```

The HTML report is generated in `htmlcov/index.html`.

### **Coverage Configuration**

Coverage settings in `pytest.ini`:

```ini
[coverage:run]
source = flux_core
omit =
    */tests/*
    */__pycache__/*
    */venv/*
    */env/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

---

## 🎯 **Writing Tests**

### **Test Structure**

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestMyComponent:
    """Tests for MyComponent."""
    
    def test_synchronous_method(self):
        """Test synchronous method."""
        result = my_function(input)
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async method."""
        result = await my_async_function(input)
        assert result == expected
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes a while."""
        # Test long-running operation
        pass
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires AWS credentials")
    async def test_real_api(self):
        """Test with real API (skipped by default)."""
        # Test with actual API calls
        pass
```

### **Using Fixtures**

```python
def test_with_fixture(sample_state, mock_bedrock_client):
    """Test using predefined fixtures."""
    # sample_state and mock_bedrock_client are automatically injected
    assert sample_state["question"]
    assert mock_bedrock_client.invoke
```

### **Mocking**

```python
# Mock Bedrock client
with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
    mock_client = Mock()
    mock_client.invoke.return_value = "Mocked response"
    mock_client_class.return_value = mock_client
    
    # Your test code here
    agent = CurrentAgent()
    response = await agent.invoke_model("prompt")
    assert response == "Mocked response"

# Mock search function
with patch("flux_core.agents.source.multi_source_search") as mock_search:
    mock_search.return_value = [{"title": "Test Paper"}]
    
    # Your test code here
    results = await source_agent.search_research("query")
    assert len(results["sources"]) == 1
```

---

## 🐛 **Debugging Tests**

### **Verbose Output**

```bash
# Show print statements
pytest -v -s

# Show full tracebacks
pytest -v --tb=long

# Stop at first failure
pytest -v -x

# Run last failed tests
pytest --lf
```

### **Run Specific Test**

```bash
# By name pattern
pytest -k "test_quality"

# By marker
pytest -m "unit and not slow"

# Specific line
pytest tests/unit/test_agents.py::123
```

### **Debug Mode**

```python
# Add breakpoint in test
def test_something():
    result = my_function()
    breakpoint()  # Debugger will stop here
    assert result == expected
```

Run with:
```bash
pytest --pdb  # Drop into debugger on failure
```

---

## 🌐 **Platform-Specific Tests**

Some tests are platform-specific and auto-skip on other platforms:

```python
import sys
import pytest

@pytest.mark.skipif(sys.platform != "darwin", reason="macOS-specific test")
class TestMacOSSpecific:
    """Tests that only run on macOS."""
    
    def test_macos_feature(self):
        # This test only runs on macOS
        pass

@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
class TestWindowsSpecific:
    """Tests that only run on Windows."""
    
    def test_windows_feature(self):
        # This test only runs on Windows
        pass
```

Run platform-specific tests:
```bash
# Will auto-skip on incompatible platforms
pytest tests/unit/test_cross_platform.py::TestMacOSSpecific -v
pytest tests/unit/test_cross_platform.py::TestWindowsSpecific -v
```

---

## ✅ **Test Best Practices**

1. **Always mock external services** - No real API calls in unit tests
2. **Use fixtures** - Reuse common test data and setup
3. **Test async code** - Use `@pytest.mark.asyncio`
4. **Mark slow tests** - Use `@pytest.mark.slow`
5. **Test error cases** - Don't just test happy path
6. **Keep tests independent** - Tests shouldn't depend on each other
7. **Use descriptive names** - Test names should describe what they test
8. **Add docstrings** - Explain what the test verifies

---

## 📊 **Test Metrics**

Current FLUX test coverage:

- **Total Tests:** 105+
- **Unit Tests:** 85+
- **Integration Tests:** 13+
- **Code Coverage:** High (>80% of core modules)
- **All Tests:** ✅ Passing
- **Platforms Tested:** Windows, Mac, Linux

---

## 🔗 **Resources**

- **Pytest Documentation:** https://docs.pytest.org/
- **Pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **Mock Library:** https://docs.python.org/3/library/unittest.mock.html
- **Coverage.py:** https://coverage.readthedocs.io/

---

## 🎓 **Quick Reference**

```bash
# Common commands (work on all platforms)
pytest                              # Run all tests
pytest -v                           # Verbose
pytest -v -s                        # Show print statements
pytest -k "pattern"                 # Run tests matching pattern
pytest -m "marker"                  # Run tests with marker
pytest --cov                        # With coverage
pytest --cov --cov-report=html      # Coverage HTML report
pytest -x                           # Stop at first failure
pytest --lf                         # Run last failed
pytest tests/unit/ -v               # Unit tests only
pytest tests/integration/ -v        # Integration tests only
pytest -m "not slow"                # Skip slow tests
```

---

**Happy Testing!** 🧪✨

All tests are designed to run on Windows, Mac, and Linux without modification.

