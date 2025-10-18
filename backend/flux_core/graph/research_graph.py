"""
LangGraph Orbital Research Flow
Implements the iterative research workflow through specialized agents.
"""

from typing import Any, Literal
from loguru import logger

from langgraph.graph import StateGraph, END
from flux_core.graph.state import ResearchState, should_continue_iteration, update_quality_score
from flux_core.agents import (
    FlowMasterAgent,
    CurrentAgent,
    SourceAgent,
    ChannelAgent,
    FilterAgent,
    ConfluenceAgent,
)


# Initialize all agents
flow_master = FlowMasterAgent()
current_agent = CurrentAgent()
source_agent = SourceAgent()
channel_agent = ChannelAgent()
filter_agent = FilterAgent()
confluence_agent = ConfluenceAgent()


# Agent wrapper functions that update state

async def flow_master_node(state: ResearchState) -> ResearchState:
    """
    Flow Master node: Decides next action based on state.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with next_action set
    """
    logger.info(f"🧑‍💼 Flow Master analyzing state (iteration {state['iteration']})")
    
    try:
        # Decide next step
        next_action = await flow_master.decide_next_step(state)
        
        # Generate routing message
        message = await flow_master.generate_routing_message(state, next_action)
        
        # Update state
        state["next_action"] = next_action
        state["messages"].append(
            flow_master.format_message(message, message_type="routing")
        )
        
        logger.info(f"🧑‍💼 Flow Master routing to: {next_action}")
        return state
    
    except Exception as e:
        logger.error(f"🧑‍💼 Flow Master error: {e}")
        state["next_action"] = "filter"  # Safe fallback
        return state


async def current_node(state: ResearchState) -> ResearchState:
    """
    Current node: Generate or refine hypotheses.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with hypotheses
    """
    iteration = state["iteration"]
    logger.info(f"💡 The Current generating hypotheses (iteration {iteration})")
    
    try:
        # Prepare context
        context = {
            "existing_hypotheses": state.get("hypotheses", []),
            "critiques": state.get("critiques", []),
        }
        
        # Generate hypotheses
        hypotheses = await current_agent.generate_hypotheses(
            state["question"],
            context=context,
            iteration=iteration,
        )
        
        # Update state
        state["hypotheses"] = hypotheses
        state["phase"] = "hypotheses"
        state["messages"].append(
            current_agent.format_message(
                f"Generated {len(hypotheses)} hypotheses",
                message_type="hypotheses",
                metadata={"count": len(hypotheses), "hypotheses": hypotheses}
            )
        )
        
        logger.info(f"💡 The Current generated {len(hypotheses)} hypotheses")
        return state
    
    except Exception as e:
        logger.error(f"💡 The Current error: {e}")
        state["phase"] = "hypotheses"
        return state


async def source_node(state: ResearchState) -> ResearchState:
    """
    Source node: Search and synthesize research.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with sources and synthesis
    """
    iteration = state["iteration"]
    logger.info(f"📚 The Source searching research (iteration {iteration})")
    
    try:
        # Prepare context
        context = {
            "existing_hypotheses": state.get("hypotheses", []),
            "critiques": state.get("critiques", []),
        }
        
        # Search research
        research = await source_agent.search_research(
            state["question"],
            context=context,
            iteration=iteration,
            limit=10,
        )
        
        # Update state
        state["sources"] = research.get("sources", [])
        state["phase"] = "research"
        
        synthesis = research.get("synthesis", {})
        state["messages"].append(
            source_agent.format_message(
                synthesis.get("summary", f"Found {len(state['sources'])} sources"),
                message_type="research",
                metadata={
                    "source_count": len(state["sources"]),
                    "synthesis": synthesis
                }
            )
        )
        
        logger.info(f"📚 The Source found {len(state['sources'])} sources")
        return state
    
    except Exception as e:
        logger.error(f"📚 The Source error: {e}")
        state["phase"] = "research"
        return state


async def channel_node(state: ResearchState) -> ResearchState:
    """
    Channel node: Design experiments.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with experiments
    """
    iteration = state["iteration"]
    hypotheses = state.get("hypotheses", [])
    logger.info(f"🔬 The Channel designing experiments (iteration {iteration})")
    
    try:
        # Prepare context
        context = {
            "existing_experiments": state.get("experiments", []),
            "critiques": state.get("critiques", []),
        }
        
        # Design experiments
        experiments = await channel_agent.design_experiments(
            hypotheses=hypotheses,
            sources=state.get("sources", []),
            iteration=iteration,
            context=context,
        )
        
        # Update state
        state["experiments"] = experiments
        state["phase"] = "experiments"
        state["messages"].append(
            channel_agent.format_message(
                f"Designed {len(experiments)} experiments",
                message_type="experiments",
                metadata={"count": len(experiments), "experiments": experiments}
            )
        )
        
        logger.info(f"🔬 The Channel designed {len(experiments)} experiments")
        return state
    
    except Exception as e:
        logger.error(f"🔬 The Channel error: {e}")
        state["phase"] = "experiments"
        return state


async def filter_node(state: ResearchState) -> ResearchState:
    """
    Filter node: Evaluate quality and decide iteration.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with critique and iteration decision
    """
    iteration = state["iteration"]
    logger.info(f"🛡️ The Filter evaluating quality (iteration {iteration})")
    
    try:
        # Review research
        critique = await filter_agent.review(state)
        
        # Update quality score
        quality_score = critique.get("quality_score", 5.0)
        update_quality_score(state, quality_score)
        
        # Store critique
        state["critiques"].append(critique)
        state["phase"] = "critique"
        state["messages"].append(
            filter_agent.format_message(
                f"Quality score: {quality_score:.1f}/10",
                message_type="critique",
                metadata=critique
            )
        )
        
        # Check if should continue iteration
        should_iterate = should_continue_iteration(state)
        state["should_iterate"] = should_iterate
        
        if not should_iterate:
            logger.info(f"🛡️ The Filter: Stopping - {state.get('stop_reason', 'complete')}")
        else:
            # Increment iteration for next orbit
            state["iteration"] = iteration + 1
            logger.info(f"🛡️ The Filter: Continuing to iteration {state['iteration']}")
        
        logger.info(f"🛡️ The Filter scored: {quality_score:.1f}/10")
        return state
    
    except Exception as e:
        logger.error(f"🛡️ The Filter error: {e}")
        state["phase"] = "critique"
        state["should_iterate"] = False
        state["stop_reason"] = "error_in_filter"
        return state


async def confluence_node(state: ResearchState) -> ResearchState:
    """
    Confluence node: Synthesize final paper.
    
    Args:
        state: Current research state
    
    Returns:
        Updated state with final paper
    """
    logger.info(f"✍️ The Confluence synthesizing paper")
    
    try:
        # Write paper
        paper = await confluence_agent.write_paper(state)
        
        # Update state
        state["paper_draft"] = paper
        state["phase"] = "complete"
        state["messages"].append(
            confluence_agent.format_message(
                f"Paper complete: {len(paper)} characters",
                message_type="paper",
                metadata={
                    "word_count": len(paper.split()),
                    "character_count": len(paper)
                }
            )
        )
        
        logger.info(f"✍️ The Confluence completed paper: {len(paper)} chars")
        return state
    
    except Exception as e:
        logger.error(f"✍️ The Confluence error: {e}")
        state["phase"] = "complete"
        state["paper_draft"] = f"# Research Paper\n\nError during synthesis: {e}"
        return state


# Routing functions

def route_from_flow_master(
    state: ResearchState,
) -> Literal["current", "source", "channel", "filter", "confluence"]:
    """
    Route from Flow Master to appropriate agent.
    
    Args:
        state: Current research state
    
    Returns:
        Next node name
    """
    next_action = state.get("next_action", "current")
    logger.debug(f"Routing from Flow Master: {next_action}")
    
    # Validate next action
    valid_actions = ["current", "source", "channel", "filter", "confluence"]
    if next_action not in valid_actions:
        logger.warning(f"Invalid next_action '{next_action}', defaulting to 'filter'")
        return "filter"
    
    return next_action  # type: ignore


def route_from_filter(
    state: ResearchState,
) -> Literal["flow_master", "confluence"]:
    """
    Route from Filter: iterate or finish.
    
    Args:
        state: Current research state
    
    Returns:
        "flow_master" for another orbit or "confluence" to finish
    """
    should_iterate = state.get("should_iterate", False)
    
    if should_iterate:
        logger.debug("Routing from Filter: flow_master (another orbit)")
        return "flow_master"
    else:
        logger.debug("Routing from Filter: confluence (finishing)")
        return "confluence"


# Build the graph

def create_research_graph() -> StateGraph:
    """
    Create and compile the LangGraph orbital research workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building LangGraph orbital research workflow...")
    
    # Create state graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("flow_master", flow_master_node)
    workflow.add_node("current", current_node)
    workflow.add_node("source", source_node)
    workflow.add_node("channel", channel_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("confluence", confluence_node)
    
    # Set entry point
    workflow.set_entry_point("flow_master")
    
    # Add conditional edges from Flow Master
    workflow.add_conditional_edges(
        "flow_master",
        route_from_flow_master,
        {
            "current": "current",
            "source": "source",
            "channel": "channel",
            "filter": "filter",
            "confluence": "confluence",
        }
    )
    
    # Add edges back to Flow Master for orbital iteration
    workflow.add_edge("current", "flow_master")
    workflow.add_edge("source", "flow_master")
    workflow.add_edge("channel", "flow_master")
    
    # Add conditional edge from Filter
    workflow.add_conditional_edges(
        "filter",
        route_from_filter,
        {
            "flow_master": "flow_master",  # Another orbit
            "confluence": "confluence",     # Finish
        }
    )
    
    # Confluence goes to END
    workflow.add_edge("confluence", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("LangGraph orbital research workflow compiled successfully!")
    return graph


# Convenience function for running research

async def run_research(question: str, research_id: str, **config) -> ResearchState:
    """
    Run complete research workflow.
    
    Args:
        question: Research question
        research_id: Unique identifier for this research
        **config: Optional configuration (max_iterations, quality_threshold, etc.)
    
    Returns:
        Final research state with completed paper
    """
    from flux_core.graph.state import create_initial_state
    
    logger.info(f"Starting research: {question}")
    
    # Create initial state
    state = create_initial_state(
        question=question,
        research_id=research_id,
        max_iterations=config.get("max_iterations"),
        quality_threshold=config.get("quality_threshold"),
        improvement_threshold=config.get("improvement_threshold"),
    )
    
    # Create and run graph
    graph = create_research_graph()
    
    # Execute graph
    final_state = await graph.ainvoke(state)
    
    logger.info(f"Research complete: {research_id}")
    logger.info(f"Final quality: {final_state.get('quality_score', 0):.1f}")
    logger.info(f"Iterations: {final_state.get('iteration', 0) + 1}")
    logger.info(f"Stop reason: {final_state.get('stop_reason', 'complete')}")
    
    return final_state


async def stream_research(question: str, research_id: str, **config):
    """
    Stream research workflow updates.
    
    Args:
        question: Research question
        research_id: Unique identifier
        **config: Optional configuration
    
    Yields:
        State updates as the graph executes
    """
    from flux_core.graph.state import create_initial_state
    
    logger.info(f"Streaming research: {question}")
    
    # Create initial state
    state = create_initial_state(
        question=question,
        research_id=research_id,
        max_iterations=config.get("max_iterations"),
        quality_threshold=config.get("quality_threshold"),
        improvement_threshold=config.get("improvement_threshold"),
    )
    
    # Create graph
    graph = create_research_graph()
    
    # Stream execution
    async for state_update in graph.astream(state):
        yield state_update
    
    logger.info(f"Research streaming complete: {research_id}")

