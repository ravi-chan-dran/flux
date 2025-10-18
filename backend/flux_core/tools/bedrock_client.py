"""
AWS Bedrock Client for Claude 3.5 Sonnet
Handles LLM invocation and streaming with error handling.
"""

import os
import json
from typing import Generator, Any
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from loguru import logger


class BedrockClientError(Exception):
    """Custom exception for Bedrock client errors."""
    pass


class BedrockClient:
    """
    Client wrapper for AWS Bedrock Runtime API.
    
    Provides methods for invoking Claude 3.5 Sonnet with both
    standard and streaming responses.
    """
    
    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
        model_id: str | None = None,
    ):
        """
        Initialize the Bedrock client.
        
        Args:
            aws_access_key_id: AWS access key (defaults to env var AWS_ACCESS_KEY_ID)
            aws_secret_access_key: AWS secret key (defaults to env var AWS_SECRET_ACCESS_KEY)
            region_name: AWS region (defaults to env var AWS_REGION or 'us-east-1')
            model_id: Bedrock model ID (defaults to env var AWS_BEDROCK_MODEL_ID)
        
        Raises:
            BedrockClientError: If AWS credentials are missing
        """
        
        # Get configuration from environment if not provided
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.model_id = model_id or os.getenv(
            "AWS_BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        
        # Validate credentials
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            error_msg = "AWS credentials not provided. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            logger.error(error_msg)
            raise BedrockClientError(error_msg)
        
        # Initialize boto3 client
        try:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
            logger.info(f"Initialized Bedrock client in region: {self.region_name}")
            logger.info(f"Using model: {self.model_id}")
        except Exception as e:
            error_msg = f"Failed to initialize Bedrock client: {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
    
    def invoke(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Invoke the model and get a complete response.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
        
        Returns:
            The generated text response
        
        Raises:
            BedrockClientError: If invocation fails
        """
        
        try:
            # Construct the request body
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt
            
            logger.debug(f"Invoking model: {self.model_id}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            # Extract text from response
            if "content" in response_body and len(response_body["content"]) > 0:
                text = response_body["content"][0]["text"]
                
                # Log usage metrics
                usage = response_body.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                logger.info(f"Tokens used: {input_tokens} input, {output_tokens} output")
                
                return text
            else:
                error_msg = "No content in model response"
                logger.error(error_msg)
                raise BedrockClientError(error_msg)
        
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = f"AWS ClientError ({error_code}): {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
        
        except BotoCoreError as e:
            error_msg = f"BotoCoreError: {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
        
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse response JSON: {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error during invocation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise BedrockClientError(error_msg) from e
    
    def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> Generator[str, None, None]:
        """
        Stream the model response token by token.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
        
        Yields:
            Tokens as they are generated
        
        Raises:
            BedrockClientError: If streaming fails
        """
        
        try:
            # Construct the request body
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt
            
            logger.debug(f"Streaming from model: {self.model_id}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Invoke the model with streaming
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(request_body),
            )
            
            # Process the event stream
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        try:
                            chunk_data = json.loads(chunk.get("bytes").decode())
                            
                            # Handle different event types
                            event_type = chunk_data.get("type")
                            
                            if event_type == "content_block_delta":
                                delta = chunk_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                            
                            elif event_type == "message_stop":
                                logger.debug("Stream completed")
                                break
                            
                            elif event_type == "error":
                                error_msg = chunk_data.get("error", {}).get("message", "Unknown error")
                                logger.error(f"Stream error: {error_msg}")
                                raise BedrockClientError(f"Stream error: {error_msg}")
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to decode chunk: {e}")
                            continue
        
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = f"AWS ClientError ({error_code}): {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
        
        except BotoCoreError as e:
            error_msg = f"BotoCoreError: {str(e)}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error during streaming: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise BedrockClientError(error_msg) from e

