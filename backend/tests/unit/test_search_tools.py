"""
Unit tests for multi-source search tools.
Tests Semantic Scholar, ArXiv, Tavily, and multi-source search.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from flux_core.tools.search import (
    search_semantic_scholar,
    search_arxiv,
    search_tavily,
    multi_source_search,
    get_available_sources,
    SearchError,
)


@pytest.fixture
def mock_semantic_scholar_available():
    """Mock Semantic Scholar as available."""
    with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True):
        yield


@pytest.fixture
def mock_arxiv_available():
    """Mock ArXiv as available."""
    with patch("flux_core.tools.search.ARXIV_AVAILABLE", True):
        yield


@pytest.fixture
def mock_tavily_available():
    """Mock Tavily as available."""
    with patch("flux_core.tools.search.TAVILY_AVAILABLE", True):
        yield


class TestSemanticScholarSearch:
    """Tests for Semantic Scholar search."""
    
    def test_returns_results(self, mock_semantic_scholar_available):
        """Test that Semantic Scholar search returns results."""
        # Mock paper object
        mock_paper = Mock()
        mock_paper.title = "Test Paper"
        mock_paper.paperId = "12345"
        mock_paper.url = "https://example.com/paper"
        mock_paper.abstract = "This is a test abstract"
        mock_paper.year = 2023
        mock_paper.citationCount = 42
        
        # Mock author
        mock_author = Mock()
        mock_author.name = "John Doe"
        mock_paper.authors = [mock_author]
        
        # Mock SemanticScholar client
        with patch("flux_core.tools.search.SemanticScholar") as mock_ss:
            mock_client = Mock()
            mock_client.search_paper.return_value = [mock_paper]
            mock_ss.return_value = mock_client
            
            results = search_semantic_scholar("quantum computing", limit=10)
            
            assert len(results) == 1
            assert results[0]["title"] == "Test Paper"
            assert results[0]["url"] == "https://example.com/paper"
            assert results[0]["abstract"] == "This is a test abstract"
            assert results[0]["year"] == 2023
            assert results[0]["authors"] == ["John Doe"]
            assert results[0]["source_type"] == "semantic_scholar"
            assert results[0]["citation_count"] == 42
    
    def test_handles_no_results(self, mock_semantic_scholar_available):
        """Test handling when no results are found."""
        with patch("flux_core.tools.search.SemanticScholar") as mock_ss:
            mock_client = Mock()
            mock_client.search_paper.return_value = []
            mock_ss.return_value = mock_client
            
            results = search_semantic_scholar("nonexistent query", limit=10)
            
            assert results == []
    
    def test_respects_limit(self, mock_semantic_scholar_available):
        """Test that search respects the limit parameter."""
        mock_papers = []
        for i in range(15):
            mock_paper = Mock()
            mock_paper.title = f"Paper {i}"
            mock_paper.paperId = f"id{i}"
            mock_paper.url = f"https://example.com/{i}"
            mock_paper.abstract = f"Abstract {i}"
            mock_paper.year = 2023
            mock_paper.citationCount = i
            mock_paper.authors = []
            mock_papers.append(mock_paper)
        
        with patch("flux_core.tools.search.SemanticScholar") as mock_ss:
            mock_client = Mock()
            mock_client.search_paper.return_value = mock_papers[:5]  # Simulate API respecting limit
            mock_ss.return_value = mock_client
            
            results = search_semantic_scholar("test", limit=5)
            
            assert len(results) == 5
            mock_client.search_paper.assert_called_once_with("test", limit=5)
    
    def test_handles_missing_fields(self, mock_semantic_scholar_available):
        """Test handling papers with missing fields."""
        mock_paper = Mock()
        mock_paper.title = None
        mock_paper.paperId = "123"
        mock_paper.url = None
        mock_paper.abstract = None
        mock_paper.year = None
        mock_paper.citationCount = None
        mock_paper.authors = None
        
        with patch("flux_core.tools.search.SemanticScholar") as mock_ss:
            mock_client = Mock()
            mock_client.search_paper.return_value = [mock_paper]
            mock_ss.return_value = mock_client
            
            results = search_semantic_scholar("test", limit=1)
            
            assert len(results) == 1
            assert results[0]["title"] == "Untitled"
            assert "semanticscholar.org" in results[0]["url"]
            assert results[0]["abstract"] == ""
            assert results[0]["year"] is None
            assert results[0]["authors"] == []
            assert results[0]["citation_count"] == 0
    
    def test_not_available_returns_empty(self):
        """Test that unavailable Semantic Scholar returns empty list."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", False):
            results = search_semantic_scholar("test", limit=10)
            assert results == []
    
    def test_handles_api_error(self, mock_semantic_scholar_available):
        """Test handling of API errors."""
        with patch("flux_core.tools.search.SemanticScholar") as mock_ss:
            mock_client = Mock()
            mock_client.search_paper.side_effect = Exception("API Error")
            mock_ss.return_value = mock_client
            
            with pytest.raises(SearchError) as exc_info:
                search_semantic_scholar("test", limit=10)
            
            assert "Semantic Scholar search failed" in str(exc_info.value)


class TestArXivSearch:
    """Tests for ArXiv search."""
    
    def test_returns_results(self, mock_arxiv_available):
        """Test that ArXiv search returns results."""
        from datetime import datetime
        
        # Mock ArXiv result
        mock_result = Mock()
        mock_result.title = "Neural Networks Paper"
        mock_result.entry_id = "https://arxiv.org/abs/2301.12345"
        mock_result.summary = "This is about neural networks"
        mock_result.published = datetime(2023, 1, 15)
        mock_result.categories = ["cs.AI", "cs.LG"]
        
        mock_author = Mock()
        mock_author.name = "Jane Smith"
        mock_result.authors = [mock_author]
        
        # Mock ArXiv search
        with patch("flux_core.tools.search.arxiv.Search") as mock_search:
            mock_search_instance = Mock()
            mock_search_instance.results.return_value = [mock_result]
            mock_search.return_value = mock_search_instance
            
            results = search_arxiv("neural networks", limit=10)
            
            assert len(results) == 1
            assert results[0]["title"] == "Neural Networks Paper"
            assert "2301.12345" in results[0]["url"]
            assert results[0]["abstract"] == "This is about neural networks"
            assert results[0]["year"] == 2023
            assert results[0]["authors"] == ["Jane Smith"]
            assert results[0]["source_type"] == "arxiv"
            assert results[0]["categories"] == ["cs.AI", "cs.LG"]
    
    def test_handles_no_results(self, mock_arxiv_available):
        """Test handling when no results are found."""
        with patch("flux_core.tools.search.arxiv.Search") as mock_search:
            mock_search_instance = Mock()
            mock_search_instance.results.return_value = []
            mock_search.return_value = mock_search_instance
            
            results = search_arxiv("nonexistent query", limit=10)
            
            assert results == []
    
    def test_respects_limit(self, mock_arxiv_available):
        """Test that search respects the limit parameter."""
        from datetime import datetime
        
        mock_results = []
        for i in range(5):
            mock_result = Mock()
            mock_result.title = f"Paper {i}"
            mock_result.entry_id = f"https://arxiv.org/abs/230{i}.{i:05d}"
            mock_result.summary = f"Summary {i}"
            mock_result.published = datetime(2023, 1, i + 1)
            mock_result.authors = []
            mock_result.categories = ["cs.AI"]
            mock_results.append(mock_result)
        
        with patch("flux_core.tools.search.arxiv.Search") as mock_search:
            mock_search_instance = Mock()
            mock_search_instance.results.return_value = mock_results
            mock_search.return_value = mock_search_instance
            
            results = search_arxiv("test", limit=5)
            
            assert len(results) == 5
            # Verify max_results parameter
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs["max_results"] == 5
    
    def test_sorted_by_date(self, mock_arxiv_available):
        """Test that results are sorted by submission date."""
        with patch("flux_core.tools.search.arxiv.Search") as mock_search:
            mock_search_instance = Mock()
            mock_search.return_value = mock_search_instance
            
            search_arxiv("test", limit=10)
            
            # Verify sort parameters
            call_kwargs = mock_search.call_args[1]
            assert "sort_by" in call_kwargs
            assert "sort_order" in call_kwargs
    
    def test_not_available_returns_empty(self):
        """Test that unavailable ArXiv returns empty list."""
        with patch("flux_core.tools.search.ARXIV_AVAILABLE", False):
            results = search_arxiv("test", limit=10)
            assert results == []
    
    def test_handles_api_error(self, mock_arxiv_available):
        """Test handling of API errors."""
        with patch("flux_core.tools.search.arxiv.Search") as mock_search:
            mock_search.side_effect = Exception("ArXiv API Error")
            
            with pytest.raises(SearchError) as exc_info:
                search_arxiv("test", limit=10)
            
            assert "ArXiv search failed" in str(exc_info.value)


class TestTavilySearch:
    """Tests for Tavily search."""
    
    def test_returns_results(self, mock_tavily_available, monkeypatch):
        """Test that Tavily search returns results."""
        monkeypatch.setenv("TAVILY_API_KEY", "test_key")
        
        mock_response = {
            "results": [
                {
                    "title": "Web Article",
                    "url": "https://example.com/article",
                    "content": "This is web content about quantum computing",
                    "score": 0.95,
                }
            ]
        }
        
        with patch("flux_core.tools.search.TavilyClient") as mock_tavily:
            mock_client = Mock()
            mock_client.search.return_value = mock_response
            mock_tavily.return_value = mock_client
            
            results = search_tavily("quantum computing", limit=10)
            
            assert len(results) == 1
            assert results[0]["title"] == "Web Article"
            assert results[0]["url"] == "https://example.com/article"
            assert "quantum computing" in results[0]["content"]
            assert results[0]["source_type"] == "tavily"
            assert results[0]["score"] == 0.95
    
    def test_handles_no_results(self, mock_tavily_available, monkeypatch):
        """Test handling when no results are found."""
        monkeypatch.setenv("TAVILY_API_KEY", "test_key")
        
        mock_response = {"results": []}
        
        with patch("flux_core.tools.search.TavilyClient") as mock_tavily:
            mock_client = Mock()
            mock_client.search.return_value = mock_response
            mock_tavily.return_value = mock_client
            
            results = search_tavily("nonexistent", limit=10)
            
            assert results == []
    
    def test_respects_limit(self, mock_tavily_available, monkeypatch):
        """Test that search respects the limit parameter."""
        monkeypatch.setenv("TAVILY_API_KEY", "test_key")
        
        mock_response = {
            "results": [
                {"title": f"Article {i}", "url": f"https://example.com/{i}", 
                 "content": f"Content {i}", "score": 0.8}
                for i in range(5)
            ]
        }
        
        with patch("flux_core.tools.search.TavilyClient") as mock_tavily:
            mock_client = Mock()
            mock_client.search.return_value = mock_response
            mock_tavily.return_value = mock_client
            
            results = search_tavily("test", limit=5)
            
            assert len(results) == 5
            mock_client.search.assert_called_once_with("test", max_results=5)
    
    def test_no_api_key_returns_empty(self, mock_tavily_available, monkeypatch):
        """Test that missing API key returns empty list."""
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        
        results = search_tavily("test", limit=10)
        
        assert results == []
    
    def test_not_available_returns_empty(self):
        """Test that unavailable Tavily returns empty list."""
        with patch("flux_core.tools.search.TAVILY_AVAILABLE", False):
            results = search_tavily("test", limit=10)
            assert results == []
    
    def test_handles_api_error(self, mock_tavily_available, monkeypatch):
        """Test handling of API errors."""
        monkeypatch.setenv("TAVILY_API_KEY", "test_key")
        
        with patch("flux_core.tools.search.TavilyClient") as mock_tavily:
            mock_client = Mock()
            mock_client.search.side_effect = Exception("Tavily API Error")
            mock_tavily.return_value = mock_client
            
            with pytest.raises(SearchError) as exc_info:
                search_tavily("test", limit=10)
            
            assert "Tavily search failed" in str(exc_info.value)


class TestMultiSourceSearch:
    """Tests for multi-source search."""
    
    def test_combines_results_properly(self):
        """Test that multi-source search combines results from all sources."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", True), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", True), \
             patch("flux_core.tools.search.search_semantic_scholar") as mock_ss, \
             patch("flux_core.tools.search.search_arxiv") as mock_arxiv, \
             patch("flux_core.tools.search.search_tavily") as mock_tavily, \
             patch.dict("os.environ", {"TAVILY_API_KEY": "test_key"}):
            
            mock_ss.return_value = [
                {"title": "SS Paper", "year": 2023, "source_type": "semantic_scholar", 
                 "citation_count": 10}
            ]
            mock_arxiv.return_value = [
                {"title": "ArXiv Paper", "year": 2024, "source_type": "arxiv"}
            ]
            mock_tavily.return_value = [
                {"title": "Web Article", "year": None, "source_type": "tavily", "score": 0.9}
            ]
            
            results = multi_source_search("test query", limit=10)
            
            assert len(results) == 3
            source_types = [r["source_type"] for r in results]
            assert "semantic_scholar" in source_types
            assert "arxiv" in source_types
            assert "tavily" in source_types
    
    def test_handles_partial_failures(self):
        """Test that multi-source handles when one source fails."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", True), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", False), \
             patch("flux_core.tools.search.search_semantic_scholar") as mock_ss, \
             patch("flux_core.tools.search.search_arxiv") as mock_arxiv:
            
            # Semantic Scholar fails
            mock_ss.side_effect = SearchError("SS failed")
            
            # ArXiv succeeds
            mock_arxiv.return_value = [
                {"title": "ArXiv Paper", "year": 2024, "source_type": "arxiv"}
            ]
            
            results = multi_source_search("test query", limit=10)
            
            # Should still get ArXiv results
            assert len(results) == 1
            assert results[0]["source_type"] == "arxiv"
    
    def test_returns_top_n_results(self):
        """Test that multi-source returns only top N results."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", True), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", False), \
             patch("flux_core.tools.search.search_semantic_scholar") as mock_ss, \
             patch("flux_core.tools.search.search_arxiv") as mock_arxiv:
            
            # Return many results from each source
            mock_ss.return_value = [
                {"title": f"SS Paper {i}", "year": 2023, "source_type": "semantic_scholar",
                 "citation_count": i}
                for i in range(10)
            ]
            mock_arxiv.return_value = [
                {"title": f"ArXiv Paper {i}", "year": 2024, "source_type": "arxiv"}
                for i in range(10)
            ]
            
            results = multi_source_search("test query", limit=5)
            
            # Should only return 5 total results
            assert len(results) == 5
    
    def test_sorts_by_relevance_and_recency(self):
        """Test that results are sorted by year and citation count."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", False), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", False), \
             patch("flux_core.tools.search.search_semantic_scholar") as mock_ss:
            
            mock_ss.return_value = [
                {"title": "Old Paper", "year": 2020, "source_type": "semantic_scholar",
                 "citation_count": 100},
                {"title": "Recent Paper", "year": 2024, "source_type": "semantic_scholar",
                 "citation_count": 5},
                {"title": "Mid Paper", "year": 2022, "source_type": "semantic_scholar",
                 "citation_count": 50},
            ]
            
            results = multi_source_search("test query", limit=10)
            
            # Most recent should be first
            assert results[0]["year"] == 2024
            assert results[0]["title"] == "Recent Paper"
    
    def test_handles_all_sources_failing(self):
        """Test handling when all sources fail."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", True), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", True), \
             patch("flux_core.tools.search.search_semantic_scholar") as mock_ss, \
             patch("flux_core.tools.search.search_arxiv") as mock_arxiv, \
             patch("flux_core.tools.search.search_tavily") as mock_tavily, \
             patch.dict("os.environ", {"TAVILY_API_KEY": "test_key"}):
            
            mock_ss.side_effect = SearchError("SS failed")
            mock_arxiv.side_effect = SearchError("ArXiv failed")
            mock_tavily.side_effect = SearchError("Tavily failed")
            
            results = multi_source_search("test query", limit=10)
            
            assert results == []
    
    def test_handles_no_available_sources(self):
        """Test when no sources are available."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", False), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", False), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", False):
            
            results = multi_source_search("test query", limit=10)
            
            assert results == []


class TestGetAvailableSources:
    """Tests for get_available_sources."""
    
    def test_returns_availability_dict(self):
        """Test that function returns correct availability dictionary."""
        with patch("flux_core.tools.search.SEMANTIC_SCHOLAR_AVAILABLE", True), \
             patch("flux_core.tools.search.ARXIV_AVAILABLE", False), \
             patch("flux_core.tools.search.TAVILY_AVAILABLE", True), \
             patch.dict("os.environ", {"TAVILY_API_KEY": "test_key"}):
            
            sources = get_available_sources()
            
            assert sources["semantic_scholar"] is True
            assert sources["arxiv"] is False
            assert sources["tavily"] is True
    
    def test_tavily_unavailable_without_api_key(self):
        """Test that Tavily is unavailable without API key."""
        with patch("flux_core.tools.search.TAVILY_AVAILABLE", True), \
             patch.dict("os.environ", {}, clear=True):
            
            sources = get_available_sources()
            
            assert sources["tavily"] is False


@pytest.mark.slow
@pytest.mark.integration
class TestSearchIntegration:
    """
    Integration tests for search tools.
    These tests require actual API access and are marked as 'integration' and 'slow'.
    Run with: pytest -m integration
    """
    
    @pytest.mark.skip(reason="Requires Semantic Scholar API access")
    def test_real_semantic_scholar_search(self):
        """Test real Semantic Scholar search."""
        results = search_semantic_scholar("machine learning", limit=5)
        assert len(results) > 0
        assert all("title" in r for r in results)
    
    @pytest.mark.skip(reason="Requires ArXiv API access")
    def test_real_arxiv_search(self):
        """Test real ArXiv search."""
        results = search_arxiv("neural networks", limit=5)
        assert len(results) > 0
        assert all("title" in r for r in results)
    
    @pytest.mark.skip(reason="Requires Tavily API key")
    def test_real_tavily_search(self):
        """Test real Tavily search."""
        results = search_tavily("artificial intelligence", limit=5)
        assert len(results) > 0
        assert all("title" in r for r in results)
    
    @pytest.mark.skip(reason="Requires all APIs")
    def test_real_multi_source_search(self):
        """Test real multi-source search."""
        results = multi_source_search("deep learning", limit=10)
        assert len(results) > 0
        sources = {r["source_type"] for r in results}
        assert len(sources) > 1  # Should have multiple sources

