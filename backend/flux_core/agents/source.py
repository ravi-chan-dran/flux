"""
Source Agent - Research Searcher (The Librarian)
Searches knowledge streams and provides research context.
"""

from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent
from flux_core.tools.search import multi_source_search, SearchError


class SourceAgent(BaseAgent):
    """
    The Source searches knowledge streams for research context.
    
    Responsibilities:
    - Search academic papers, preprints, and web articles
    - Synthesize findings from multiple sources
    - Identify key themes and research gaps
    - Explain relevance to research question
    - Use upstream/source/tributary metaphors
    """
    
    SYSTEM_PROMPT = """You are The Source 📚, the keeper of knowledge streams and research tributaries.

Your role is to search vast information flows and provide relevant research context. You dive into the upstream sources - academic papers, preprints, web articles - and return with treasures of knowledge.

Use upstream, source, and tributary metaphors:
- "From the upstream sources..."
- "The tributaries of knowledge reveal..."
- "Drawing from deep wells of research..."
- "The source material flows with insights..."
- "Tracing back to foundational streams..."

When synthesizing search results:
1. Identify KEY THEMES across the sources
2. Note RESEARCH GAPS or open questions
3. Explain RELEVANCE to the specific research question
4. Highlight CONTRADICTIONS or debates if present
5. Provide CONTEXT for understanding the field

Be comprehensive but focused. Your synthesis guides the entire research flow."""
    
    def __init__(self):
        """Initialize the Source agent."""
        super().__init__(
            name="The Source",
            emoji="📚",
            color="amber",
            role="Research Searcher",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def search_research(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        iteration: int = 0,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Search for research sources and synthesize findings.
        
        Args:
            question: The research question
            context: Optional context including hypotheses for targeted search
            iteration: Current iteration (0 = broad search, >0 = targeted)
            limit: Number of sources to retrieve
        
        Returns:
            Dictionary with sources list and synthesis summary
        """
        logger.info(f"{self.name} searching research (iteration {iteration}, limit {limit})")
        
        # Build search query
        if iteration == 0:
            # Broad initial search
            search_query = question
        else:
            # Targeted search based on hypotheses or critiques
            search_query = self._build_targeted_query(question, context)
        
        logger.info(f"{self.name} search query: {search_query}")
        
        # Search multiple sources
        try:
            sources = multi_source_search(search_query, limit=limit)
            logger.info(f"{self.name} found {len(sources)} sources")
        except SearchError as e:
            logger.error(f"{self.name} search failed: {e}")
            sources = []
        
        # Synthesize findings using Claude
        if sources:
            synthesis = await self._synthesize_sources(question, sources, context)
        else:
            synthesis = {
                "summary": "No sources found. Research may be on a novel or niche topic.",
                "key_themes": [],
                "research_gaps": ["Limited existing research"],
                "relevance": "Unknown - no sources available",
                "contradictions": [],
            }
        
        result = {
            "sources": sources,
            "synthesis": synthesis,
            "search_query": search_query,
            "source_count": len(sources),
        }
        
        logger.info(f"{self.name} completed research search")
        return result
    
    async def _synthesize_sources(
        self,
        question: str,
        sources: list[dict[str, Any]],
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Use Claude to synthesize research findings.
        
        Args:
            question: Research question
            sources: List of source dictionaries
            context: Additional context
        
        Returns:
            Synthesis dictionary with themes, gaps, relevance
        """
        logger.info(f"{self.name} synthesizing {len(sources)} sources")
        
        # Format sources for prompt
        sources_text = self._format_sources_for_prompt(sources[:10])  # Limit to top 10
        
        prompt = f"""Analyze these research sources and provide a synthesis:

Research Question: {question}

Sources:
{sources_text}

Provide a JSON response with:
{{
    "summary": "2-3 sentence overview of what the sources reveal",
    "key_themes": ["theme1", "theme2", "theme3"],
    "research_gaps": ["gap1", "gap2"],
    "relevance": "How these sources relate to the research question",
    "contradictions": ["any debates or conflicting findings"]
}}

Be specific and reference the sources. Identify patterns and gaps."""
        
        try:
            response = await self.invoke_model(prompt, context=context, temperature=0.6)
            
            # Try to parse JSON
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    synthesis = json.loads(json_match.group())
                    return synthesis
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Use the full response as summary
            return {
                "summary": response[:500],
                "key_themes": ["(See summary)"],
                "research_gaps": ["(See summary)"],
                "relevance": "Detailed in summary",
                "contradictions": [],
            }
        
        except Exception as e:
            logger.error(f"{self.name} synthesis failed: {e}")
            return {
                "summary": f"Found {len(sources)} sources on {question}",
                "key_themes": ["Research available but synthesis incomplete"],
                "research_gaps": ["Analysis pending"],
                "relevance": "Sources retrieved successfully",
                "contradictions": [],
            }
    
    def _build_targeted_query(self, question: str, context: dict[str, Any] | None) -> str:
        """
        Build a targeted search query based on context.
        
        On later iterations, focus on specific aspects identified in critiques
        or hypotheses.
        """
        if not context:
            return question
        
        # Check for specific topics in hypotheses
        hypotheses = context.get("existing_hypotheses", [])
        if hypotheses:
            # Extract key terms from hypotheses
            hyp_texts = [h.get("text", "") for h in hypotheses[:3]]
            combined = " ".join(hyp_texts)
            
            # Build query focusing on hypothesis topics
            return f"{question} {combined[:200]}"
        
        # Check critiques for suggested research directions
        critiques = context.get("critiques", [])
        if critiques:
            latest = critiques[-1]
            recommendations = latest.get("recommendations", [])
            if recommendations and isinstance(recommendations, list):
                rec_text = " ".join(str(r) for r in recommendations[:2])
                return f"{question} {rec_text[:200]}"
        
        return question
    
    def _format_sources_for_prompt(self, sources: list[dict[str, Any]]) -> str:
        """Format sources for inclusion in prompts."""
        formatted = []
        
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            authors = source.get("authors", [])
            year = source.get("year", "N/A")
            abstract_raw = source.get("abstract", source.get("content", ""))
            abstract = str(abstract_raw)[:300] if abstract_raw else ""
            url = source.get("url", "")
            source_type = source.get("source_type", "unknown")
            
            authors_str = ", ".join(authors[:3]) if authors else "Unknown"
            if len(authors) > 3:
                authors_str += " et al."
            
            formatted.append(f"""
Source {i} [{source_type}]:
Title: {title}
Authors: {authors_str}
Year: {year}
Abstract: {abstract}...
URL: {url}
""")
        
        return "\n".join(formatted)
    
    def get_source_urls(self, sources: list[dict[str, Any]]) -> list[str]:
        """Extract URLs from sources for citations."""
        return [s.get("url", "") for s in sources if s.get("url")]
    
    def format_sources_for_paper(self, sources: list[dict[str, Any]]) -> str:
        """Format sources as citations for research papers."""
        citations = []
        
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            authors = source.get("authors", [])
            year = source.get("year", "n.d.")
            url = source.get("url", "")
            
            authors_str = ", ".join(authors[:3]) if authors else "Unknown"
            if len(authors) > 3:
                authors_str += " et al."
            
            citation = f"[{i}] {authors_str}. ({year}). {title}. {url}"
            citations.append(citation)
        
        return "\n".join(citations)

