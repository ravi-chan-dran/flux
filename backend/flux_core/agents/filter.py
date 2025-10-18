"""
Filter Agent - Quality Critic (The Evaluator)
Evaluates research quality and identifies issues.
"""

import json
import re
from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent
from flux_core.graph.state import ResearchState


class FilterAgent(BaseAgent):
    """
    The Filter evaluates research quality and identifies issues.
    
    Responsibilities:
    - Review hypotheses, sources, and experiments
    - Assign quality scores (0-10)
    - Identify specific issues and strengths
    - Provide constructive recommendations
    - Use filter/signal/noise metaphors
    """
    
    SYSTEM_PROMPT = """You are The Filter 🛡️, the guardian of research quality who separates signal from noise.

Your role is to critically evaluate all research components and identify issues that need improvement. You filter out weaknesses while acknowledging strengths.

Use filter, signal, and noise metaphors:
- "Filtering through the noise..."
- "The signal is clear in..."
- "Noise detected in..."
- "This passes through the quality filter..."
- "Blocking turbidity in..."

Evaluate these components:
1. HYPOTHESES: Are they clear, testable, and well-reasoned?
2. SOURCES: Are they relevant, recent, and comprehensive?
3. EXPERIMENTS: Are they rigorous, specific, and feasible?

Provide:
- QUALITY SCORE (0-10): Overall research quality
- ISSUES: Specific problems with each component
- STRENGTHS: What's working well
- RECOMMENDATIONS: Concrete suggestions for improvement

Be direct, constructive, and specific. Your critique drives improvement."""
    
    def __init__(self):
        """Initialize the Filter agent."""
        super().__init__(
            name="The Filter",
            emoji="🛡️",
            color="red",
            role="Quality Critic",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def review(self, state: ResearchState) -> dict[str, Any]:
        """
        Review the research state and provide quality critique.
        
        Args:
            state: Current research state with hypotheses, sources, experiments
        
        Returns:
            Critique dictionary with quality_score, issues, strengths, recommendations
        """
        question = state.get("question", "")
        hypotheses = state.get("hypotheses", [])
        sources = state.get("sources", [])
        experiments = state.get("experiments", [])
        iteration = state.get("iteration", 0)
        
        logger.info(f"{self.name} reviewing research (iteration {iteration})")
        logger.info(f"  Hypotheses: {len(hypotheses)}, Sources: {len(sources)}, "
                   f"Experiments: {len(experiments)}")
        
        # Build review prompt
        prompt = self._build_review_prompt(
            question, hypotheses, sources, experiments, iteration
        )
        
        try:
            response = await self.invoke_model(prompt, temperature=0.5)
            
            # Parse critique
            critique = self._parse_critique(response)
            
            # Ensure quality score is extracted
            if "quality_score" not in critique or critique["quality_score"] is None:
                critique["quality_score"] = self.calculate_quality_score(response)
            
            # Ensure issues are extracted
            if "issues" not in critique or not critique["issues"]:
                critique["issues"] = self.extract_issues(response)
            
            logger.info(f"{self.name} quality score: {critique['quality_score']:.1f}/10")
            logger.info(f"{self.name} identified {len(critique.get('issues', []))} issues")
            
            return critique
        
        except Exception as e:
            logger.error(f"{self.name} review failed: {e}")
            return self._fallback_critique()
    
    def _build_review_prompt(
        self,
        question: str,
        hypotheses: list[dict[str, Any]],
        sources: list[dict[str, Any]],
        experiments: list[dict[str, Any]],
        iteration: int,
    ) -> str:
        """Build the review prompt with all components."""
        hypotheses_text = self._format_hypotheses(hypotheses)
        sources_text = self._format_sources(sources)
        experiments_text = self._format_experiments(experiments)
        
        prompt = f"""Review this research for quality and identify issues:

Research Question: {question}
Iteration: {iteration}

HYPOTHESES ({len(hypotheses)}):
{hypotheses_text}

SOURCES ({len(sources)}):
{sources_text}

EXPERIMENTS ({len(experiments)}):
{experiments_text}

Provide a critique in JSON format:
{{
    "quality_score": <0-10>,
    "issues": [
        "Specific issue 1 with component",
        "Specific issue 2 with component"
    ],
    "strengths": [
        "What's working well 1",
        "What's working well 2"
    ],
    "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2"
    ]
}}

Be direct and constructive. Identify which components need improvement."""
        
        return prompt
    
    def _parse_critique(self, response: str) -> dict[str, Any]:
        """Parse critique from LLM response."""
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                critique = json.loads(json_match.group())
                
                # Validate and clean
                return {
                    "quality_score": float(critique.get("quality_score", 5.0)),
                    "issues": critique.get("issues", []),
                    "strengths": critique.get("strengths", []),
                    "recommendations": critique.get("recommendations", []),
                    "raw_critique": response,
                }
            
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse JSON critique: {e}")
        
        # Fallback: Extract from text
        return {
            "quality_score": self.calculate_quality_score(response),
            "issues": self.extract_issues(response),
            "strengths": self._extract_strengths(response),
            "recommendations": self._extract_recommendations(response),
            "raw_critique": response,
        }
    
    def calculate_quality_score(self, critique_text: str) -> float:
        """
        Extract numeric quality score from critique text.
        
        Args:
            critique_text: The critique text from LLM
        
        Returns:
            Quality score 0.0-10.0
        """
        # Look for patterns like "score: 7", "quality: 8/10", "7.5 out of 10"
        patterns = [
            r'quality[_\s]*score[:\s]*(\d+\.?\d*)',
            r'score[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:out of|/)\s*10',
            r'rate[:\s]*(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, critique_text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    # Normalize if needed
                    if score > 10:
                        score = score / 10
                    return min(10.0, max(0.0, score))
                except (ValueError, IndexError):
                    continue
        
        # Fallback: Sentiment-based scoring
        positive_words = ["excellent", "strong", "good", "solid", "clear", "rigorous"]
        negative_words = ["weak", "poor", "unclear", "vague", "lacking", "insufficient"]
        
        text_lower = critique_text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate based on sentiment
        if positive_count > negative_count:
            return 7.0
        elif negative_count > positive_count:
            return 4.0
        else:
            return 5.5
    
    def extract_issues(self, critique_text: str) -> list[str]:
        """
        Extract specific issues from critique text.
        
        Args:
            critique_text: The critique text from LLM
        
        Returns:
            List of issue strings
        """
        issues = []
        
        # Look for issues section
        issues_section = re.search(
            r'issues?[:\s]*(.*?)(?:strengths?|recommendations?|$)',
            critique_text,
            re.IGNORECASE | re.DOTALL
        )
        
        if issues_section:
            issues_text = issues_section.group(1)
            
            # Extract bullet points or numbered items
            issue_patterns = [
                r'[-•*]\s*(.+?)(?=\n[-•*]|\n\n|$)',
                r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
            ]
            
            for pattern in issue_patterns:
                matches = re.finditer(pattern, issues_text, re.MULTILINE)
                for match in matches:
                    issue = match.group(1).strip()
                    if len(issue) > 10:  # Filter out very short matches
                        issues.append(issue)
        
        # Fallback: Look for negative indicators
        if not issues:
            negative_patterns = [
                r'(hypotheses? (?:are|is) (?:unclear|weak|vague)[^.]*\.)',
                r'(sources? (?:are|is) (?:insufficient|limited|outdated)[^.]*\.)',
                r'(experiments? (?:are|is) (?:poorly|not) (?:designed|specified)[^.]*\.)',
            ]
            
            for pattern in negative_patterns:
                matches = re.finditer(pattern, critique_text, re.IGNORECASE)
                for match in matches:
                    issues.append(match.group(1).strip())
        
        return issues[:10]  # Limit to 10 issues
    
    def _extract_strengths(self, critique_text: str) -> list[str]:
        """Extract strengths from critique text."""
        strengths = []
        
        # Look for strengths section
        strengths_section = re.search(
            r'strengths?[:\s]*(.*?)(?:issues?|recommendations?|$)',
            critique_text,
            re.IGNORECASE | re.DOTALL
        )
        
        if strengths_section:
            strengths_text = strengths_section.group(1)
            
            # Extract bullet points or numbered items
            strength_patterns = [
                r'[-•*]\s*(.+?)(?=\n[-•*]|\n\n|$)',
                r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
            ]
            
            for pattern in strength_patterns:
                matches = re.finditer(pattern, strengths_text, re.MULTILINE)
                for match in matches:
                    strength = match.group(1).strip()
                    if len(strength) > 10:
                        strengths.append(strength)
        
        return strengths[:10]
    
    def _extract_recommendations(self, critique_text: str) -> list[str]:
        """Extract recommendations from critique text."""
        recommendations = []
        
        # Look for recommendations section
        rec_section = re.search(
            r'recommendations?[:\s]*(.*?)$',
            critique_text,
            re.IGNORECASE | re.DOTALL
        )
        
        if rec_section:
            rec_text = rec_section.group(1)
            
            # Extract bullet points or numbered items
            rec_patterns = [
                r'[-•*]\s*(.+?)(?=\n[-•*]|\n\n|$)',
                r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
            ]
            
            for pattern in rec_patterns:
                matches = re.finditer(pattern, rec_text, re.MULTILINE)
                for match in matches:
                    rec = match.group(1).strip()
                    if len(rec) > 10:
                        recommendations.append(rec)
        
        return recommendations[:10]
    
    def _fallback_critique(self) -> dict[str, Any]:
        """Generate minimal fallback critique."""
        return {
            "quality_score": 5.0,
            "issues": ["Review incomplete - evaluation error occurred"],
            "strengths": ["Research components present"],
            "recommendations": ["Complete evaluation needed"],
            "raw_critique": "Fallback critique due to error",
        }
    
    def _format_hypotheses(self, hypotheses: list[dict[str, Any]]) -> str:
        """Format hypotheses for prompt."""
        if not hypotheses:
            return "(None generated)"
        
        formatted = []
        for h in hypotheses:
            formatted.append(
                f"- {h.get('id', '?')}: {h.get('text', 'N/A')} "
                f"[Confidence: {h.get('confidence', 0)}%]"
            )
        return "\n".join(formatted)
    
    def _format_sources(self, sources: list[dict[str, Any]]) -> str:
        """Format sources for prompt."""
        if not sources:
            return "(None found)"
        
        formatted = []
        for i, s in enumerate(sources[:5], 1):  # Show top 5
            title = s.get("title", "Untitled")
            year = s.get("year", "N/A")
            source_type = s.get("source_type", "unknown")
            formatted.append(f"{i}. [{source_type}] {title} ({year})")
        
        if len(sources) > 5:
            formatted.append(f"... and {len(sources) - 5} more")
        
        return "\n".join(formatted)
    
    def _format_experiments(self, experiments: list[dict[str, Any]]) -> str:
        """Format experiments for prompt."""
        if not experiments:
            return "(None designed)"
        
        formatted = []
        for exp in experiments:
            hyp_id = exp.get("hypothesis_id", "?")
            method = exp.get("method", "N/A")[:150]
            formatted.append(f"- {hyp_id}: {method}...")
        
        return "\n".join(formatted)

