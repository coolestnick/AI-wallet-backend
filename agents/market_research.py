from typing import Optional, AsyncGenerator, Dict, List
import os
import uuid
from datetime import datetime
import google.generativeai as genai
import asyncio
import logging
from config.models import get_model_config

# Import from base module to avoid circular imports
from agents.base import Agent


class MarketResearchAgent(Agent):
    """
    Market Research Agent provides analysis on cryptocurrency market trends
    and insights into token performance.
    """
    
    def __init__(self, model_id=None, **kwargs):
        config = get_model_config("research")
        model_id = model_id or config["model_id"]
        super().__init__(
            name="Market Research Agent",
            agent_id="market_research",
            description="Expert analysis on cryptocurrency market trends, token performance, and industry insights",
        )
        
        # Configure Google Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
            # Still create a logger, but the agent won't work for API calls
            self.logger = logging.getLogger("market_research")
            self.api_configured = False
            self.model = None
            self.model_id = model_id
            return
            
        # API key is available, configure the Gemini client
        self.api_configured = True
        genai.configure(api_key=api_key)
        
        # Initialize the model based on the requested model_id
        self.model_id = model_id
        self.model = genai.GenerativeModel(model_id)
        
        # Set up logging
        self.logger = logging.getLogger("market_research")
        
        # Set up the agent configuration
        self.config = {
            "temperature": config["temperature"],
            "max_output_tokens": config["max_output_tokens"],
            "system_prompt": config["system_prompt"],
        }
    
    async def generate_response(self, messages: List, **kwargs):
        """
        Generate a non-streaming response
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            dict: Response message with role and content
        """
        try:
            # Check if API is configured
            if not getattr(self, 'api_configured', False):
                return {
                    "role": "assistant",
                    "content": "I'm sorry, but I can't process your request because the GEMINI_API_KEY is missing. Please add your Gemini API key to the .env file and restart the server.",
                }
            
            # Convert messages to format expected by Gemini
            content = self._format_messages_for_gemini(messages)
            
            # Log the formatted content
            self.logger.info(f"Sending to Gemini: {content}")
            
            # Generate response using Google Gemini
            generation_config = {
                "temperature": self.config["temperature"],
                "max_output_tokens": self.config["max_output_tokens"],
            }
            
            # Add system prompt if available - we need to prepend it to the conversation
            if self.config.get("system_prompt") and isinstance(content, list) and len(content) > 0:
                # For Gemini, we add the system prompt as a user message at the beginning
                system_content = [{
                    'role': 'user', 
                    'parts': [{'text': self.config["system_prompt"]}]
                }]
                # Add a model response to acknowledge the system prompt
                system_content.append({
                    'role': 'model',
                    'parts': [{'text': 'I understand and will follow these instructions.'}]
                })
                # Combine with the actual conversation
                content = system_content + content
            
            # Generate response
            response = await self.model.generate_content_async(
                content,
                generation_config=generation_config
            )
            
            # Return formatted response
            return {
                "role": "assistant",
                "content": response.text,
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            # Handle errors gracefully
            return {
                "role": "assistant",
                "content": f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}",
            }
    
    async def generate_streaming_response(self, messages: List, **kwargs) -> AsyncGenerator[Dict, None]:
        """
        Generate a streaming response using Gemini
        
        Args:
            messages: List of message objects with role and content
            
        Yields:
            dict: Chunks of the response with content and done flag
        """
        try:
            # Check if API is configured
            if not getattr(self, 'api_configured', False):
                yield {
                    "content": "I'm sorry, but I can't process your request because the GEMINI_API_KEY is missing. ",
                    "done": False
                }
                yield {
                    "content": "Please add your Gemini API key to the .env file and restart the server.",
                    "done": False
                }
                yield {"content": "", "done": True}
                return
            
            # Convert messages to format expected by Gemini
            content = self._format_messages_for_gemini(messages)
            
            # Log the formatted content
            self.logger.info(f"Sending to Gemini (streaming): {content}")
            
            # Prepare generation config
            generation_config = {
                "temperature": self.config["temperature"],
                "max_output_tokens": self.config["max_output_tokens"],
            }
            
            # Add system prompt if available - we need to prepend it to the conversation
            if self.config.get("system_prompt") and isinstance(content, list) and len(content) > 0:
                # For Gemini, we add the system prompt as a user message at the beginning
                system_content = [{
                    'role': 'user', 
                    'parts': [{'text': self.config["system_prompt"]}]
                }]
                # Add a model response to acknowledge the system prompt
                system_content.append({
                    'role': 'model',
                    'parts': [{'text': 'I understand and will follow these instructions.'}]
                })
                # Combine with the actual conversation
                content = system_content + content
            
            # Generate streaming response
            stream = await self.model.generate_content_async(
                content,
                generation_config=generation_config,
                stream=True
            )
            
            # Get content from each chunk and yield it
            async for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield {"content": chunk.text, "done": False}
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)
            
            # Final chunk indicating end of stream
            yield {"content": "", "done": True}
            
        except Exception as e:
            self.logger.error(f"Error in streaming response: {str(e)}")
            # Handle errors in the stream
            yield {"error": str(e), "done": True}
    
    def _format_messages_for_gemini(self, messages):
        """
        Format messages for Gemini API
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            list: Formatted messages for Gemini
        """
        try:
            # For Gemini, we need to format messages as a conversation
            formatted_messages = []
            
            # Convert Pydantic models to dicts if necessary
            message_objects = []
            for msg in messages:
                if hasattr(msg, 'dict'):
                    message_objects.append(msg.dict())
                elif hasattr(msg, 'model_dump'):
                    message_objects.append(msg.model_dump())
                else:
                    message_objects.append(msg)
            
            # Format as Gemini content parts
            for msg in message_objects:
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role == 'user':
                    formatted_messages.append(
                        {'role': 'user', 'parts': [{'text': content}]}
                    )
                elif role == 'assistant':
                    formatted_messages.append(
                        {'role': 'model', 'parts': [{'text': content}]}
                    )
                elif role == 'system':
                    # System messages might be handled differently
                    # For Gemini, we typically use system_instructions in the generation config
                    pass
            
            # If we have a properly formatted conversation with at least one message
            if formatted_messages:
                return formatted_messages
            
            # Fallback to just sending the last user message text directly
            for msg in reversed(message_objects):
                if msg.get('role') == 'user':
                    return msg.get('content', '')
            
            # Final fallback
            return "Hello, how can I help you with cryptocurrency market research today?"
            
        except Exception as e:
            self.logger.error(f"Error formatting messages: {str(e)}")
            # If there's an error in formatting, return a simple prompt
            return "Hello, how can I help you with cryptocurrency market research today?"


def get_market_research_agent(
    model_id: str = "gemini-2.0-flash-lite",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """Get a Market Research agent"""
    return MarketResearchAgent(
        model_id=model_id,
        user_id=user_id,
        session_id=session_id,
        debug_mode=debug_mode,
    )
