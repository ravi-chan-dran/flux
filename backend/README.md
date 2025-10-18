# FLUX Backend - Orbital Research Agent

FastAPI backend for the FLUX research system, powered by LangGraph and AWS Bedrock.

## Project Structure

```
backend/
├── flux_core/                 # Core package
│   ├── agents/               # Research agents
│   ├── graph/                # LangGraph state and workflow
│   │   └── state.py         # ResearchState TypedDict
│   ├── models/               # Pydantic models
│   └── tools/                # Tools and utilities
│       ├── bedrock_client.py # AWS Bedrock client
│       ├── search.py        # Multi-source search (Semantic Scholar, ArXiv, Tavily)
│       └── storage.py       # Async storage with pathlib
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   │   ├── test_bedrock_client.py
│   │   ├── test_search_tools.py
│   │   └── test_cross_platform.py
│   └── integration/          # Integration tests
├── storage/                  # Storage for research artifacts
│   └── papers/              # Generated papers
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── .gitattributes           # Git attributes for line endings
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` - AWS region (default: us-east-1)
- `AWS_BEDROCK_MODEL_ID` - Bedrock model ID (default: Claude 3.5 Sonnet)
- `TAVILY_API_KEY` - Tavily search API key

Optional configuration:
- `LOG_LEVEL` - Logging level (default: INFO)
- `CORS_ORIGINS` - Comma-separated CORS origins (default: http://localhost:3000)
- `MAX_ITERATIONS` - Maximum research iterations (default: 1)
- `QUALITY_THRESHOLD` - Quality score threshold (default: 8.0)
- `IMPROVEMENT_THRESHOLD` - Improvement threshold (default: 0.5)

### 4. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with service info
- `GET /health` - Health check
- `GET /config` - Current configuration (non-sensitive)

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run with Coverage

```bash
pytest --cov=flux_core --cov-report=html
```

### Run Specific Test Markers

```bash
# Skip slow tests
pytest -m "not slow"

# Skip integration tests
pytest -m "not integration"

# Run only unit tests
pytest -m unit
```

### Cross-Platform Testing

Test cross-platform compatibility (macOS, Linux, Windows):

```bash
# Run all cross-platform tests
pytest tests/unit/test_cross_platform.py -v

# Run platform-specific tests (auto-skipped on other platforms)
pytest tests/unit/test_cross_platform.py -k TestMacOSSpecific
pytest tests/unit/test_cross_platform.py -k TestLinuxSpecific
pytest tests/unit/test_cross_platform.py -k TestWindowsSpecific

# Run platform summary
pytest tests/unit/test_cross_platform.py::TestCrossPlatformSummary -v
```

**Platform Compatibility:**
- ✅ **macOS (Darwin)**: Full support with native paths
- ✅ **Linux**: Full support with POSIX paths
- ✅ **Windows**: Full support with pathlib handling drive letters and backslashes
- All file operations use `pathlib.Path` for cross-platform compatibility
- Async operations via `aiofiles` work on all platforms

## Components

### BedrockClient

AWS Bedrock client wrapper for Claude 3.5 Sonnet interactions.

```python
from flux_core.tools.bedrock_client import BedrockClient

# Initialize client (uses environment variables)
client = BedrockClient()

# Standard invocation
response = client.invoke(
    prompt="Explain quantum computing",
    system_prompt="You are a physics expert",
    max_tokens=2000
)

# Streaming invocation
for token in client.stream(prompt="Write a story"):
    print(token, end="", flush=True)
```

### ResearchState

LangGraph state definition for orbital research workflow.

```python
from flux_core.graph.state import create_initial_state

# Create initial research state
state = create_initial_state(
    question="How does quantum entanglement work?",
    research_id="research-123",
    max_iterations=5,
    quality_threshold=8.5
)
```

### Multi-Source Search

Search academic papers and web articles from multiple sources.

```python
from flux_core.tools.search import (
    search_semantic_scholar,
    search_arxiv,
    search_tavily,
    multi_source_search,
    get_available_sources
)

# Search individual sources
papers = search_semantic_scholar("machine learning", limit=10)
preprints = search_arxiv("neural networks", limit=10)
articles = search_tavily("AI research", limit=10)

# Multi-source search (combines all sources)
results = multi_source_search("deep learning", limit=20)

# Check which sources are available
sources = get_available_sources()
# {'semantic_scholar': True, 'arxiv': True, 'tavily': True}
```

**Features:**
- Semantic Scholar: Academic papers with citation counts
- ArXiv: Latest preprints sorted by date
- Tavily: Web articles (requires API key)
- Graceful degradation if sources unavailable
- Automatic result merging and sorting by relevance/recency

### Storage Module

Cross-platform async storage using pathlib and aiofiles.

```python
from flux_core.tools.storage import (
    save_paper,
    load_paper,
    list_papers,
    delete_paper,
    ensure_storage_dirs
)

# Ensure storage directories exist
ensure_storage_dirs()

# Save research paper
await save_paper("research-123", state)
# Saves: paper.md, metadata.json, conversation.json, state.json

# Load research paper
data = await load_paper("research-123")
print(data["paper"])  # Paper content
print(data["metadata"])  # Metadata

# List all papers
papers = await list_papers()
for paper in papers:
    print(f"{paper['research_id']}: {paper['question']}")

# Delete paper
await delete_paper("research-123")
```

**Features:**
- Cross-platform paths using `pathlib.Path`
- Async file operations with `aiofiles`
- Structured storage: papers, metadata, conversations, state
- Platform-independent directory handling

## Development

### Code Style

This project follows Python best practices:
- Type hints for all functions
- Docstrings for all public APIs
- Loguru for structured logging
- Pydantic for data validation

### Line Endings

This project uses LF line endings (Unix-style) by default, configured via `.gitattributes`:
- Shell scripts (`.sh`) always use LF
- Batch files (`.bat`) always use CRLF
- All other text files use LF

### Adding New Dependencies

```bash
# Add to requirements.txt with version pinning
pip install <package>
pip freeze | grep <package> >> requirements.txt
```

## Troubleshooting

### AWS Credentials Error

If you see "AWS credentials not provided":
1. Ensure `.env` file exists and contains valid AWS credentials
2. Verify credentials have access to AWS Bedrock
3. Check that the Bedrock model is available in your region

### Import Errors

If you encounter import errors:
```bash
# Ensure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Test Failures

If tests fail:
1. Ensure all dependencies are installed
2. Check that mocking is working correctly
3. Run tests with verbose output: `pytest -v`

## License

MIT License - See LICENSE file for details

