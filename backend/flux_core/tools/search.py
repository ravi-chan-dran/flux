"""
Multi-Source Search Tools for Research
Searches academic papers, preprints, and web articles.
"""

import os
from typing import Any
from loguru import logger

# Try to import search libraries, handle gracefully if not available
SEMANTIC_SCHOLAR_AVAILABLE = False
ARXIV_AVAILABLE = False
TAVILY_AVAILABLE = False

try:
    from semanticscholar import SemanticScholar
    SEMANTIC_SCHOLAR_AVAILABLE = True
    logger.info("Semantic Scholar available")
except ImportError:
    logger.warning("Semantic Scholar not available - install semanticscholar package")

try:
    import arxiv
    ARXIV_AVAILABLE = True
    logger.info("ArXiv search available")
except ImportError:
    logger.warning("ArXiv not available - install arxiv package")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
    logger.info("Tavily search available")
except ImportError:
    logger.warning("Tavily not available - install tavily-python package")


class SearchError(Exception):
    """Custom exception for search errors."""
    pass


def search_semantic_scholar(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search Semantic Scholar for academic papers.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of paper dictionaries with title, url, abstract, year, authors, source_type
    
    Raises:
        SearchError: If search fails
    """
    if not SEMANTIC_SCHOLAR_AVAILABLE:
        logger.warning("Semantic Scholar not available, returning empty results")
        return []
    
    try:
        logger.info(f"Searching Semantic Scholar for: {query} (limit: {limit})")
        
        sch = SemanticScholar()
        results = sch.search_paper(query, limit=limit)
        
        papers = []
        for paper in results:
            # Extract author names
            authors = []
            if paper.authors:
                authors = [author.name for author in paper.authors if author.name]
            
            paper_dict = {
                "title": paper.title or "Untitled",
                "url": paper.url or f"https://www.semanticscholar.org/paper/{paper.paperId}",
                "abstract": paper.abstract or "",
                "year": paper.year or None,
                "authors": authors,
                "source_type": "semantic_scholar",
                "citation_count": paper.citationCount or 0,
                "paper_id": paper.paperId,
            }
            papers.append(paper_dict)
        
        logger.info(f"Found {len(papers)} papers from Semantic Scholar")
        return papers
    
    except Exception as e:
        error_msg = f"Semantic Scholar search failed: {str(e)}"
        logger.error(error_msg)
        raise SearchError(error_msg) from e


def search_arxiv(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search ArXiv for AI/ML preprints, sorted by date.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of paper dictionaries with title, url, abstract, year, authors, source_type
    
    Raises:
        SearchError: If search fails
    """
    if not ARXIV_AVAILABLE:
        logger.warning("ArXiv not available, returning empty results")
        return []
    
    try:
        logger.info(f"Searching ArXiv for: {query} (limit: {limit})")
        
        # Create search with sorting by submission date (most recent first)
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        papers = []
        for result in search.results():
            # Extract author names
            authors = [author.name for author in result.authors]
            
            paper_dict = {
                "title": result.title,
                "url": result.entry_id,
                "abstract": result.summary,
                "year": result.published.year if result.published else None,
                "authors": authors,
                "source_type": "arxiv",
                "published_date": result.published.isoformat() if result.published else None,
                "arxiv_id": result.entry_id.split("/")[-1],
                "categories": result.categories,
            }
            papers.append(paper_dict)
        
        logger.info(f"Found {len(papers)} papers from ArXiv")
        return papers
    
    except Exception as e:
        error_msg = f"ArXiv search failed: {str(e)}"
        logger.error(error_msg)
        raise SearchError(error_msg) from e


def search_tavily(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search Tavily for web articles (if API key available).
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of article dictionaries with title, url, content, year, authors, source_type
    
    Raises:
        SearchError: If search fails
    """
    if not TAVILY_AVAILABLE:
        logger.warning("Tavily not available, returning empty results")
        return []
    
    # Check for API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set, skipping Tavily search")
        return []
    
    try:
        # Truncate query if too long (Tavily has query length limits)
        # Extract key terms from long queries
        if len(query) > 500:
            # Split by sentences and take first few meaningful parts
            sentences = query.split('. ')
            truncated_query = '. '.join(sentences[:3])  # Take first 3 sentences
            if len(truncated_query) > 500:
                truncated_query = truncated_query[:500]
            logger.info(f"Query too long ({len(query)} chars), truncated to: {truncated_query[:100]}...")
            query = truncated_query
        
        logger.info(f"Searching Tavily for: {query[:100]}... (limit: {limit})")
        
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=limit)
        
        articles = []
        if response and "results" in response:
            for result in response["results"]:
                article_dict = {
                    "title": result.get("title", "Untitled"),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "abstract": result.get("content", "")[:500],  # Use first 500 chars as abstract
                    "year": None,  # Tavily doesn't provide publication year
                    "authors": [],  # Tavily doesn't provide authors
                    "source_type": "tavily",
                    "score": result.get("score", 0.0),
                }
                articles.append(article_dict)
        
        logger.info(f"Found {len(articles)} articles from Tavily")
        return articles
    
    except Exception as e:
        error_msg = f"Tavily search failed: {str(e)}"
        logger.error(error_msg)
        
        # Log additional details for debugging
        if "400" in str(e):
            logger.error(f"Bad Request - Query length: {len(query)}, Query preview: {query[:200]}...")
            logger.error("This might be due to query length limits or invalid characters")
        elif "401" in str(e):
            logger.error("Unauthorized - Check TAVILY_API_KEY")
        elif "429" in str(e):
            logger.error("Rate limited - Too many requests")
        
        raise SearchError(error_msg) from e


def multi_source_search(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search multiple sources and combine results.
    
    Calls all available search sources (Semantic Scholar, ArXiv, Tavily),
    combines results, sorts by relevance and recency, and returns top N.
    
    Args:
        query: Search query string
        limit: Maximum number of total results to return
    
    Returns:
        Combined and sorted list of results from all sources
    """
    logger.info(f"Multi-source search for: {query}")
    logger.info(f"Available sources: SS={SEMANTIC_SCHOLAR_AVAILABLE}, "
                f"ArXiv={ARXIV_AVAILABLE}, Tavily={TAVILY_AVAILABLE}")
    
    all_results = []
    sources_used = []
    sources_failed = []
    
    # Search each source, handle failures gracefully
    per_source_limit = max(limit // 3, 5)  # Get more from each source, filter later
    
    # Semantic Scholar
    if SEMANTIC_SCHOLAR_AVAILABLE:
        try:
            ss_results = search_semantic_scholar(query, limit=per_source_limit)
            all_results.extend(ss_results)
            sources_used.append("semantic_scholar")
            logger.info(f"Added {len(ss_results)} results from Semantic Scholar")
        except SearchError as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            sources_failed.append("semantic_scholar")
    
    # ArXiv
    if ARXIV_AVAILABLE:
        try:
            arxiv_results = search_arxiv(query, limit=per_source_limit)
            all_results.extend(arxiv_results)
            sources_used.append("arxiv")
            logger.info(f"Added {len(arxiv_results)} results from ArXiv")
        except SearchError as e:
            logger.error(f"ArXiv search failed: {e}")
            sources_failed.append("arxiv")
    
    # Tavily
    if TAVILY_AVAILABLE and os.getenv("TAVILY_API_KEY"):
        try:
            tavily_results = search_tavily(query, limit=per_source_limit)
            all_results.extend(tavily_results)
            sources_used.append("tavily")
            logger.info(f"Added {len(tavily_results)} results from Tavily")
        except SearchError as e:
            logger.error(f"Tavily search failed: {e}")
            sources_failed.append("tavily")
            
            # Try with a simplified query as fallback
            try:
                # Extract key terms from the original query
                simplified_query = query.split('\n')[0]  # Take first line
                if len(simplified_query) > 200:
                    simplified_query = simplified_query[:200]
                logger.info(f"Trying Tavily with simplified query: {simplified_query[:100]}...")
                
                tavily_fallback_results = search_tavily(simplified_query, limit=per_source_limit)
                all_results.extend(tavily_fallback_results)
                sources_used.append("tavily_fallback")
                logger.info(f"Added {len(tavily_fallback_results)} results from Tavily (fallback)")
            except SearchError as fallback_e:
                logger.error(f"Tavily fallback also failed: {fallback_e}")
                sources_failed.append("tavily_fallback")
    
    if not all_results:
        logger.warning("No results from any source")
        return []
    
    # Sort by relevance and recency
    # Priority: recent papers (year), citation count, score
    def sort_key(item: dict[str, Any]) -> tuple:
        year = item.get("year") or 0
        citation_count = item.get("citation_count", 0)
        score = item.get("score", 0.5)
        
        # Boost recent papers
        year_score = year if year > 0 else 0
        
        # Combine metrics (higher is better)
        return (-year_score, -citation_count, -score)
    
    sorted_results = sorted(all_results, key=sort_key)
    
    # Return top N results
    top_results = sorted_results[:limit]
    
    logger.info(f"Multi-source search complete: {len(top_results)} results from "
                f"{len(sources_used)} sources")
    if sources_failed:
        logger.warning(f"Failed sources: {', '.join(sources_failed)}")
    
    return top_results


def get_available_sources() -> dict[str, bool]:
    """
    Get dictionary of available search sources.
    
    Returns:
        Dictionary mapping source names to availability status
    """
    return {
        "semantic_scholar": SEMANTIC_SCHOLAR_AVAILABLE,
        "arxiv": ARXIV_AVAILABLE,
        "tavily": TAVILY_AVAILABLE and bool(os.getenv("TAVILY_API_KEY")),
    }

