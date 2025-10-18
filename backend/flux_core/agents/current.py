"""
Current Agent - Hypothesis Generator (The Theorist)
Generates creative hypotheses and testable ideas using energy/current metaphors.
"""

import json
import re
from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent


class CurrentAgent(BaseAgent):
    """
    The Current generates creative hypotheses and testable ideas.
    
    Responsibilities:
    - Generate bold, innovative hypotheses on iteration 0
    - Refine existing hypotheses based on Filter critiques
    - Provide confidence ratings and reasoning
    - Suggest test approaches for each hypothesis
    - Use energy/current/spark metaphors
    """
    
    SYSTEM_PROMPT = """You are The Current 💡, the generator of creative hypotheses and innovative ideas.

Your role is to spark new theories and testable propositions that flow through the research system. You think boldly, creatively, and rigorously about possibilities.

Use energy, current, and spark metaphors:
- "A spark of insight suggests..."
- "The current of thought flows toward..."
- "Energy builds around the idea that..."
- "Charged with potential..."
- "A surge of understanding..."

For each hypothesis, provide:
1. Clear, testable statement
2. Confidence level (0-100) based on intuition and reasoning
3. Reasoning explaining the intuition and logic
4. Suggested test approach

On iteration 0: Generate 3-5 bold NEW hypotheses exploring different aspects of the question.
On later iterations: REFINE existing hypotheses based on critiques - improve clarity, adjust confidence, strengthen reasoning, or replace weak hypotheses with better ones.

Be creative but rigorous. Think like a theorist generating insights that experimenters can test."""
    
    def __init__(self):
        """Initialize the Current agent."""
        super().__init__(
            name="The Current",
            emoji="💡",
            color="cyan",
            role="Hypothesis Generator",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def generate_hypotheses(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        iteration: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Generate or refine hypotheses based on the research question.
        
        Args:
            question: The research question
            context: Optional context including critiques, sources, etc.
            iteration: Current iteration number (0 = first generation)
        
        Returns:
            List of hypothesis dictionaries with id, text, confidence, reasoning, test_approach
        """
        logger.info(f"{self.name} generating hypotheses (iteration {iteration})")
        
        if iteration == 0:
            # First iteration: Generate new hypotheses
            prompt = f"""Generate 3-5 bold, creative hypotheses for this research question:

Question: {question}

For each hypothesis, provide:
- id: A short identifier (h1, h2, etc.)
- text: Clear, testable hypothesis statement
- confidence: Confidence level 0-100
- reasoning: Why this hypothesis has potential
- test_approach: How to test this hypothesis

Format as a JSON array of hypothesis objects."""
        
        else:
            # Refinement iteration: Improve existing hypotheses
            existing_hypotheses = context.get("existing_hypotheses", []) if context else []
            critiques = context.get("critiques", []) if context else []
            
            hypotheses_text = self._format_hypotheses_for_prompt(existing_hypotheses)
            critiques_text = self._format_critiques_for_prompt(critiques)
            
            prompt = f"""Refine these hypotheses based on the critiques:

Original Question: {question}

Existing Hypotheses:
{hypotheses_text}

Critiques:
{critiques_text}

Refine the hypotheses by:
- Improving clarity and testability
- Adjusting confidence based on critique
- Strengthening reasoning
- Replacing weak hypotheses with better alternatives

Return the refined hypotheses in the same JSON format as before."""
        
        try:
            response = await self.invoke_model(prompt, context=context, temperature=0.8)
            
            # Parse hypotheses from response
            hypotheses = self._parse_hypotheses(response, iteration)
            
            logger.info(f"{self.name} generated {len(hypotheses)} hypotheses")
            return hypotheses
        
        except Exception as e:
            logger.error(f"{self.name} failed to generate hypotheses: {e}")
            # Return minimal hypotheses to continue flow
            return self._fallback_hypotheses(question, iteration)
    
    def _parse_hypotheses(self, response: str, iteration: int) -> list[dict[str, Any]]:
        """
        Parse hypotheses from LLM response.
        
        Tries JSON parsing first, falls back to text parsing.
        """
        # Try to extract JSON array
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                hypotheses = json.loads(json_match.group())
                
                # Validate and clean hypotheses
                cleaned = []
                for i, h in enumerate(hypotheses):
                    if isinstance(h, dict):
                        cleaned.append({
                            "id": h.get("id", f"h{i+1}"),
                            "text": h.get("text", "Hypothesis text"),
                            "confidence": min(100, max(0, int(h.get("confidence", 50)))),
                            "reasoning": h.get("reasoning", "Reasoning provided"),
                            "test_approach": h.get("test_approach", "Test approach needed"),
                            "iteration_generated": iteration,
                        })
                
                if cleaned:
                    return cleaned
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON hypotheses: {e}")
        
        # Fallback: Parse from text
        return self._parse_hypotheses_from_text(response, iteration)
    
    def _parse_hypotheses_from_text(self, text: str, iteration: int) -> list[dict[str, Any]]:
        """Parse hypotheses from unstructured text."""
        hypotheses = []
        
        # Look for numbered items or hypothesis patterns
        hypothesis_pattern = r'(?:Hypothesis|H)[\s]*(\d+)[:\s]*(.*?)(?=(?:Hypothesis|H)[\s]*\d+|$)'
        matches = re.finditer(hypothesis_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(matches):
            hyp_num = match.group(1)
            hyp_text = match.group(2).strip()
            
            # Extract confidence if present
            confidence = 50
            conf_match = re.search(r'confidence[:\s]*(\d+)', hyp_text, re.IGNORECASE)
            if conf_match:
                confidence = int(conf_match.group(1))
            
            hypotheses.append({
                "id": f"h{hyp_num}",
                "text": hyp_text[:200],  # Truncate if too long
                "confidence": min(100, max(0, confidence)),
                "reasoning": "Parsed from response",
                "test_approach": "See full hypothesis text",
                "iteration_generated": iteration,
            })
        
        # If no matches, create a single hypothesis
        if not hypotheses and text.strip():
            hypotheses.append({
                "id": "h1",
                "text": text[:200],
                "confidence": 50,
                "reasoning": "Generated hypothesis",
                "test_approach": "Requires experimental design",
                "iteration_generated": iteration,
            })
        
        return hypotheses
    
    def _fallback_hypotheses(self, question: str, iteration: int) -> list[dict[str, Any]]:
        """Generate minimal fallback hypotheses if LLM fails."""
        return [
            {
                "id": "h1",
                "text": f"Hypothesis related to: {question[:100]}",
                "confidence": 50,
                "reasoning": "Fallback hypothesis due to generation error",
                "test_approach": "Experimental validation needed",
                "iteration_generated": iteration,
            }
        ]
    
    def _format_hypotheses_for_prompt(self, hypotheses: list[dict[str, Any]]) -> str:
        """Format hypotheses for inclusion in prompts."""
        if not hypotheses:
            return "(No existing hypotheses)"
        
        formatted = []
        for h in hypotheses:
            formatted.append(
                f"- {h.get('id', '?')}: {h.get('text', 'N/A')} "
                f"(confidence: {h.get('confidence', 0)})"
            )
        
        return "\n".join(formatted)
    
    def _format_critiques_for_prompt(self, critiques: list[dict[str, Any]]) -> str:
        """Format critiques for inclusion in prompts."""
        if not critiques:
            return "(No critiques yet)"
        
        # Get the most recent critique
        if critiques:
            latest = critiques[-1]
            issues = latest.get("issues", [])
            
            # Filter for hypothesis-related issues
            hyp_issues = [
                issue for issue in issues
                if isinstance(issue, str) and 
                ("hypothesis" in issue.lower() or "hypotheses" in issue.lower())
            ]
            
            if hyp_issues:
                return "\n".join(f"- {issue}" for issue in hyp_issues)
        
        return "(No specific hypothesis critiques)"

