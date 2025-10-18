"""
Unit tests for BedrockClient
Tests AWS Bedrock integration with mocked boto3 client.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError

from flux_core.tools.bedrock_client import BedrockClient, BedrockClientError


@pytest.fixture
def mock_aws_profile(monkeypatch):
    """Mock AWS profile in environment."""
    monkeypatch.setenv("AWS_PROFILE", "test-profile")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")


@pytest.fixture
def mock_boto3_session():
    """Create a mock boto3 session."""
    with patch("flux_core.tools.bedrock_client.boto3.Session") as mock_session:
        yield mock_session


@pytest.fixture
def mock_boto3_client():
    """Create a mock boto3 client."""
    with patch("flux_core.tools.bedrock_client.boto3.client") as mock_client:
        yield mock_client


class TestBedrockClientInitialization:
    """Tests for BedrockClient initialization."""
    
    def test_initialization_with_aws_profile(self, mock_aws_profile, mock_boto3_session):
        """Test successful initialization using AWS profile."""
        mock_bedrock = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_bedrock
        mock_boto3_session.return_value = mock_session_instance
        
        client = BedrockClient()
        
        assert client.profile_name == "test-profile"
        assert client.region_name == "us-east-1"
        assert client.model_id == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert client.client == mock_bedrock
        
        mock_boto3_session.assert_called_once_with(
            profile_name="test-profile",
            region_name="us-east-1",
        )
        mock_session_instance.client.assert_called_once_with(service_name="bedrock-runtime")
    
    def test_initialization_with_explicit_profile(self, mock_boto3_session):
        """Test initialization with explicitly provided profile."""
        mock_bedrock = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_bedrock
        mock_boto3_session.return_value = mock_session_instance
        
        client = BedrockClient(
            profile_name="custom-profile",
            region_name="us-west-2",
            model_id="custom-model-id",
        )
        
        assert client.profile_name == "custom-profile"
        assert client.region_name == "us-west-2"
        assert client.model_id == "custom-model-id"
        
        mock_boto3_session.assert_called_once_with(
            profile_name="custom-profile",
            region_name="us-west-2",
        )
    
    def test_initialization_without_profile_uses_default_chain(self, mock_boto3_client):
        """Test that initialization without profile uses default credential chain."""
        mock_bedrock = Mock()
        mock_boto3_client.return_value = mock_bedrock
        
        client = BedrockClient()
        
        assert client.profile_name is None
        mock_boto3_client.assert_called_once_with(
            service_name="bedrock-runtime",
            region_name="us-east-1",
        )
    
    def test_initialization_boto3_error(self, mock_aws_profile, mock_boto3_session):
        """Test initialization handles boto3 session creation errors."""
        mock_boto3_session.side_effect = Exception("Boto3 initialization failed")
        
        with pytest.raises(BedrockClientError) as exc_info:
            BedrockClient()
        
        assert "Failed to initialize Bedrock client" in str(exc_info.value)


class TestBedrockClientInvoke:
    """Tests for BedrockClient.invoke method."""
    
    @pytest.fixture
    def client(self, mock_aws_credentials, mock_boto3_client):
        """Create a BedrockClient instance with mocked boto3."""
        mock_bedrock = Mock()
        mock_boto3_client.return_value = mock_bedrock
        return BedrockClient()
    
    def test_invoke_success(self, client):
        """Test successful model invocation."""
        # Mock response
        mock_response = {
            "body": Mock(read=lambda: json.dumps({
                "content": [{"text": "This is the generated response"}],
                "usage": {"input_tokens": 10, "output_tokens": 20}
            }).encode())
        }
        client.client.invoke_model = Mock(return_value=mock_response)
        
        result = client.invoke(
            prompt="Test prompt",
            system_prompt="Test system prompt",
            max_tokens=1000
        )
        
        assert result == "This is the generated response"
        
        # Verify the invoke_model was called with correct parameters
        call_args = client.client.invoke_model.call_args
        assert call_args[1]["modelId"] == client.model_id
        
        body = json.loads(call_args[1]["body"])
        assert body["messages"][0]["content"] == "Test prompt"
        assert body["system"] == "Test system prompt"
        assert body["max_tokens"] == 1000
    
    def test_invoke_without_system_prompt(self, client):
        """Test invocation without system prompt."""
        mock_response = {
            "body": Mock(read=lambda: json.dumps({
                "content": [{"text": "Response without system prompt"}],
                "usage": {"input_tokens": 5, "output_tokens": 10}
            }).encode())
        }
        client.client.invoke_model = Mock(return_value=mock_response)
        
        result = client.invoke(prompt="Test prompt")
        
        assert result == "Response without system prompt"
        
        body = json.loads(client.client.invoke_model.call_args[1]["body"])
        assert "system" not in body
    
    def test_invoke_custom_parameters(self, client):
        """Test invocation with custom temperature and top_p."""
        mock_response = {
            "body": Mock(read=lambda: json.dumps({
                "content": [{"text": "Response"}],
                "usage": {}
            }).encode())
        }
        client.client.invoke_model = Mock(return_value=mock_response)
        
        client.invoke(
            prompt="Test",
            temperature=0.5,
            top_p=0.8
        )
        
        body = json.loads(client.client.invoke_model.call_args[1]["body"])
        assert body["temperature"] == 0.5
        assert body["top_p"] == 0.8
    
    def test_invoke_empty_response(self, client):
        """Test handling of empty response content."""
        mock_response = {
            "body": Mock(read=lambda: json.dumps({
                "content": [],
                "usage": {}
            }).encode())
        }
        client.client.invoke_model = Mock(return_value=mock_response)
        
        with pytest.raises(BedrockClientError) as exc_info:
            client.invoke(prompt="Test")
        
        assert "No content in model response" in str(exc_info.value)
    
    def test_invoke_client_error(self, client):
        """Test handling of AWS ClientError."""
        error_response = {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}}
        client.client.invoke_model = Mock(
            side_effect=ClientError(error_response, "InvokeModel")
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            client.invoke(prompt="Test")
        
        assert "ThrottlingException" in str(exc_info.value)
    
    def test_invoke_botocore_error(self, client):
        """Test handling of BotoCoreError."""
        client.client.invoke_model = Mock(
            side_effect=BotoCoreError()
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            client.invoke(prompt="Test")
        
        assert "BotoCoreError" in str(exc_info.value)
    
    def test_invoke_json_decode_error(self, client):
        """Test handling of malformed JSON response."""
        mock_response = {
            "body": Mock(read=lambda: b"invalid json")
        }
        client.client.invoke_model = Mock(return_value=mock_response)
        
        with pytest.raises(BedrockClientError) as exc_info:
            client.invoke(prompt="Test")
        
        assert "Failed to parse response JSON" in str(exc_info.value)
    
    def test_invoke_unexpected_error(self, client):
        """Test handling of unexpected errors."""
        client.client.invoke_model = Mock(
            side_effect=RuntimeError("Unexpected error")
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            client.invoke(prompt="Test")
        
        assert "Unexpected error during invocation" in str(exc_info.value)


class TestBedrockClientStream:
    """Tests for BedrockClient.stream method."""
    
    @pytest.fixture
    def client(self, mock_aws_profile, mock_boto3_session):
        """Create a BedrockClient instance with mocked boto3."""
        mock_bedrock = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_bedrock
        mock_boto3_session.return_value = mock_session_instance
        return BedrockClient()
    
    def test_stream_success(self, client):
        """Test successful streaming response."""
        # Create mock streaming events
        mock_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": "Hello"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": " world"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "message_stop"
                    }).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        # Collect streamed tokens
        tokens = list(client.stream(prompt="Test prompt"))
        
        assert tokens == ["Hello", " world"]
    
    def test_stream_with_system_prompt(self, client):
        """Test streaming with system prompt."""
        mock_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": "Response"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({"type": "message_stop"}).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        tokens = list(client.stream(
            prompt="Test",
            system_prompt="System context"
        ))
        
        assert tokens == ["Response"]
        
        # Verify system prompt was included
        body = json.loads(
            client.client.invoke_model_with_response_stream.call_args[1]["body"]
        )
        assert body["system"] == "System context"
    
    def test_stream_empty_text_ignored(self, client):
        """Test that empty text deltas are ignored."""
        mock_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": ""}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": "Text"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({"type": "message_stop"}).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        tokens = list(client.stream(prompt="Test"))
        
        assert tokens == ["Text"]
    
    def test_stream_error_event(self, client):
        """Test handling of error events in stream."""
        mock_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "error",
                        "error": {"message": "Stream error occurred"}
                    }).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        with pytest.raises(BedrockClientError) as exc_info:
            list(client.stream(prompt="Test"))
        
        assert "Stream error occurred" in str(exc_info.value)
    
    def test_stream_malformed_chunk(self, client):
        """Test that malformed chunks are skipped with warning."""
        mock_events = [
            {
                "chunk": {
                    "bytes": b"invalid json"
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": "Valid"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({"type": "message_stop"}).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        tokens = list(client.stream(prompt="Test"))
        
        # Should skip invalid chunk and continue
        assert tokens == ["Valid"]
    
    def test_stream_client_error(self, client):
        """Test handling of AWS ClientError during streaming."""
        error_response = {"Error": {"Code": "ValidationException", "Message": "Invalid request"}}
        client.client.invoke_model_with_response_stream = Mock(
            side_effect=ClientError(error_response, "InvokeModelWithResponseStream")
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            list(client.stream(prompt="Test"))
        
        assert "ValidationException" in str(exc_info.value)
    
    def test_stream_botocore_error(self, client):
        """Test handling of BotoCoreError during streaming."""
        client.client.invoke_model_with_response_stream = Mock(
            side_effect=BotoCoreError()
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            list(client.stream(prompt="Test"))
        
        assert "BotoCoreError" in str(exc_info.value)
    
    def test_stream_unexpected_error(self, client):
        """Test handling of unexpected errors during streaming."""
        client.client.invoke_model_with_response_stream = Mock(
            side_effect=RuntimeError("Unexpected streaming error")
        )
        
        with pytest.raises(BedrockClientError) as exc_info:
            list(client.stream(prompt="Test"))
        
        assert "Unexpected error during streaming" in str(exc_info.value)
    
    def test_stream_custom_parameters(self, client):
        """Test streaming with custom parameters."""
        mock_events = [
            {
                "chunk": {
                    "bytes": json.dumps({
                        "type": "content_block_delta",
                        "delta": {"type": "text_delta", "text": "Test"}
                    }).encode()
                }
            },
            {
                "chunk": {
                    "bytes": json.dumps({"type": "message_stop"}).encode()
                }
            },
        ]
        
        mock_response = {"body": iter(mock_events)}
        client.client.invoke_model_with_response_stream = Mock(return_value=mock_response)
        
        list(client.stream(
            prompt="Test",
            max_tokens=2000,
            temperature=0.3,
            top_p=0.95
        ))
        
        body = json.loads(
            client.client.invoke_model_with_response_stream.call_args[1]["body"]
        )
        assert body["max_tokens"] == 2000
        assert body["temperature"] == 0.3
        assert body["top_p"] == 0.95


@pytest.mark.integration
class TestBedrockClientIntegration:
    """
    Integration tests for BedrockClient.
    These tests are marked as 'integration' and require real AWS credentials.
    Run with: pytest -m integration
    """
    
    @pytest.mark.skip(reason="Requires real AWS credentials and incurs costs")
    def test_real_invoke(self):
        """Test real invocation (requires AWS credentials)."""
        client = BedrockClient()
        response = client.invoke(
            prompt="Say 'Hello' and nothing else.",
            max_tokens=10
        )
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.skip(reason="Requires real AWS credentials and incurs costs")
    def test_real_stream(self):
        """Test real streaming (requires AWS credentials)."""
        client = BedrockClient()
        tokens = list(client.stream(
            prompt="Count from 1 to 3.",
            max_tokens=50
        ))
        assert len(tokens) > 0
        full_response = "".join(tokens)
        assert len(full_response) > 0

