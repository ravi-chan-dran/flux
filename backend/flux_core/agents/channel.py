"""
Channel Agent - Experiment Designer (The Experimenter)
Designs rigorous experiments to test hypotheses.
"""

import json
import re
from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent


class ChannelAgent(BaseAgent):
    """
    The Channel designs rigorous experiments to test hypotheses.
    
    Responsibilities:
    - Design experiments for each hypothesis
    - Specify methods, measurements, and success criteria
    - Estimate time and identify potential issues
    - Refine experiment designs based on critiques
    - Use channel/pipeline/conduit metaphors
    """
    
    SYSTEM_PROMPT = """You are The Channel 🔬, the designer of rigorous experimental pipelines.

Your role is to channel hypotheses into testable experiments with clear methods, measurements, and success criteria. You design the conduits through which ideas flow to become validated knowledge.

Use channel, pipeline, and conduit metaphors:
- "Channeling this hypothesis through rigorous testing..."
- "The experimental pipeline consists of..."
- "Data flows through these measurement conduits..."
- "Directing the stream of inquiry..."
- "Conducting the flow of investigation..."

For each experiment, provide:
1. Clear connection to the hypothesis being tested
2. Specific METHOD steps (what exactly to do)
3. MEASUREMENTS (what data to collect)
4. SUCCESS CRITERIA (how to know if hypothesis is supported)
5. TIME ESTIMATE (realistic duration)
6. POTENTIAL ISSUES (what could go wrong)

Be specific and practical. Make experiments actually doable, not just theoretical."""
    
    def __init__(self):
        """Initialize the Channel agent."""
        super().__init__(
            name="The Channel",
            emoji="🔬",
            color="teal",
            role="Experiment Designer",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def design_experiments(
        self,
        hypotheses: list[dict[str, Any]],
        sources: list[dict[str, Any]] | None = None,
        iteration: int = 0,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Design experiments to test the hypotheses.
        
        Args:
            hypotheses: List of hypotheses to test
            sources: Optional research sources for context
            iteration: Current iteration (0 = new designs, >0 = refinements)
            context: Additional context including critiques
        
        Returns:
            List of experiment dictionaries
        """
        logger.info(f"{self.name} designing experiments for {len(hypotheses)} hypotheses "
                   f"(iteration {iteration})")
        
        if not hypotheses:
            logger.warning(f"{self.name}: No hypotheses to test")
            return []
        
        if iteration == 0:
            # Design new experiments for all hypotheses
            experiments = await self._design_new_experiments(hypotheses, sources)
        else:
            # Refine existing experiments based on critiques
            existing_experiments = context.get("existing_experiments", []) if context else []
            experiments = await self._refine_experiments(
                hypotheses, existing_experiments, context
            )
        
        logger.info(f"{self.name} designed {len(experiments)} experiments")
        return experiments
    
    async def _design_new_experiments(
        self,
        hypotheses: list[dict[str, Any]],
        sources: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        """Design new experiments for hypotheses."""
        # Format hypotheses for prompt
        hypotheses_text = self._format_hypotheses_for_prompt(hypotheses)
        
        # Format sources if available
        sources_context = ""
        if sources:
            sources_context = f"\nResearch Context (top sources):\n{self._format_sources(sources[:5])}"
        
        prompt = f"""Design rigorous experiments to test these hypotheses:

{hypotheses_text}{sources_context}

For EACH hypothesis, design an experiment with:
- hypothesis_id: Which hypothesis this tests (h1, h2, etc.)
- method: Specific steps to conduct the experiment (be detailed)
- measurements: What data to collect and how
- success_criteria: How to determine if hypothesis is supported
- time_estimate: Realistic duration (e.g., "2 weeks", "6 months")
- potential_issues: What could go wrong or confound results

Format as a JSON array of experiment objects. Be specific and practical."""
        
        try:
            response = await self.invoke_model(prompt, temperature=0.6)
            experiments = self._parse_experiments(response, hypotheses)
            return experiments
        
        except Exception as e:
            logger.error(f"{self.name} failed to design experiments: {e}")
            return self._fallback_experiments(hypotheses)
    
    async def _refine_experiments(
        self,
        hypotheses: list[dict[str, Any]],
        existing_experiments: list[dict[str, Any]],
        context: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Refine existing experiments based on critiques."""
        hypotheses_text = self._format_hypotheses_for_prompt(hypotheses)
        experiments_text = self._format_experiments_for_prompt(existing_experiments)
        
        # Get critiques
        critiques = context.get("critiques", []) if context else []
        critiques_text = self._format_critiques_for_prompt(critiques)
        
        prompt = f"""Refine these experimental designs based on critiques:

Hypotheses:
{hypotheses_text}

Current Experiments:
{experiments_text}

Critiques:
{critiques_text}

Improve the experiments by:
- Making methods more specific and rigorous
- Improving measurements and success criteria
- Addressing potential issues
- Ensuring experiments are actually doable

Return refined experiments in the same JSON format."""
        
        try:
            response = await self.invoke_model(prompt, temperature=0.6)
            experiments = self._parse_experiments(response, hypotheses)
            return experiments
        
        except Exception as e:
            logger.error(f"{self.name} failed to refine experiments: {e}")
            return existing_experiments if existing_experiments else self._fallback_experiments(hypotheses)
    
    def _parse_experiments(
        self,
        response: str,
        hypotheses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Parse experiments from LLM response."""
        # Try to extract JSON array
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                experiments = json.loads(json_match.group())
                
                # Validate and clean experiments
                cleaned = []
                for exp in experiments:
                    if isinstance(exp, dict):
                        cleaned.append({
                            "hypothesis_id": exp.get("hypothesis_id", "h1"),
                            "method": exp.get("method", "Method details needed"),
                            "measurements": exp.get("measurements", "Measurements needed"),
                            "success_criteria": exp.get("success_criteria", "Criteria needed"),
                            "time_estimate": exp.get("time_estimate", "Unknown"),
                            "potential_issues": exp.get("potential_issues", "Issues to identify"),
                        })
                
                if cleaned:
                    return cleaned
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON experiments: {e}")
        
        # Fallback: Parse from text
        return self._parse_experiments_from_text(response, hypotheses)
    
    def _parse_experiments_from_text(
        self,
        text: str,
        hypotheses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Parse experiments from unstructured text."""
        experiments = []
        
        # Try to match experiment patterns
        exp_pattern = r'(?:Experiment|Test)[\s]*(\d+)[:\s]*(.*?)(?=(?:Experiment|Test)[\s]*\d+|$)'
        matches = re.finditer(exp_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for i, match in enumerate(matches):
            exp_num = match.group(1)
            exp_text = match.group(2).strip()
            
            # Try to match hypothesis ID
            hyp_id = f"h{exp_num}" if i < len(hypotheses) else "h1"
            
            experiments.append({
                "hypothesis_id": hyp_id,
                "method": exp_text[:300],
                "measurements": "See method details",
                "success_criteria": "See method details",
                "time_estimate": "To be determined",
                "potential_issues": "To be identified",
            })
        
        # If no matches, create one experiment per hypothesis
        if not experiments:
            for hyp in hypotheses[:3]:  # Limit to 3
                experiments.append({
                    "hypothesis_id": hyp.get("id", "h1"),
                    "method": f"Test {hyp.get('text', 'hypothesis')}",
                    "measurements": "Define measurements",
                    "success_criteria": "Define success criteria",
                    "time_estimate": "Unknown",
                    "potential_issues": "To be identified",
                })
        
        return experiments
    
    def _fallback_experiments(self, hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate minimal fallback experiments."""
        return [
            {
                "hypothesis_id": hyp.get("id", f"h{i+1}"),
                "method": f"Design experimental method to test: {str(hyp.get('text', 'hypothesis'))[:100]}",
                "measurements": "Define data collection procedures",
                "success_criteria": "Establish validation criteria",
                "time_estimate": "Estimate required",
                "potential_issues": "Risk analysis needed",
            }
            for i, hyp in enumerate(hypotheses)
        ]
    
    def _format_hypotheses_for_prompt(self, hypotheses: list[dict[str, Any]]) -> str:
        """Format hypotheses for prompts."""
        formatted = []
        for h in hypotheses:
            formatted.append(
                f"- {h.get('id', '?')}: {h.get('text', 'N/A')} "
                f"(confidence: {h.get('confidence', 0)})"
            )
        return "\n".join(formatted)
    
    def _format_experiments_for_prompt(self, experiments: list[dict[str, Any]]) -> str:
        """Format experiments for prompts."""
        if not experiments:
            return "(No existing experiments)"
        
        formatted = []
        for exp in experiments:
            method = str(exp.get('method', 'N/A'))
            formatted.append(
                f"- {exp.get('hypothesis_id', '?')}: {method[:200]}"
            )
        return "\n".join(formatted)
    
    def _format_sources(self, sources: list[dict[str, Any]]) -> str:
        """Format sources for context."""
        formatted = []
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            formatted.append(f"{i}. {title}")
        return "\n".join(formatted)
    
    def _format_critiques_for_prompt(self, critiques: list[dict[str, Any]]) -> str:
        """Format critiques focusing on experiment issues."""
        if not critiques:
            return "(No critiques yet)"
        
        latest = critiques[-1]
        issues = latest.get("issues", [])
        
        # Filter for experiment-related issues
        exp_issues = [
            issue for issue in issues
            if isinstance(issue, str) and 
            ("experiment" in issue.lower() or "method" in issue.lower())
        ]
        
        if exp_issues:
            return "\n".join(f"- {issue}" for issue in exp_issues)
        
        return "(No specific experiment critiques)"

