"""
Base Agent Class for FLUX Research System
Abstract base class for all research agents with Bedrock integration.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncGenerator
from loguru import logger

from flux_core.tools.bedrock_client import BedrockClient, BedrockClientError


class BaseAgent(ABC):
    """
    Abstract base class for all FLUX research agents.
    
    Provides common functionality:
    - Bedrock LLM integration
    - Message formatting with metadata
    - Conversation history tracking
    - Streaming response support
    - Error handling
    """
    
    def __init__(
        self,
        name: str,
        emoji: str,
        color: str,
        role: str,
        system_prompt: str,
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent display name (e.g., "The Current")
            emoji: Agent emoji identifier (e.g., 💡)
            color: Agent color theme (e.g., "cyan")
            role: Agent's primary role (e.g., "Hypothesis Generator")
            system_prompt: System prompt defining agent behavior
        """
        self.name = name
        self.emoji = emoji
        self.color = color
        self.role = role
        self.system_prompt = system_prompt
        
        # Initialize Bedrock client
        try:
            self.bedrock_client = BedrockClient()
            logger.info(f"Initialized {self.name} {self.emoji} - {self.role}")
        except BedrockClientError as e:
            logger.error(f"Failed to initialize Bedrock client for {self.name}: {e}")
            raise
        
        # Conversation history for this agent
        self.conversation_history: list[dict[str, Any]] = []
    
    async def invoke_model(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Invoke the LLM model and get a complete response.
        
        Args:
            prompt: User prompt for the model
            context: Optional context dictionary with additional information
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated response text
        
        Raises:
            BedrockClientError: If model invocation fails
        """
        try:
            # Build full prompt with context if provided
            full_prompt = self._build_prompt(prompt, context)
            
            logger.info(f"{self.name} invoking model with {len(full_prompt)} char prompt")
            logger.debug(f"{self.name} prompt preview: {full_prompt[:200]}...")
            
            # Invoke model
            response = self.bedrock_client.invoke(
                prompt=full_prompt,
                system_prompt=self.system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Track in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": full_prompt,
                "timestamp": datetime.utcnow().isoformat(),
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            logger.info(f"{self.name} received response: {len(response)} chars")
            return response
        
        except BedrockClientError as e:
            logger.error(f"{self.name} model invocation failed: {e}")
            raise
        except Exception as e:
            error_msg = f"{self.name} unexpected error during invocation: {e}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
    
    async def stream_response(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Stream the LLM response token by token.
        
        Args:
            prompt: User prompt for the model
            context: Optional context dictionary
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Yields:
            Response tokens as they are generated
        
        Raises:
            BedrockClientError: If streaming fails
        """
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            logger.info(f"{self.name} streaming response with {len(full_prompt)} char prompt")
            
            # Track prompt in history
            self.conversation_history.append({
                "role": "user",
                "content": full_prompt,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Stream response
            full_response = []
            for token in self.bedrock_client.stream(
                prompt=full_prompt,
                system_prompt=self.system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            ):
                full_response.append(token)
                yield token
            
            # Track complete response in history
            complete_response = "".join(full_response)
            self.conversation_history.append({
                "role": "assistant",
                "content": complete_response,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            logger.info(f"{self.name} completed streaming: {len(complete_response)} chars")
        
        except BedrockClientError as e:
            logger.error(f"{self.name} streaming failed: {e}")
            raise
        except Exception as e:
            error_msg = f"{self.name} unexpected error during streaming: {e}"
            logger.error(error_msg)
            raise BedrockClientError(error_msg) from e
    
    def format_message(
        self,
        content: str,
        message_type: str = "response",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Format a message with agent metadata.
        
        Args:
            content: Message content
            message_type: Type of message (e.g., "response", "analysis", "critique")
            metadata: Optional additional metadata
        
        Returns:
            Formatted message dictionary
        """
        message = {
            "agent": self.name,
            "emoji": self.emoji,
            "color": self.color,
            "role": self.role,
            "message": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        logger.debug(f"{self.name} formatted message: {message_type}")
        return message
    
    def get_conversation_history(self) -> list[dict[str, Any]]:
        """
        Get the conversation history for this agent.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history.clear()
        logger.debug(f"{self.name} conversation history cleared")
    
    def _build_prompt(self, prompt: str, context: dict[str, Any] | None) -> str:
        """
        Build full prompt with context if provided.
        
        Args:
            prompt: Base prompt
            context: Optional context dictionary
        
        Returns:
            Complete prompt string
        """
        if not context:
            return prompt
        
        # Build context section
        context_parts = []
        for key, value in context.items():
            if value is not None:
                context_parts.append(f"{key}: {value}")
        
        if not context_parts:
            return prompt
        
        context_str = "\n".join(context_parts)
        full_prompt = f"""Context:
{context_str}

{prompt}"""
        
        return full_prompt
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.name} {self.emoji} ({self.role})"
    
    def __str__(self) -> str:
        """String representation of agent."""
        return self.__repr__()

