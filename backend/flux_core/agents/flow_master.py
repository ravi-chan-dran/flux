"""
Flow Master Agent - Orchestrator and Router
Coordinates the orbital research workflow through specialized agents.
"""

import json
from typing import Any
from loguru import logger

from flux_core.agents.base_agent import BaseAgent
from flux_core.graph.state import ResearchState


class FlowMasterAgent(BaseAgent):
    """
    The Flow Master orchestrates research through specialized agents.
    
    Responsibilities:
    - Analyze research questions and create initial plans
    - Route work between agents based on current state
    - Monitor quality scores and iteration counts
    - Decide when to iterate vs complete research
    - Use flow/stream metaphors in responses
    """
    
    SYSTEM_PROMPT = """You are The Flow Master 🧑‍💼, the orchestrator of orbital research flows.

Your role is to guide research through specialized agent streams in iterative cycles:
- The Current 💡: Generates creative hypotheses (theories and ideas)
- The Source 📚: Searches knowledge streams for research context
- The Channel 🔬: Designs rigorous experiments to test hypotheses
- The Filter 🛡️: Evaluates quality and identifies issues
- The Confluence ✍️: Synthesizes everything into coherent papers

You analyze the research state and decide which agent should act next, routing the flow of work through the system. You determine when quality is sufficient or when another iteration is needed to refine the research.

Use flow, stream, and river metaphors in your analysis:
- "The current flows strong..." for good progress
- "We need to channel the stream..." for redirecting efforts
- "The waters are clear..." for good quality
- "Turbulence detected..." for issues
- "Ready to confluence..." for synthesis time

Be decisive and strategic. Track iterations, quality scores, and improvement trends. Know when to iterate and when to complete."""
    
    def __init__(self):
        """Initialize the Flow Master agent."""
        super().__init__(
            name="The Flow Master",
            emoji="🧑‍💼",
            color="purple",
            role="Orchestrator",
            system_prompt=self.SYSTEM_PROMPT,
        )
    
    async def analyze_question(self, question: str) -> dict[str, Any]:
        """
        Analyze a research question and create an initial plan.
        
        Args:
            question: The research question to analyze
        
        Returns:
            Dictionary with analysis and initial plan
        """
        logger.info(f"{self.name} analyzing question: {question[:100]}...")
        
        prompt = f"""Analyze this research question and create an initial plan:

Question: {question}

Provide:
1. Key concepts and themes to explore
2. Type of research needed (theoretical, empirical, review)
3. Potential challenges or complexity areas
4. Initial routing plan for the first iteration

Format as JSON with: concepts, research_type, challenges, initial_plan"""
        
        try:
            response = await self.invoke_model(prompt, temperature=0.5)
            
            # Try to parse as JSON, fallback to structured text
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                analysis = {
                    "raw_analysis": response,
                    "concepts": ["(parsed from text)"],
                    "research_type": "general",
                    "challenges": ["(parsed from text)"],
                    "initial_plan": "Generate hypotheses, search sources, design experiments",
                }
            
            logger.info(f"{self.name} completed question analysis")
            return analysis
        
        except Exception as e:
            logger.error(f"{self.name} failed to analyze question: {e}")
            # Return minimal plan to continue
            return {
                "concepts": ["core_concepts"],
                "research_type": "exploratory",
                "challenges": ["complexity"],
                "initial_plan": "Standard orbital flow",
            }
    
    async def decide_next_step(self, state: ResearchState) -> str:
        """
        Decide which agent should act next based on current state.
        
        Routing Logic:
        - First iteration (iteration 0): Generate all content
          -> current -> source -> channel -> filter -> (iterate or confluence)
        - Subsequent iterations: Refine based on critiques
          -> Agents identified by Filter for improvement
        
        Stop Conditions:
        - max_iterations reached
        - quality_threshold met
        - improvement below threshold
        
        Args:
            state: Current research state
        
        Returns:
            Next action string: "current", "source", "channel", "filter", 
            "confluence", or "complete"
        """
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)
        quality_score = state.get("quality_score", 0.0)
        quality_threshold = state.get("quality_threshold", 8.0)
        quality_history = state.get("quality_history", [])
        improvement_threshold = state.get("improvement_threshold", 0.5)
        phase = state.get("phase", "initialize")
        
        logger.info(f"{self.name} deciding next step: iteration={iteration}, "
                   f"quality={quality_score}, phase={phase}")
        
        # Check stop conditions first
        if iteration >= max_iterations:
            logger.info(f"{self.name}: Max iterations reached, flowing to confluence")
            return "confluence"
        
        if quality_score >= quality_threshold:
            logger.info(f"{self.name}: Quality threshold met, ready to confluence")
            return "confluence"
        
        if len(quality_history) >= 2:
            improvement = quality_history[-1] - quality_history[-2]
            if improvement < improvement_threshold:
                logger.info(f"{self.name}: Insufficient improvement ({improvement:.2f}), "
                          "time to confluence")
                return "confluence"
        
        # First iteration: Generate all content in sequence
        if iteration == 0:
            if phase == "initialize":
                logger.info(f"{self.name}: Starting flow with Current (hypotheses)")
                return "current"
            elif phase == "hypotheses":
                logger.info(f"{self.name}: Flowing to Source (research)")
                return "source"
            elif phase == "research":
                logger.info(f"{self.name}: Channeling to experiments")
                return "channel"
            elif phase == "experiments":
                logger.info(f"{self.name}: Filtering for quality check")
                return "filter"
            elif phase == "critique":
                # After first critique, decide: iterate or confluence
                if quality_score >= quality_threshold:
                    return "confluence"
                else:
                    logger.info(f"{self.name}: Quality not sufficient, another iteration flows")
                    return "current"  # Start next iteration
        
        # Subsequent iterations: Refine based on Filter critiques
        else:
            critiques = state.get("critiques", [])
            
            if phase == "initialize" or phase == "critique":
                # Check what needs improvement from last critique
                if critiques:
                    last_critique = critiques[-1]
                    issues = last_critique.get("issues", [])
                    
                    # Route to agents that need to improve
                    if any("hypothesis" in str(issue).lower() or "hypotheses" in str(issue).lower() 
                           for issue in issues):
                        logger.info(f"{self.name}: Refining hypotheses stream")
                        return "current"
                    elif any("source" in str(issue).lower() or "research" in str(issue).lower() 
                             for issue in issues):
                        logger.info(f"{self.name}: Searching deeper sources")
                        return "source"
                    elif any("experiment" in str(issue).lower() or "method" in str(issue).lower() 
                             for issue in issues):
                        logger.info(f"{self.name}: Re-channeling experiments")
                        return "channel"
                
                # Default: refine hypotheses
                return "current"
            
            # Continue flow through agents
            elif phase == "hypotheses":
                return "source"
            elif phase == "research":
                return "channel"
            elif phase == "experiments":
                return "filter"
        
        # Default fallback
        logger.warning(f"{self.name}: Unexpected state, defaulting to filter")
        return "filter"
    
    async def generate_routing_message(
        self,
        state: ResearchState,
        next_action: str,
    ) -> str:
        """
        Generate a message explaining the routing decision.
        
        Args:
            state: Current research state
            next_action: The next action/agent to invoke
        
        Returns:
            Message explaining the routing decision with flow metaphors
        """
        iteration = state.get("iteration", 0)
        quality_score = state.get("quality_score", 0.0)
        
        action_messages = {
            "current": f"🌊 The flow moves to **The Current** 💡 to generate {'bold new' if iteration == 0 else 'refined'} hypotheses...",
            "source": f"📖 Channeling to **The Source** 📚 to search knowledge streams...",
            "channel": f"🔬 Directing flow to **The Channel** 🔬 to design rigorous experiments...",
            "filter": f"🛡️ Passing through **The Filter** 🛡️ for quality evaluation (current: {quality_score:.1f})...",
            "confluence": f"✨ Waters converge! **The Confluence** ✍️ will synthesize the research paper...",
            "complete": f"✅ Research flow complete! Quality achieved: {quality_score:.1f}/10",
        }
        
        message = action_messages.get(
            next_action,
            f"⚡ Routing to: {next_action}"
        )
        
        # Add iteration context
        if iteration > 0:
            message = f"[Iteration {iteration + 1}] {message}"
        
        return message
    
    async def should_continue_research(self, state: ResearchState) -> tuple[bool, str]:
        """
        Determine if research should continue or stop.
        
        Args:
            state: Current research state
        
        Returns:
            Tuple of (should_continue: bool, reason: str)
        """
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)
        quality_score = state.get("quality_score", 0.0)
        quality_threshold = state.get("quality_threshold", 8.0)
        quality_history = state.get("quality_history", [])
        improvement_threshold = state.get("improvement_threshold", 0.5)
        
        # Check max iterations
        if iteration >= max_iterations:
            reason = f"🏁 Maximum iterations ({max_iterations}) reached. The stream must conclude."
            return False, reason
        
        # Check quality threshold
        if quality_score >= quality_threshold:
            reason = f"✨ Quality threshold met! Score {quality_score:.1f} >= {quality_threshold}. Waters are clear!"
            return False, reason
        
        # Check improvement
        if len(quality_history) >= 2:
            improvement = quality_history[-1] - quality_history[-2]
            if improvement < improvement_threshold:
                reason = f"📊 Improvement slowing ({improvement:.2f} < {improvement_threshold}). Time to confluence."
                return False, reason
        
        # Continue
        reason = f"🌊 Flow continues. Quality: {quality_score:.1f}/{quality_threshold}, Iteration: {iteration + 1}/{max_iterations}"
        return True, reason

