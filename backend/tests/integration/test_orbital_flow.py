"""
Integration tests for FLUX Orbital Research Flow.
Tests iteration behavior, quality tracking, and stopping conditions.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from flux_core.graph.research_graph import (
    create_research_graph,
    run_research,
)
from flux_core.graph.state import create_initial_state


@pytest.mark.integration
class TestOrbitalIterationBehavior:
    """Tests for orbital iteration logic and stopping conditions."""
    
    @pytest.mark.asyncio
    async def test_single_orbit_when_quality_met(self, mock_bedrock_client):
        """
        Test that research completes in one orbit when quality threshold is met immediately.
        
        With low quality threshold and high mock quality score,
        should complete after first orbit.
        """
        # Patch Bedrock client
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock high quality score response
            mock_bedrock_client.invoke.return_value = """
            {
                "quality_score": 9.0,
                "issues": [],
                "strengths": ["Excellent hypotheses", "Great sources"],
                "recommendations": ["Continue with current approach"]
            }
            """
            
            # Create state with low threshold
            state = create_initial_state(
                question="What is 2+2?",
                research_id="test-single-orbit",
                max_iterations=3,
                quality_threshold=7.0,  # Low threshold - should meet immediately
                improvement_threshold=0.5,
            )
            
            # Run graph
            graph = create_research_graph()
            final_state = await graph.ainvoke(state)
            
            # Verify single orbit
            assert final_state["iteration"] == 0, "Should complete in first iteration"
            assert len(final_state["quality_history"]) == 1, "Should have one quality score"
            assert final_state["quality_score"] >= 7.0, "Quality should meet threshold"
            assert final_state["stop_reason"] == "quality_threshold_met"
            assert final_state["phase"] == "complete"
    
    @pytest.mark.asyncio
    async def test_multiple_orbits_when_quality_low(self, mock_bedrock_client):
        """
        Test that research iterates multiple times when quality is below threshold.
        
        With high threshold and gradually improving scores,
        should iterate multiple times.
        """
        # Patch Bedrock client
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock progressive quality improvement
            quality_responses = [
                '{"quality_score": 5.0, "issues": ["Needs more detail"], "strengths": ["Good start"], "recommendations": ["Expand"]}',
                '{"quality_score": 6.5, "issues": ["Still needs work"], "strengths": ["Better"], "recommendations": ["Continue"]}',
                '{"quality_score": 8.5, "issues": [], "strengths": ["Excellent"], "recommendations": ["Complete"]}',
            ]
            
            call_count = {"index": 0}
            def get_response(*args, **kwargs):
                response = quality_responses[min(call_count["index"], len(quality_responses) - 1)]
                call_count["index"] += 1
                return response
            
            mock_bedrock_client.invoke.side_effect = get_response
            
            # Create state with high threshold
            state = create_initial_state(
                question="Explain quantum computing",
                research_id="test-multiple-orbits",
                max_iterations=5,
                quality_threshold=8.0,  # High threshold
                improvement_threshold=0.3,
            )
            
            # Run graph
            graph = create_research_graph()
            final_state = await graph.ainvoke(state)
            
            # Verify multiple orbits
            assert final_state["iteration"] >= 1, "Should have multiple iterations"
            assert len(final_state["quality_history"]) >= 2, "Should have multiple quality scores"
            
            # Verify quality improvement
            history = final_state["quality_history"]
            assert history[-1] > history[0], "Quality should improve"
            
            # Should eventually meet threshold or hit max iterations
            assert (
                final_state["quality_score"] >= 8.0 or 
                final_state["iteration"] >= 5
            )
    
    @pytest.mark.asyncio
    async def test_stops_at_max_iterations(self, mock_bedrock_client):
        """
        Test that research stops at max iterations even if quality not met.
        
        With impossible threshold, should hit max iterations.
        """
        # Patch Bedrock client
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock consistently low quality
            mock_bedrock_client.invoke.return_value = """
            {
                "quality_score": 5.0,
                "issues": ["Not good enough"],
                "strengths": ["Trying"],
                "recommendations": ["Keep working"]
            }
            """
            
            # Create state with impossible threshold
            state = create_initial_state(
                question="Solve P vs NP",
                research_id="test-max-iterations",
                max_iterations=2,  # Low max to test quickly
                quality_threshold=9.9,  # Impossible threshold
                improvement_threshold=0.1,
            )
            
            # Run graph
            graph = create_research_graph()
            final_state = await graph.ainvoke(state)
            
            # Verify max iterations reached
            assert final_state["iteration"] >= 2, "Should reach max iterations"
            assert final_state["stop_reason"] == "max_iterations_reached"
            assert final_state["quality_score"] < 9.9, "Quality not met"
            assert final_state["phase"] == "complete"
    
    @pytest.mark.asyncio
    async def test_stops_on_diminishing_returns(self, mock_bedrock_client):
        """
        Test that research stops when improvement falls below threshold.
        
        Quality improves then plateaus - should stop early.
        """
        # Patch Bedrock client
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock quality plateau
            quality_responses = [
                '{"quality_score": 6.0, "issues": ["Needs work"], "strengths": ["OK"], "recommendations": ["Improve"]}',
                '{"quality_score": 6.3, "issues": ["Still needs work"], "strengths": ["Better"], "recommendations": ["Continue"]}',
                '{"quality_score": 6.4, "issues": ["Plateau"], "strengths": ["Stable"], "recommendations": ["Done"]}',
            ]
            
            call_count = {"index": 0}
            def get_response(*args, **kwargs):
                response = quality_responses[min(call_count["index"], len(quality_responses) - 1)]
                call_count["index"] += 1
                return response
            
            mock_bedrock_client.invoke.side_effect = get_response
            
            # Create state with high improvement threshold
            state = create_initial_state(
                question="Research topic",
                research_id="test-diminishing-returns",
                max_iterations=5,
                quality_threshold=9.0,  # High threshold (won't be met)
                improvement_threshold=0.5,  # High improvement threshold
            )
            
            # Run graph
            graph = create_research_graph()
            final_state = await graph.ainvoke(state)
            
            # Verify stopped due to insufficient improvement
            assert final_state["stop_reason"] == "insufficient_improvement"
            assert len(final_state["quality_history"]) >= 2
            
            # Verify improvement was below threshold
            if len(final_state["quality_history"]) >= 2:
                improvement = (
                    final_state["quality_history"][-1] - 
                    final_state["quality_history"][-2]
                )
                assert improvement < 0.5, "Improvement should be below threshold"
    
    @pytest.mark.asyncio
    async def test_quality_increases_each_orbit(self, mock_bedrock_client):
        """
        Test that quality score increases across orbital iterations.
        
        Verify that quality_history shows progressive improvement.
        """
        # Patch Bedrock client
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock steadily increasing quality
            quality_responses = [
                '{"quality_score": 4.0, "issues": ["Many issues"], "strengths": ["Starting"], "recommendations": ["Improve all"]}',
                '{"quality_score": 5.5, "issues": ["Some issues"], "strengths": ["Better"], "recommendations": ["Keep going"]}',
                '{"quality_score": 7.0, "issues": ["Few issues"], "strengths": ["Good"], "recommendations": ["Almost there"]}',
                '{"quality_score": 8.5, "issues": [], "strengths": ["Excellent"], "recommendations": ["Complete"]}',
            ]
            
            call_count = {"index": 0}
            def get_response(*args, **kwargs):
                response = quality_responses[min(call_count["index"], len(quality_responses) - 1)]
                call_count["index"] += 1
                return response
            
            mock_bedrock_client.invoke.side_effect = get_response
            
            # Create state
            state = create_initial_state(
                question="Research with improvement",
                research_id="test-quality-increase",
                max_iterations=4,
                quality_threshold=8.0,
                improvement_threshold=0.3,
            )
            
            # Run graph
            graph = create_research_graph()
            final_state = await graph.ainvoke(state)
            
            # Verify quality improvement
            history = final_state["quality_history"]
            assert len(history) >= 2, "Should have multiple quality scores"
            
            # Check each score is higher than previous
            for i in range(1, len(history)):
                assert history[i] >= history[i-1], f"Quality should increase: {history[i-1]} -> {history[i]}"
            
            # Verify final quality meets threshold
            assert final_state["quality_score"] >= 8.0


@pytest.mark.integration
class TestStateEvolution:
    """Tests for state changes during orbital flow."""
    
    @pytest.mark.asyncio
    async def test_iteration_increments_correctly(self, mock_bedrock_client, sample_state):
        """Test that iteration counter increments with each orbit."""
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock quality that requires multiple iterations
            mock_bedrock_client.invoke.return_value = """
            {"quality_score": 6.0, "issues": ["Needs work"], "strengths": ["OK"], "recommendations": ["Continue"]}
            """
            
            sample_state["max_iterations"] = 2
            sample_state["quality_threshold"] = 9.0
            
            graph = create_research_graph()
            final_state = await graph.ainvoke(sample_state)
            
            # Should have iterated
            assert final_state["iteration"] > 0
            assert final_state["iteration"] <= 2
    
    @pytest.mark.asyncio
    async def test_quality_history_grows(self, mock_bedrock_client, sample_state):
        """Test that quality_history accumulates scores."""
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            quality_responses = [
                '{"quality_score": 5.0}',
                '{"quality_score": 6.0}',
            ]
            
            call_count = {"index": 0}
            def get_response(*args, **kwargs):
                response = quality_responses[min(call_count["index"], len(quality_responses) - 1)]
                call_count["index"] += 1
                return response
            
            mock_bedrock_client.invoke.side_effect = get_response
            
            sample_state["max_iterations"] = 2
            sample_state["quality_threshold"] = 9.0
            
            graph = create_research_graph()
            final_state = await graph.ainvoke(sample_state)
            
            # Verify history
            assert len(final_state["quality_history"]) >= 1
            assert all(isinstance(score, (int, float)) for score in final_state["quality_history"])
    
    @pytest.mark.asyncio
    async def test_stop_reason_set_appropriately(self, mock_bedrock_client):
        """Test that stop_reason is set correctly for different conditions."""
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Test quality threshold met
            mock_bedrock_client.invoke.return_value = '{"quality_score": 9.0}'
            
            state1 = create_initial_state(
                question="Test",
                research_id="test-stop-reason-1",
                quality_threshold=8.0,
            )
            
            graph = create_research_graph()
            final1 = await graph.ainvoke(state1)
            
            assert final1["stop_reason"] in [
                "quality_threshold_met",
                "max_iterations_reached",
                "insufficient_improvement"
            ]


@pytest.mark.integration
class TestComponentIntegration:
    """Tests for integration between different components."""
    
    @pytest.mark.asyncio
    async def test_agents_populate_state_correctly(self, mock_bedrock_client):
        """Test that each agent adds expected data to state."""
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            # Mock responses for different agents
            def dynamic_response(*args, **kwargs):
                prompt = args[0] if args else ""
                
                if "hypothes" in prompt.lower():
                    return '[{"id": "h1", "text": "Test hypothesis", "confidence": 80, "reasoning": "Test", "test_approach": "Test"}]'
                elif "search" in prompt.lower() or "source" in prompt.lower():
                    return '{"summary": "Test summary", "key_themes": ["theme1"], "research_gaps": ["gap1"], "relevance": "relevant", "contradictions": []}'
                elif "experiment" in prompt.lower():
                    return '[{"hypothesis_id": "h1", "method": "Test method", "measurements": "Test", "success_criteria": "Test", "time_estimate": "1 week", "potential_issues": "None"}]'
                elif "quality" in prompt.lower() or "review" in prompt.lower():
                    return '{"quality_score": 8.5, "issues": [], "strengths": ["Good"], "recommendations": ["Continue"]}'
                else:
                    return "Test response"
            
            mock_bedrock_client.invoke.side_effect = dynamic_response
            
            # Mock search results
            with patch("flux_core.agents.source.multi_source_search") as mock_search:
                mock_search.return_value = [
                    {"title": "Test", "authors": ["Author"], "year": 2024, 
                     "abstract": "Test", "url": "http://test.com", "source_type": "test"}
                ]
                
                state = create_initial_state(
                    question="Test question",
                    research_id="test-integration",
                    quality_threshold=8.0,
                )
                
                graph = create_research_graph()
                final_state = await graph.ainvoke(state)
                
                # Verify state population
                assert len(final_state["hypotheses"]) > 0, "Should have hypotheses"
                assert len(final_state["sources"]) > 0, "Should have sources"
                assert len(final_state["experiments"]) > 0, "Should have experiments"
                assert len(final_state["critiques"]) > 0, "Should have critiques"
                assert final_state["paper_draft"], "Should have paper"
    
    @pytest.mark.asyncio
    async def test_messages_track_agent_activity(self, mock_bedrock_client):
        """Test that messages array tracks agent activity."""
        with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
            mock_client_class.return_value = mock_bedrock_client
            
            mock_bedrock_client.invoke.return_value = '{"quality_score": 9.0}'
            
            # Mock search
            with patch("flux_core.agents.source.multi_source_search") as mock_search:
                mock_search.return_value = []
                
                state = create_initial_state(
                    question="Test",
                    research_id="test-messages",
                    quality_threshold=8.5,
                )
                
                graph = create_research_graph()
                final_state = await graph.ainvoke(state)
                
                # Verify messages
                messages = final_state.get("messages", [])
                assert len(messages) > 1, "Should have multiple messages"
                
                # Check message structure
                if messages:
                    msg = messages[-1]
                    assert "agent" in msg or "message" in msg


@pytest.mark.slow
@pytest.mark.integration
class TestRealWorkflow:
    """
    Integration tests with more realistic scenarios.
    Marked as slow since they exercise the full workflow.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real AWS Bedrock access")
    async def test_full_research_workflow_real(self):
        """
        Test complete research workflow with real LLM.
        
        This test requires AWS credentials and makes real API calls.
        Run with: pytest -m integration --run-real
        """
        state = create_initial_state(
            question="What are the latest advances in quantum computing?",
            research_id="real-workflow-test",
            max_iterations=2,
            quality_threshold=7.0,
        )
        
        graph = create_research_graph()
        final_state = await graph.ainvoke(state)
        
        # Verify complete workflow
        assert final_state["phase"] == "complete"
        assert final_state["paper_draft"]
        assert len(final_state["quality_history"]) >= 1

