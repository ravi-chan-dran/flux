"""
Unit tests for FLUX research agents.
Tests agent initialization, LLM integration, and specific agent behaviors.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from flux_core.agents.base_agent import BaseAgent
from flux_core.agents.flow_master import FlowMasterAgent
from flux_core.agents.current import CurrentAgent
from flux_core.agents.source import SourceAgent
from flux_core.agents.channel import ChannelAgent
from flux_core.agents.filter import FilterAgent
from flux_core.agents.confluence import ConfluenceAgent


@pytest.fixture
def mock_bedrock_client():
    """Mock BedrockClient for all agents."""
    with patch("flux_core.agents.base_agent.BedrockClient") as mock_client_class:
        mock_client = Mock()
        mock_client.invoke = Mock(return_value="Mocked LLM response")
        mock_client.stream = Mock(return_value=iter(["Mocked ", "stream ", "response"]))
        mock_client_class.return_value = mock_client
        yield mock_client


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""
    
    def test_base_agent_initialization(self, mock_bedrock_client):
        """Test that BaseAgent initializes correctly."""
        # Create a concrete implementation for testing
        class TestAgent(BaseAgent):
            pass
        
        agent = TestAgent(
            name="Test Agent",
            emoji="🧪",
            color="blue",
            role="Tester",
            system_prompt="You are a test agent",
        )
        
        assert agent.name == "Test Agent"
        assert agent.emoji == "🧪"
        assert agent.color == "blue"
        assert agent.role == "Tester"
        assert agent.system_prompt == "You are a test agent"
        assert agent.bedrock_client == mock_bedrock_client
        assert isinstance(agent.conversation_history, list)
    
    @pytest.mark.asyncio
    async def test_invoke_model(self, mock_bedrock_client):
        """Test that invoke_model calls Bedrock and tracks history."""
        class TestAgent(BaseAgent):
            pass
        
        agent = TestAgent(
            name="Test", emoji="🧪", color="blue", role="Test", system_prompt="Test prompt"
        )
        
        mock_bedrock_client.invoke.return_value = "Test response"
        
        response = await agent.invoke_model("Test prompt", context={"key": "value"})
        
        assert response == "Test response"
        assert len(agent.conversation_history) == 2  # User + assistant
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_stream_response(self, mock_bedrock_client):
        """Test that stream_response yields tokens."""
        class TestAgent(BaseAgent):
            pass
        
        agent = TestAgent(
            name="Test", emoji="🧪", color="blue", role="Test", system_prompt="Test prompt"
        )
        
        mock_bedrock_client.stream.return_value = iter(["Hello", " ", "World"])
        
        tokens = []
        async for token in agent.stream_response("Test prompt"):
            tokens.append(token)
        
        assert tokens == ["Hello", " ", "World"]
        assert len(agent.conversation_history) == 2  # User + assistant
    
    def test_format_message(self, mock_bedrock_client):
        """Test message formatting with metadata."""
        class TestAgent(BaseAgent):
            pass
        
        agent = TestAgent(
            name="Test", emoji="🧪", color="blue", role="Test", system_prompt="Test prompt"
        )
        
        message = agent.format_message(
            "Test content",
            message_type="analysis",
            metadata={"extra": "data"}
        )
        
        assert message["agent"] == "Test"
        assert message["emoji"] == "🧪"
        assert message["color"] == "blue"
        assert message["message"] == "Test content"
        assert message["message_type"] == "analysis"
        assert message["metadata"]["extra"] == "data"
        assert "timestamp" in message
    
    def test_conversation_history_management(self, mock_bedrock_client):
        """Test conversation history tracking and clearing."""
        class TestAgent(BaseAgent):
            pass
        
        agent = TestAgent(
            name="Test", emoji="🧪", color="blue", role="Test", system_prompt="Test prompt"
        )
        
        # Add some history
        agent.conversation_history.append({"role": "user", "content": "test"})
        agent.conversation_history.append({"role": "assistant", "content": "response"})
        
        # Get history
        history = agent.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        
        # Clear history
        agent.clear_conversation_history()
        assert len(agent.conversation_history) == 0


class TestFlowMasterAgent:
    """Tests for FlowMasterAgent."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test FlowMasterAgent initializes correctly."""
        agent = FlowMasterAgent()
        
        assert agent.name == "The Flow Master"
        assert agent.emoji == "🧑‍💼"
        assert agent.color == "purple"
        assert agent.role == "Orchestrator"
    
    @pytest.mark.asyncio
    async def test_analyze_question(self, mock_bedrock_client):
        """Test question analysis returns structured plan."""
        agent = FlowMasterAgent()
        
        mock_bedrock_client.invoke.return_value = """
        {
            "concepts": ["quantum", "entanglement"],
            "research_type": "theoretical",
            "challenges": ["complexity"],
            "initial_plan": "Generate hypotheses first"
        }
        """
        
        analysis = await agent.analyze_question("How does quantum entanglement work?")
        
        assert "concepts" in analysis
        assert isinstance(analysis, dict)
    
    @pytest.mark.asyncio
    async def test_decide_next_step_first_iteration(self, mock_bedrock_client):
        """Test routing logic for first iteration."""
        agent = FlowMasterAgent()
        
        # First iteration, initialize phase
        state = {
            "iteration": 0,
            "max_iterations": 3,
            "quality_score": 0.0,
            "quality_threshold": 8.0,
            "phase": "initialize",
            "quality_history": [],
        }
        
        next_step = await agent.decide_next_step(state)
        assert next_step == "current"  # Should start with Current agent
    
    @pytest.mark.asyncio
    async def test_decide_next_step_max_iterations(self, mock_bedrock_client):
        """Test that max iterations triggers confluence."""
        agent = FlowMasterAgent()
        
        state = {
            "iteration": 3,
            "max_iterations": 3,
            "quality_score": 5.0,
            "quality_threshold": 8.0,
            "phase": "critique",
            "quality_history": [4.0, 5.0],
        }
        
        next_step = await agent.decide_next_step(state)
        assert next_step == "confluence"
    
    @pytest.mark.asyncio
    async def test_decide_next_step_quality_threshold(self, mock_bedrock_client):
        """Test that meeting quality threshold triggers confluence."""
        agent = FlowMasterAgent()
        
        state = {
            "iteration": 1,
            "max_iterations": 3,
            "quality_score": 8.5,
            "quality_threshold": 8.0,
            "phase": "critique",
            "quality_history": [7.0, 8.5],
        }
        
        next_step = await agent.decide_next_step(state)
        assert next_step == "confluence"


class TestCurrentAgent:
    """Tests for CurrentAgent (Hypothesis Generator)."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test CurrentAgent initializes correctly."""
        agent = CurrentAgent()
        
        assert agent.name == "The Current"
        assert agent.emoji == "💡"
        assert agent.color == "cyan"
        assert agent.role == "Hypothesis Generator"
    
    @pytest.mark.asyncio
    async def test_generate_hypotheses_first_iteration(self, mock_bedrock_client):
        """Test hypothesis generation on iteration 0."""
        agent = CurrentAgent()
        
        mock_bedrock_client.invoke.return_value = """
        [
            {
                "id": "h1",
                "text": "Quantum entanglement is non-local",
                "confidence": 85,
                "reasoning": "Based on Bell's theorem",
                "test_approach": "Bell inequality tests"
            },
            {
                "id": "h2",
                "text": "Information cannot travel faster than light",
                "confidence": 90,
                "reasoning": "Special relativity",
                "test_approach": "Causality experiments"
            }
        ]
        """
        
        hypotheses = await agent.generate_hypotheses(
            "How does quantum entanglement work?",
            iteration=0
        )
        
        assert len(hypotheses) >= 1
        assert all("id" in h for h in hypotheses)
        assert all("text" in h for h in hypotheses)
        assert all("confidence" in h for h in hypotheses)
    
    @pytest.mark.asyncio
    async def test_generate_hypotheses_refinement(self, mock_bedrock_client):
        """Test hypothesis refinement on later iterations."""
        agent = CurrentAgent()
        
        existing = [
            {"id": "h1", "text": "Test hypothesis", "confidence": 50}
        ]
        
        mock_bedrock_client.invoke.return_value = """
        [{"id": "h1", "text": "Refined hypothesis", "confidence": 75, 
          "reasoning": "Better reasoning", "test_approach": "Better test"}]
        """
        
        hypotheses = await agent.generate_hypotheses(
            "Question",
            context={"existing_hypotheses": existing, "critiques": []},
            iteration=1
        )
        
        assert len(hypotheses) >= 1


class TestSourceAgent:
    """Tests for SourceAgent (Research Searcher)."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test SourceAgent initializes correctly."""
        agent = SourceAgent()
        
        assert agent.name == "The Source"
        assert agent.emoji == "📚"
        assert agent.color == "amber"
        assert agent.role == "Research Searcher"
    
    @pytest.mark.asyncio
    async def test_search_research(self, mock_bedrock_client):
        """Test research search and synthesis."""
        agent = SourceAgent()
        
        # Mock multi_source_search
        with patch("flux_core.agents.source.multi_source_search") as mock_search:
            mock_search.return_value = [
                {
                    "title": "Test Paper",
                    "authors": ["Author"],
                    "year": 2024,
                    "abstract": "Test abstract",
                    "url": "http://test.com",
                    "source_type": "arxiv"
                }
            ]
            
            mock_bedrock_client.invoke.return_value = """
            {
                "summary": "Test research summary",
                "key_themes": ["theme1", "theme2"],
                "research_gaps": ["gap1"],
                "relevance": "Highly relevant",
                "contradictions": []
            }
            """
            
            result = await agent.search_research(
                "quantum computing",
                iteration=0,
                limit=10
            )
            
            assert "sources" in result
            assert "synthesis" in result
            assert len(result["sources"]) == 1


class TestChannelAgent:
    """Tests for ChannelAgent (Experiment Designer)."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test ChannelAgent initializes correctly."""
        agent = ChannelAgent()
        
        assert agent.name == "The Channel"
        assert agent.emoji == "🔬"
        assert agent.color == "teal"
        assert agent.role == "Experiment Designer"
    
    @pytest.mark.asyncio
    async def test_design_experiments(self, mock_bedrock_client):
        """Test experiment design for hypotheses."""
        agent = ChannelAgent()
        
        hypotheses = [
            {"id": "h1", "text": "Test hypothesis", "confidence": 80}
        ]
        
        mock_bedrock_client.invoke.return_value = """
        [
            {
                "hypothesis_id": "h1",
                "method": "Test the hypothesis using method X",
                "measurements": "Measure Y and Z",
                "success_criteria": "Y > threshold",
                "time_estimate": "2 weeks",
                "potential_issues": "Confounding variables"
            }
        ]
        """
        
        experiments = await agent.design_experiments(hypotheses, iteration=0)
        
        assert len(experiments) >= 1
        assert all("hypothesis_id" in e for e in experiments)
        assert all("method" in e for e in experiments)


class TestFilterAgent:
    """Tests for FilterAgent (Quality Critic)."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test FilterAgent initializes correctly."""
        agent = FilterAgent()
        
        assert agent.name == "The Filter"
        assert agent.emoji == "🛡️"
        assert agent.color == "red"
        assert agent.role == "Quality Critic"
    
    @pytest.mark.asyncio
    async def test_review(self, mock_bedrock_client):
        """Test research review and critique."""
        agent = FilterAgent()
        
        state = {
            "question": "Test question",
            "hypotheses": [{"id": "h1", "text": "Hypothesis"}],
            "sources": [{"title": "Paper"}],
            "experiments": [{"hypothesis_id": "h1", "method": "Method"}],
            "iteration": 0,
        }
        
        mock_bedrock_client.invoke.return_value = """
        {
            "quality_score": 7.5,
            "issues": ["Hypothesis needs more detail"],
            "strengths": ["Good source coverage"],
            "recommendations": ["Expand hypothesis reasoning"]
        }
        """
        
        critique = await agent.review(state)
        
        assert "quality_score" in critique
        assert "issues" in critique
        assert "strengths" in critique
        assert "recommendations" in critique
    
    def test_calculate_quality_score(self, mock_bedrock_client):
        """Test quality score extraction from text."""
        agent = FilterAgent()
        
        # Test explicit score
        text1 = "The quality score is 8.5 out of 10"
        score1 = agent.calculate_quality_score(text1)
        assert 8.0 <= score1 <= 9.0
        
        # Test pattern "score: 7"
        text2 = "Overall score: 7.0"
        score2 = agent.calculate_quality_score(text2)
        assert 6.5 <= score2 <= 7.5
        
        # Test sentiment-based fallback
        text3 = "This is excellent and strong work with good quality"
        score3 = agent.calculate_quality_score(text3)
        assert score3 > 5.0  # Should be positive
    
    def test_extract_issues(self, mock_bedrock_client):
        """Test issue extraction from critique text."""
        agent = FilterAgent()
        
        text = """
        Issues:
        - Hypotheses are unclear and vague
        - Sources are insufficient
        - Experiments poorly designed
        
        Strengths:
        - Good overall approach
        """
        
        issues = agent.extract_issues(text)
        
        assert len(issues) >= 1
        assert any("unclear" in issue.lower() or "vague" in issue.lower() for issue in issues)
    
    def test_extract_issues_handles_no_issues(self, mock_bedrock_client):
        """Test that extract_issues handles text with no clear issues."""
        agent = FilterAgent()
        
        text = "Everything looks great! No problems found."
        issues = agent.extract_issues(text)
        
        # Should return empty list or minimal issues
        assert isinstance(issues, list)


class TestConfluenceAgent:
    """Tests for ConfluenceAgent (Paper Synthesizer)."""
    
    def test_initialization(self, mock_bedrock_client):
        """Test ConfluenceAgent initializes correctly."""
        agent = ConfluenceAgent()
        
        assert agent.name == "The Confluence"
        assert agent.emoji == "✍️"
        assert agent.color == "indigo"
        assert agent.role == "Paper Synthesizer"
    
    @pytest.mark.asyncio
    async def test_write_paper(self, mock_bedrock_client):
        """Test paper writing and synthesis."""
        agent = ConfluenceAgent()
        
        state = {
            "question": "How does quantum computing work?",
            "hypotheses": [{"id": "h1", "text": "Qubits enable superposition"}],
            "sources": [{"title": "Quantum Paper", "authors": ["Feynman"], "year": 1982}],
            "experiments": [{"hypothesis_id": "h1", "method": "Test superposition"}],
            "critiques": [],
            "quality_score": 8.0,
            "iteration": 2,
        }
        
        mock_bedrock_client.invoke.return_value = """
# Quantum Computing Research

## Abstract
This paper explores quantum computing through hypothesis-driven research.

## Introduction
Quantum computing represents a paradigm shift...

## Background
Based on extensive literature review...

## Hypotheses
We propose that qubits enable superposition...

## Methodology
Experimental designs were developed...

## Results
The research reveals...

## Discussion
These findings suggest...

## Conclusion
This work contributes to understanding quantum computing.

## References
1. Feynman et al. (1982). Quantum Paper.
"""
        
        paper = await agent.write_paper(state)
        
        assert len(paper) > 200
        assert "abstract" in paper.lower() or "quantum" in paper.lower()
    
    def test_get_paper_metadata(self, mock_bedrock_client):
        """Test paper metadata extraction."""
        agent = ConfluenceAgent()
        
        state = {
            "question": "Test question",
            "iteration": 2,
            "quality_score": 7.5,
            "quality_history": [6.0, 7.0, 7.5],
            "hypotheses": [{"id": "h1"}],
            "sources": [{"title": "Paper"}],
            "experiments": [{"hypothesis_id": "h1"}],
            "stop_reason": "quality_threshold",
        }
        
        paper = "# Test Paper\n\nContent here with many words..."
        
        metadata = agent.get_paper_metadata(state, paper)
        
        assert metadata["question"] == "Test question"
        assert metadata["iterations"] == 3
        assert metadata["final_quality_score"] == 7.5
        assert metadata["hypothesis_count"] == 1
        assert metadata["source_count"] == 1


@pytest.mark.integration
class TestAgentIntegration:
    """
    Integration tests for agents working together.
    These require real Bedrock access and are skipped by default.
    """
    
    @pytest.mark.skip(reason="Requires AWS Bedrock access")
    @pytest.mark.asyncio
    async def test_full_research_flow(self):
        """Test a complete research flow through all agents."""
        # This would test: Flow Master -> Current -> Source -> Channel -> Filter -> Confluence
        pass

