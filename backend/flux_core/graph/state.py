"""
LangGraph State Definition for FLUX Orbital Research Flow
"""

import os
from datetime import datetime
from typing import TypedDict, Any
from loguru import logger


class ResearchState(TypedDict, total=False):
    """
    State dictionary for the FLUX orbital research workflow.
    
    This state is passed between agents in the LangGraph flow,
    tracking the entire research lifecycle from hypothesis generation
    through iterative refinement to final paper generation.
    """
    
    # Core Question
    question: str  # The research question to investigate
    research_id: str  # Unique identifier for this research session
    
    # Iteration Control
    iteration: int  # Current iteration number (0-indexed)
    max_iterations: int  # Maximum allowed iterations
    quality_score: float  # Current quality score (0-10)
    quality_threshold: float  # Minimum quality score to stop iteration
    quality_history: list[float]  # History of quality scores across iterations
    improvement_threshold: float  # Minimum improvement required to continue
    
    # Workflow State
    phase: str  # Current phase: hypothesis, research, experiment, critique, write
    next_action: str  # Routing decision for next step
    should_iterate: bool  # Whether to continue iterating
    stop_reason: str  # Reason for stopping iteration
    
    # Research Content
    hypotheses: list[dict[str, Any]]  # Generated research hypotheses
    sources: list[dict[str, Any]]  # Gathered research sources (papers, articles)
    experiments: list[dict[str, Any]]  # Designed experiments or analysis plans
    critiques: list[dict[str, Any]]  # Critical evaluations and feedback
    paper_draft: str  # Current draft of the research paper
    
    # Communication
    messages: list[dict[str, Any]]  # Conversation log for debugging and tracking
    
    # Metrics
    started_at: str  # ISO timestamp when research started
    total_tokens_used: int  # Total tokens consumed by LLM calls
    total_cost: float  # Estimated cost in USD


def create_initial_state(
    question: str,
    research_id: str,
    max_iterations: int | None = None,
    quality_threshold: float | None = None,
    improvement_threshold: float | None = None,
) -> ResearchState:
    """
    Create an initial research state with default values.
    
    Args:
        question: The research question to investigate
        research_id: Unique identifier for this research session
        max_iterations: Maximum iterations (defaults to env var MAX_ITERATIONS or 1)
        quality_threshold: Quality threshold (defaults to env var QUALITY_THRESHOLD or 8.0)
        improvement_threshold: Improvement threshold (defaults to env var IMPROVEMENT_THRESHOLD or 0.5)
    
    Returns:
        Initialized ResearchState dictionary
    """
    
    # Read configuration from environment variables with fallbacks
    if max_iterations is None:
        max_iterations = int(os.getenv("MAX_ITERATIONS", "1"))
    
    if quality_threshold is None:
        quality_threshold = float(os.getenv("QUALITY_THRESHOLD", "8.0"))
    
    if improvement_threshold is None:
        improvement_threshold = float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5"))
    
    logger.info(f"Creating initial state for research: {research_id}")
    logger.info(f"Question: {question}")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info(f"Quality threshold: {quality_threshold}")
    logger.info(f"Improvement threshold: {improvement_threshold}")
    
    state: ResearchState = {
        # Core
        "question": question,
        "research_id": research_id,
        
        # Iteration control
        "iteration": 0,
        "max_iterations": max_iterations,
        "quality_score": 0.0,
        "quality_threshold": quality_threshold,
        "quality_history": [],
        "improvement_threshold": improvement_threshold,
        
        # Workflow
        "phase": "initialize",
        "next_action": "generate_hypotheses",
        "should_iterate": True,
        "stop_reason": "",
        
        # Content (empty lists)
        "hypotheses": [],
        "sources": [],
        "experiments": [],
        "critiques": [],
        "paper_draft": "",
        
        # Communication
        "messages": [
            {
                "role": "system",
                "content": f"Starting research on: {question}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ],
        
        # Metrics
        "started_at": datetime.utcnow().isoformat(),
        "total_tokens_used": 0,
        "total_cost": 0.0,
    }
    
    return state


def should_continue_iteration(state: ResearchState) -> bool:
    """
    Determine if the research should continue iterating.
    
    Args:
        state: Current research state
    
    Returns:
        True if should continue, False otherwise
    """
    
    # Check if we've hit max iterations
    if state["iteration"] >= state["max_iterations"]:
        state["should_iterate"] = False
        state["stop_reason"] = "max_iterations_reached"
        logger.info(f"Stopping: Max iterations ({state['max_iterations']}) reached")
        return False
    
    # Check if quality threshold is met
    if state["quality_score"] >= state["quality_threshold"]:
        state["should_iterate"] = False
        state["stop_reason"] = "quality_threshold_met"
        logger.info(f"Stopping: Quality threshold ({state['quality_threshold']}) met with score {state['quality_score']}")
        return False
    
    # Check if improvement is sufficient
    if len(state["quality_history"]) >= 2:
        improvement = state["quality_history"][-1] - state["quality_history"][-2]
        if improvement < state["improvement_threshold"]:
            state["should_iterate"] = False
            state["stop_reason"] = "insufficient_improvement"
            logger.info(f"Stopping: Improvement ({improvement}) below threshold ({state['improvement_threshold']})")
            return False
    
    # Continue iteration
    logger.info(f"Continuing iteration {state['iteration'] + 1}")
    return True


def update_quality_score(state: ResearchState, new_score: float) -> None:
    """
    Update the quality score and history in the state.
    
    Args:
        state: Current research state
        new_score: New quality score to record
    """
    state["quality_history"].append(new_score)
    state["quality_score"] = new_score
    logger.info(f"Quality score updated: {new_score} (iteration {state['iteration']})")

