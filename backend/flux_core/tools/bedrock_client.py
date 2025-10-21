"""
AWS Bedrock Client for Claude 3.5 Sonnet
Handles LLM invocation and streaming with error handling.
"""

import os
import json
import time
import asyncio
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
        profile_name: str | None = None,
        region_name: str | None = None,
        model_id: str | None = None,
    ):
        """
        Initialize the Bedrock client.
        
        Uses AWS profile for authentication (recommended) or falls back to
        environment variables or IAM role.
        
        Args:
            profile_name: AWS profile name from ~/.aws/credentials (defaults to env var AWS_PROFILE)
            region_name: AWS region (defaults to env var AWS_REGION or 'us-east-1')
            model_id: Bedrock model ID (defaults to env var AWS_BEDROCK_MODEL_ID)
        
        Raises:
            BedrockClientError: If AWS credentials cannot be found
        """
        
        # Get configuration from environment if not provided
        self.profile_name = profile_name or os.getenv("AWS_PROFILE")
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.model_id = model_id or os.getenv(
            "AWS_BEDROCK_MODEL_ID",
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        
        # Track token usage and cost
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        # Initialize boto3 client
        try:
            # Create session with profile if specified
            if self.profile_name:
                logger.info(f"Using AWS profile: {self.profile_name}")
                session = boto3.Session(
                    profile_name=self.profile_name,
                    region_name=self.region_name
                )
                self.client = session.client(service_name="bedrock-runtime")
            else:
                # Use default credential chain (env vars, IAM role, etc.)
                logger.info("Using AWS default credential chain")
                self.client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=self.region_name,
                )
            
            logger.info(f"Initialized Bedrock client in region: {self.region_name}")
            logger.info(f"Using model: {self.model_id}")
            
        except Exception as e:
            error_msg = f"Failed to initialize Bedrock client: {str(e)}"
            logger.error(error_msg)
            logger.error("Make sure you have configured AWS credentials:")
            logger.error("  1. Set AWS_PROFILE in .env to use a profile from ~/.aws/credentials")
            logger.error("  2. Or configure AWS CLI: aws configure")
            logger.error("  3. Or set AWS environment variables")
            logger.error("  4. Or use IAM role (if running on AWS)")
            raise BedrockClientError(error_msg) from e
    
    def invoke(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_retries: int = 5,
    ) -> str:
        """
        Invoke the model and get a complete response with automatic retry on throttling.
        
        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            max_retries: Maximum number of retries for throttling (default: 5)
        
        Returns:
            The generated text response
        
        Raises:
            BedrockClientError: If invocation fails after all retries
        """
        
        # Construct the request body (outside retry loop)
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
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
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
                    
                    # Track usage metrics
                    usage = response_body.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    
                    # Update cumulative tracking
                    self.total_input_tokens += input_tokens
                    self.total_output_tokens += output_tokens
                    
                    # Calculate cost (Claude 3.5 Sonnet pricing)
                    # Input: $3 per 1M tokens, Output: $15 per 1M tokens
                    input_cost = (input_tokens / 1_000_000) * 3.0
                    output_cost = (output_tokens / 1_000_000) * 15.0
                    invocation_cost = input_cost + output_cost
                    self.total_cost += invocation_cost
                    
                    logger.info(f"Tokens used: {input_tokens} input, {output_tokens} output (${invocation_cost:.4f})")
                    
                    # Success! Return the result
                    if attempt > 0:
                        logger.info(f"✅ Successfully invoked after {attempt + 1} attempts")
                    return text
                else:
                    error_msg = "No content in model response"
                    logger.error(error_msg)
                    raise BedrockClientError(error_msg)
            
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                
                # Handle throttling with exponential backoff
                if error_code == "ThrottlingException" and attempt < max_retries - 1:
                    # Calculate backoff delay: 2^attempt seconds (2, 4, 8, 16, 32)
                    delay = 2 ** (attempt + 1)
                    logger.warning(
                        f"⚠️ Throttled by AWS Bedrock (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    continue  # Retry
                
                # If not throttling or last attempt, raise error
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
        
        # Should never reach here, but just in case
        raise BedrockClientError(f"Max retries ({max_retries}) exceeded for model invocation")
    
    def get_usage_stats(self) -> dict[str, Any]:
        """
        Get current token usage and cost statistics.
        
        Returns:
            Dictionary with token and cost stats
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,
        }
    
    def reset_usage_stats(self):
        """Reset token usage and cost tracking."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
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

