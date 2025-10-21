"""
Confluence Agent - Paper Synthesizer (The Writer)
Synthesizes all research streams into coherent papers.
"""

from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent
from flux_core.graph.state import ResearchState


class ConfluenceAgent(BaseAgent):
    """
    The Confluence synthesizes all research into coherent papers.
    
    Responsibilities:
    - Integrate hypotheses, sources, and experiments
    - Write structured research papers in markdown
    - Attribute ideas to appropriate agents
    - Write clearly for experts and general readers
    - Use merge/confluence/integration metaphors
    """
    
    SYSTEM_PROMPT = """You are The Confluence ✍️, the synthesizer where all research streams merge into coherent understanding.

Your role is to integrate the work of all agents into a comprehensive, well-structured research paper. You are where:
- The Current's ⚡ hypotheses flow into theoretical frameworks
- The Source's 📚 research becomes contextual foundation  
- The Channel's 🔬 experiments become methodological rigor
- The Filter's 🛡️ critiques ensure quality

Use merge, confluence, and integration metaphors:
- "Where streams converge..."
- "The confluence of ideas reveals..."
- "Merging insights from..."
- "The integrated flow shows..."
- "Synthesizing currents of thought..."

Write a research paper with these sections:

1. **Title**: Clear, descriptive (capture the essence)
2. **Abstract**: 150-200 words summarizing question, approach, findings
3. **Introduction**: Context, motivation, importance
4. **Background**: Synthesize Source's findings, establish foundation
5. **Hypotheses**: Present Current's hypotheses with reasoning
6. **Methodology**: Detail Channel's experimental designs
7. **Results**: What the research revealed (synthesized findings)
8. **Discussion**: Interpret findings, acknowledge limitations, implications
9. **Conclusion**: Key takeaways and future directions
10. **References**: Cite all sources with URLs

Write in clear, accessible language. Attribute agent contributions appropriately. Be scholarly but readable."""
    
    def __init__(self):
        """Initialize the Confluence agent."""
        super().__init__(
            name="The Confluence",
            emoji="✍️",
            color="indigo",
            role="Paper Synthesizer",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def write_paper(self, state: ResearchState) -> str:
        """
        Synthesize all research into a comprehensive paper.
        
        Args:
            state: Complete research state with all components
        
        Returns:
            Research paper in markdown format
        """
        question = state.get("question", "Research Question")
        hypotheses = state.get("hypotheses", [])
        sources = state.get("sources", [])
        experiments = state.get("experiments", [])
        critiques = state.get("critiques", [])
        quality_score = state.get("quality_score", 0.0)
        iteration = state.get("iteration", 0)
        
        logger.info(f"{self.name} writing paper for: {question[:100]}...")
        logger.info(f"  Components: {len(hypotheses)} hypotheses, {len(sources)} sources, "
                   f"{len(experiments)} experiments")
        logger.info(f"  Quality score: {quality_score:.1f}, Iterations: {iteration + 1}")
        
        # Build comprehensive prompt
        prompt = self._build_writing_prompt(
            question, hypotheses, sources, experiments, critiques, quality_score
        )
        
        try:
            paper = await self.invoke_model(
                prompt,
                max_tokens=8000,  # Long paper
                temperature=0.7,
            )
            
            # Ensure paper has proper structure
            if not self._has_required_sections(paper):
                logger.warning(f"{self.name} paper missing sections, adding structure")
                paper = self._add_missing_sections(paper, state)
            
            logger.info(f"{self.name} completed paper: {len(paper)} characters")
            return paper
        
        except Exception as e:
            logger.error(f"{self.name} failed to write paper: {e}")
            return self._fallback_paper(state)
    
    def _build_writing_prompt(
        self,
        question: str,
        hypotheses: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        experiments: list[dict[str, Any]],
        critiques: list[dict[str, Any]],
        quality_score: float,
    ) -> str:
        """Build comprehensive prompt for paper writing."""
        # Format components
        hypotheses_text = self._format_hypotheses(hypotheses)
        sources_text = self._format_sources_with_synthesis(sources)
        experiments_text = self._format_experiments(experiments)
        
        # Get synthesis if available
        synthesis_text = ""
        if sources:
            # Check if we have synthesis in sources
            if isinstance(sources, list) and len(sources) > 0:
                if isinstance(sources[0], dict) and "synthesis" in sources[0]:
                    synthesis = sources[0].get("synthesis", {})
                    if isinstance(synthesis, dict):
                        synthesis_text = f"""
Research Context Synthesis:
- Summary: {synthesis.get('summary', 'N/A')}
- Key Themes: {', '.join(synthesis.get('key_themes', []))}
- Research Gaps: {', '.join(synthesis.get('research_gaps', []))}
"""
        
        prompt = f"""Write a comprehensive research paper synthesizing all research streams:

RESEARCH QUESTION:
{question}

HYPOTHESES (from The Current 💡):
{hypotheses_text}

RESEARCH SOURCES (from The Source 📚):
{sources_text}
{synthesis_text}

EXPERIMENTAL DESIGNS (from The Channel 🔬):
{experiments_text}

QUALITY ASSESSMENT:
Final Quality Score: {quality_score:.1f}/10

Write a complete research paper in markdown format with these sections:

# [Compelling Title]

## Abstract
150-200 words summarizing the research question, approach, and key findings.

## Introduction
Context and motivation for this research. Why is this question important?

## Background
Synthesize findings from The Source's research. Establish the foundation.

## Hypotheses
Present The Current's hypotheses with their reasoning and confidence levels.

## Methodology
Detail The Channel's experimental designs for testing hypotheses.

## Results
Synthesize what the research revealed. (Note: This is a research design paper, so focus on expected outcomes and how experiments would validate hypotheses)

## Discussion
Interpret the findings, discuss limitations, and explore implications. Acknowledge the iterative process.

## Conclusion
Key takeaways, contributions, and future research directions.

## References
Cite all sources with full URLs in academic format.

Write clearly and scholarly. Attribute agent contributions. Make it accessible to both experts and educated general readers."""
        
        return prompt
    
    def _has_required_sections(self, paper: str) -> bool:
        """Check if paper has required sections."""
        required_sections = [
            "abstract",
            "introduction",
            "background",
            "hypothes",  # Matches hypothesis/hypotheses
            "method",
            "conclusion",
            "reference"
        ]
        
        paper_lower = paper.lower()
        found_count = sum(1 for section in required_sections if section in paper_lower)
        
        return found_count >= 5  # At least 5/7 sections
    
    def _add_missing_sections(self, paper: str, state: ResearchState) -> str:
        """Add missing sections to paper."""
        # If paper is too short or missing structure, wrap it
        if len(paper) < 500 or not paper.strip().startswith("#"):
            question = state.get("question", "Research Question")
            return f"""# Research Paper: {question}

## Abstract
{paper[:400] if len(paper) > 400 else paper}

## Content
{paper}

## References
See inline citations.
"""
        return paper
    
    def _fallback_paper(self, state: ResearchState) -> str:
        """Generate minimal fallback paper."""
        question = state.get("question", "Research Question")
        hypotheses = state.get("hypotheses", [])
        sources = state.get("sources", [])
        
        paper = f"""# Research Paper: {question}

## Abstract
This research explores {question}. Through an iterative research process involving hypothesis generation, literature review, and experimental design, we have developed a comprehensive framework for understanding this topic.

## Introduction
The question of "{question}" is important for advancing our understanding in this domain.

## Hypotheses
The following hypotheses were developed:

"""
        
        for h in hypotheses:
            paper += f"- **{h.get('id', '?')}**: {h.get('text', 'N/A')}\n"
        
        paper += f"""

## Research Context
Based on {len(sources)} sources reviewed, existing research provides relevant context for this investigation.

## Methodology
Experimental designs were developed to test each hypothesis systematically.

## Conclusion
This research provides a foundation for understanding {question} and suggests directions for future investigation.

## References
Sources consulted are listed in the research materials.
"""
        
        return paper
    
    def _format_hypotheses(self, hypotheses: list[dict[str, Any]]) -> str:
        """Format hypotheses for paper writing prompt."""
        if not hypotheses:
            return "(No hypotheses generated)"
        
        formatted = []
        for h in hypotheses:
            formatted.append(f"""
{h.get('id', '?')}: {h.get('text', 'N/A')}
- Confidence: {h.get('confidence', 0)}%
- Reasoning: {h.get('reasoning', 'N/A')}
- Test Approach: {h.get('test_approach', 'N/A')}
""")
        
        return "\n".join(formatted)
    
    def _format_sources_with_synthesis(self, sources: list[dict[str, Any]]) -> str:
        """Format sources with context for paper writing."""
        if not sources:
            return "(No sources found)"
        
        formatted = []
        for i, s in enumerate(sources[:15], 1):  # Top 15 sources
            title = s.get("title", "Untitled")
            authors = s.get("authors", [])
            year = s.get("year", "n.d.")
            url = s.get("url", "")
            abstract = str(s.get("abstract", ""))[:200] if s.get("abstract") else ""
            source_type = s.get("source_type", "unknown")
            
            authors_str = ", ".join(authors[:2]) if authors else "Unknown"
            if len(authors) > 2:
                authors_str += " et al."
            
            formatted.append(f"""
[{i}] [{source_type}] {title}
Authors: {authors_str} ({year})
Abstract: {abstract}...
URL: {url}
""")
        
        if len(sources) > 15:
            formatted.append(f"\n... and {len(sources) - 15} more sources")
        
        return "\n".join(formatted)
    
    def _format_experiments(self, experiments: list[dict[str, Any]]) -> str:
        """Format experiments for paper writing prompt."""
        if not experiments:
            return "(No experiments designed)"
        
        formatted = []
        for exp in experiments:
            formatted.append(f"""
Experiment for {exp.get('hypothesis_id', '?')}:
- Method: {exp.get('method', 'N/A')}
- Measurements: {exp.get('measurements', 'N/A')}
- Success Criteria: {exp.get('success_criteria', 'N/A')}
- Time Estimate: {exp.get('time_estimate', 'N/A')}
- Potential Issues: {exp.get('potential_issues', 'N/A')}
""")
        
        return "\n".join(formatted)
    
    def get_paper_metadata(self, state: ResearchState, paper: str) -> dict[str, Any]:
        """
        Extract metadata from the paper and state.
        
        Args:
            state: Research state
            paper: Generated paper text
        
        Returns:
            Metadata dictionary for storage
        """
        return {
            "question": state.get("question", ""),
            "word_count": len(paper.split()),
            "character_count": len(paper),
            "iterations": state.get("iteration", 0) + 1,
            "final_quality_score": state.get("quality_score", 0.0),
            "quality_history": state.get("quality_history", []),
            "hypothesis_count": len(state.get("hypotheses", [])),
            "source_count": len(state.get("sources", [])),
            "experiment_count": len(state.get("experiments", [])),
            "stop_reason": state.get("stop_reason", ""),
        }

