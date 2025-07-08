from typing import Optional, AsyncGenerator, Dict, List
import os
import uuid
from datetime import datetime
import google.generativeai as genai
import asyncio
import logging
import httpx
from config.models import get_model_config

# Import from base module to avoid circular imports
from agents.base import Agent
from app.services.unified_crypto_api import get_unified_api


class CryptoAdvisorAgent(Agent):
    """
    Crypto Advisor Agent provides expert guidance on cryptocurrency investments,
    market trends, and blockchain technologies.
    """
    
    def __init__(self, model_id=None, **kwargs):
        config = get_model_config("crypto_advisor")
        model_id = model_id or config["model_id"]
        super().__init__(
            name="Crypto Advisor Agent",
            agent_id="crypto_advisor",
            description="Expert guidance on cryptocurrency investments, market trends, and blockchain technologies",
        )
        
        # User info
        self.user_id = kwargs.get("user_id")
        self.session_id = kwargs.get("session_id")
        
        # Setup unified crypto API service
        self.unified_api = None  # Will be initialized when needed
        
        # API key setup for Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
            self.logger = logging.getLogger("crypto_advisor")
            self.api_configured = False
            self.model = None
            self.model_id = model_id
            return
        self.api_configured = True
        genai.configure(api_key=api_key)
        self.model_id = model_id
        self.model = genai.GenerativeModel(model_id)
        self.logger = logging.getLogger("crypto_advisor")
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
            
            # Process messages and augment with crypto data
            context_messages = await self._process_messages(messages)
            
            # Convert messages to format expected by Gemini
            content = self._format_messages_for_gemini(context_messages)
            
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
            
            # Process messages and augment with crypto data
            context_messages = await self._process_messages(messages)
            
            # Convert messages to format expected by Gemini
            content = self._format_messages_for_gemini(context_messages)
            
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
                try:
                    # Safely extract text from the chunk
                    chunk_text = ""
                    if hasattr(chunk, 'text'):
                        chunk_text = chunk.text
                    elif hasattr(chunk, 'parts') and len(chunk.parts) > 0:
                        chunk_text = chunk.parts[0].text
                    
                    if chunk_text:
                        yield {"content": chunk_text, "done": False}
                        # Small delay to prevent overwhelming the client
                        await asyncio.sleep(0.01)
                except Exception as chunk_error:
                    self.logger.error(f"Error processing stream chunk: {str(chunk_error)}")
                    # Continue with the stream rather than failing completely
            
            # Final chunk indicating end of stream
            yield {"content": "", "done": True}
            
        except Exception as e:
            self.logger.error(f"Error in streaming response: {str(e)}")
            # Handle errors in the stream
            yield {"error": str(e), "done": True}
    
    async def _process_messages(self, messages: List) -> List:
        """
        Process and augment messages with cryptocurrency data
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            List: Enhanced messages with crypto data context
        """
        # Clone the messages to avoid modifying the original
        enhanced_messages = messages.copy()
        
        # Check the last user message
        if len(messages) > 0 and messages[-1]["role"] == "user":
            user_query = messages[-1]["content"].lower()
            
            # Check if query contains cryptocurrency keywords
            crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "price", "crypto", "market", "coin", "token"]
            if any(keyword in user_query for keyword in crypto_keywords):
                # Fetch relevant crypto data
                crypto_data = await self._fetch_crypto_data(user_query)
                
                if crypto_data:
                    # Add crypto data as context to the user's message
                    enhanced_messages[-1]["content"] += f"\n\nCurrent Market Data (reference only): {crypto_data}"
            
        return enhanced_messages
    
    async def _fetch_crypto_data(self, query: str) -> Optional[str]:
        """
        Fetch cryptocurrency data based on the user query using unified API
        
        Args:
            query: User query
            
        Returns:
            String with cryptocurrency data if available
        """
        try:
            # Initialize unified API if not already done
            if self.unified_api is None:
                self.unified_api = await get_unified_api()
            
            # Identify specific cryptocurrencies in the query
            crypto_mapping = {
                "bitcoin": "bitcoin",
                "btc": "bitcoin", 
                "ethereum": "ethereum",
                "eth": "ethereum",
                "solana": "solana",
                "sol": "solana",
                "cardano": "cardano",
                "ada": "cardano",
                "bnb": "binancecoin",
                "xrp": "ripple",
            }
            
            # Default coins to fetch if no specific ones are mentioned
            coins_to_fetch = ["bitcoin", "ethereum", "solana"]
            
            # Check if query contains specific coins
            for key, value in crypto_mapping.items():
                if key in query and value not in coins_to_fetch:
                    coins_to_fetch.append(value)
            
            # Limit to top 5 coins
            coins_to_fetch = coins_to_fetch[:5]
            
            # Fetch data using unified API (CoinGecko)
            prices_data = await self.unified_api.get_prices_coingecko(coins_to_fetch, ["usd"])
            
            if prices_data:
                # Format data as a concise string
                data_points = []
                for coin_key, price_data in prices_data.items():
                    if "_usd" in coin_key:
                        coin_name = coin_key.replace("_usd", "")
                        price = price_data.price_usd
                        change_24h = price_data.price_change_24h or 0
                        market_cap = price_data.market_cap
                        
                        # Format price with appropriate decimal places
                        if price < 1:
                            price_str = f"${price:.6f}"
                        elif price < 10:
                            price_str = f"${price:.4f}"
                        elif price < 1000:
                            price_str = f"${price:.2f}"
                        else:
                            price_str = f"${price:,.2f}"
                        
                        # Format market cap
                        if market_cap and market_cap >= 1_000_000_000:
                            market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
                        elif market_cap:
                            market_cap_str = f"${market_cap / 1_000_000:.2f}M"
                        else:
                            market_cap_str = "N/A"
                        
                        # Create data point
                        data_point = (
                            f"{coin_name.title()}: "
                            f"{price_str} "
                            f"({'↑' if change_24h >= 0 else '↓'}{abs(change_24h):.2f}% 24h) "
                            f"Market Cap: {market_cap_str}"
                        )
                        data_points.append(data_point)
                
                # Try to get market overview for additional context
                try:
                    market_overview = await self.unified_api.get_market_overview()
                    if market_overview.get("market_summary"):
                        data_points.append("") # Add spacing
                        data_points.append("Market Overview:")
                        for coin_key, coin_data in market_overview["market_summary"].items():
                            if hasattr(coin_data, '__dict__'):
                                data_points.append(f"  {coin_data.symbol}: ${coin_data.price_usd:.2f}")
                except Exception:
                    pass  # Ignore if market overview fails
                
                # Format as a single string
                result = "\n".join(data_points)
                result += f"\n\nLast updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                
                return result
            
            return None
        except Exception as e:
            self.logger.error(f"Error fetching crypto data: {str(e)}")
            return None
    
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
            for message in messages:
                if hasattr(message, "dict"):
                    message_objects.append(message.dict())
                else:
                    message_objects.append(message)
                    
            # Format for Gemini
            for message in message_objects:
                role = message["role"].lower()
                content = message["content"]
                
                # Map roles from OpenAI format to Gemini format
                if role == "user":
                    gemini_role = "user"
                elif role == "assistant":
                    gemini_role = "model"
                elif role == "system":
                    # Gemini doesn't have system messages, we'll convert to user
                    gemini_role = "user"
                else:
                    # Skip unknown roles
                    continue
                
                # Create formatted message
                formatted_messages.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })
                
            return formatted_messages
        except Exception as e:
            self.logger.error(f"Error formatting messages: {str(e)}")
            # Return a simplified version in case of error
            return [{"role": "user", "parts": [{"text": "Hello, can you help me with cryptocurrency?"}]}]


def get_crypto_advisor_agent(
    model_id: str = "gemini-2.0-flash-lite",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Factory function to create a CryptoAdvisorAgent
    
    Args:
        model_id: ID of the model to use
        user_id: ID of the user
        session_id: ID of the session
        debug_mode: Whether to enable debug mode
        
    Returns:
        CryptoAdvisorAgent
    """
    return CryptoAdvisorAgent(
        model_id=model_id,
        user_id=user_id,
        session_id=session_id,
        debug_mode=debug_mode,
    )
