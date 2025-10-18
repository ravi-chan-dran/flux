"""
Pytest configuration and fixtures for FLUX tests.
Provides common fixtures, mocking utilities, and test configuration.
"""

import os
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, AsyncMock

# Load test environment if available
test_env_path = Path(__file__).parent.parent / ".env.test"
if test_env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(test_env_path)


@pytest.fixture
def test_config() -> dict[str, Any]:
    """
    Test configuration fixture.
    
    Returns configuration values for testing with sensible defaults.
    """
    return {
        "max_iterations": 3,
        "quality_threshold": 8.0,
        "improvement_threshold": 0.5,
        "mock_llm": True,
        "log_level": "WARNING",  # Less verbose during tests
    }


@pytest.fixture
def sample_state() -> dict[str, Any]:
    """
    Sample ResearchState fixture.
    
    Returns a complete, initialized research state for testing.
    """
    from flux_core.graph.state import create_initial_state
    
    state = create_initial_state(
        question="How does quantum entanglement work?",
        research_id="test-research-123",
        max_iterations=3,
        quality_threshold=8.0,
        improvement_threshold=0.5,
    )
    
    return state


@pytest.fixture
def sample_state_with_content() -> dict[str, Any]:
    """
    Sample ResearchState with hypotheses, sources, and experiments.
    
    Returns a state populated with sample research content.
    """
    from flux_core.graph.state import create_initial_state
    
    state = create_initial_state(
        question="How does quantum entanglement work?",
        research_id="test-research-456",
    )
    
    # Add sample hypotheses
    state["hypotheses"] = [
        {
            "id": "h1",
            "text": "Quantum entanglement demonstrates non-local correlations",
            "confidence": 85,
            "reasoning": "Based on Bell's theorem",
            "test_approach": "Bell inequality violation experiments",
        },
        {
            "id": "h2",
            "text": "Entanglement does not allow faster-than-light communication",
            "confidence": 95,
            "reasoning": "No-communication theorem",
            "test_approach": "Information transfer experiments",
        },
    ]
    
    # Add sample sources
    state["sources"] = [
        {
            "title": "Bell's Theorem and Quantum Entanglement",
            "authors": ["Bell, J."],
            "year": 1964,
            "abstract": "Paper on Bell's inequality and quantum mechanics",
            "url": "https://example.com/bell",
            "source_type": "semantic_scholar",
        },
        {
            "title": "Experimental Tests of Bell's Inequalities",
            "authors": ["Aspect, A.", "Grangier, P."],
            "year": 1982,
            "abstract": "Experimental verification of quantum entanglement",
            "url": "https://example.com/aspect",
            "source_type": "semantic_scholar",
        },
    ]
    
    # Add sample experiments
    state["experiments"] = [
        {
            "hypothesis_id": "h1",
            "method": "Conduct Bell inequality tests with entangled photons",
            "measurements": "Measure correlation coefficients at different angles",
            "success_criteria": "Violation of Bell inequality bounds",
            "time_estimate": "6 months",
            "potential_issues": "Detector efficiency loopholes",
        },
    ]
    
    state["phase"] = "experiments"
    
    return state


@pytest.fixture
def mock_search_results() -> list[dict[str, Any]]:
    """
    Mock search results fixture.
    
    Returns sample research sources from search.
    """
    return [
        {
            "title": "Introduction to Quantum Computing",
            "authors": ["Feynman, R."],
            "year": 1982,
            "abstract": "A foundational paper on quantum computing concepts",
            "url": "https://example.com/feynman1982",
            "source_type": "arxiv",
            "citation_count": 5000,
        },
        {
            "title": "Quantum Algorithms for Machine Learning",
            "authors": ["Lloyd, S.", "Mohseni, M."],
            "year": 2013,
            "abstract": "Exploring quantum speedups in machine learning",
            "url": "https://example.com/lloyd2013",
            "source_type": "arxiv",
            "citation_count": 1200,
        },
        {
            "title": "Recent Advances in Quantum Error Correction",
            "authors": ["Preskill, J."],
            "year": 2023,
            "abstract": "State-of-the-art error correction techniques",
            "url": "https://example.com/preskill2023",
            "source_type": "semantic_scholar",
            "citation_count": 150,
        },
    ]


@pytest.fixture
def mock_bedrock_response() -> str:
    """
    Mock Bedrock/Claude response fixture.
    
    Returns a sample LLM response for testing.
    """
    return """This is a sample response from Claude.

The analysis shows interesting patterns in the research question.
Key themes include quantum mechanics and information theory."""


@pytest.fixture
def mock_bedrock_client():
    """
    Mock BedrockClient fixture.
    
    Returns a fully mocked Bedrock client for testing.
    """
    from unittest.mock import Mock
    
    mock_client = Mock()
    
    # Mock invoke method
    mock_client.invoke = Mock(return_value="Mocked LLM response")
    
    # Mock stream method
    mock_client.stream = Mock(return_value=iter(["Mocked ", "stream ", "response"]))
    
    return mock_client


@pytest.fixture
def mock_agents():
    """
    Mock all agent classes.
    
    Returns dict of mocked agents for testing without LLM calls.
    """
    from unittest.mock import AsyncMock
    
    agents = {}
    
    # Mock each agent
    for agent_name in ["flow_master", "current", "source", "channel", "filter", "confluence"]:
        mock_agent = Mock()
        mock_agent.name = agent_name.replace("_", " ").title()
        mock_agent.emoji = "🤖"
        mock_agent.invoke_model = AsyncMock(return_value="Mock response")
        mock_agent.format_message = Mock(return_value={
            "agent": mock_agent.name,
            "message": "Mock message",
            "timestamp": "2024-01-01T00:00:00",
        })
        agents[agent_name] = mock_agent
    
    return agents


@pytest.fixture
def mock_quality_scores():
    """
    Mock quality score progression fixture.
    
    Returns a sequence of quality scores for testing iteration logic.
    """
    return {
        "low_quality": [3.0, 4.0, 4.5],  # Below threshold
        "improving": [5.0, 6.5, 8.0],    # Improves to threshold
        "high_quality": [8.5, 9.0, 9.2],  # Above threshold
        "plateau": [6.0, 6.2, 6.3],      # Insufficient improvement
    }


@pytest.fixture
def temp_storage_dir(tmp_path):
    """
    Temporary storage directory fixture.
    
    Creates a temporary directory for testing storage operations.
    """
    storage_dir = tmp_path / "storage" / "papers"
    storage_dir.mkdir(parents=True)
    return storage_dir


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_aws: marks tests requiring AWS credentials"
    )
    config.addinivalue_line(
        "markers", "requires_api_keys: marks tests requiring API keys"
    )


# Set environment variables for testing
@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    # Set test environment variables
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    os.environ.setdefault("MAX_ITERATIONS", "3")
    os.environ.setdefault("QUALITY_THRESHOLD", "8.0")
    os.environ.setdefault("IMPROVEMENT_THRESHOLD", "0.5")
    
    # Mock AWS credentials if not set
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        os.environ["AWS_ACCESS_KEY_ID"] = "test_key"
    if not os.getenv("AWS_SECRET_ACCESS_KEY"):
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret"
    if not os.getenv("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"


# Async fixture support
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

