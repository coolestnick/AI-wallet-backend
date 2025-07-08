from typing import Optional, AsyncGenerator, Dict, List
import os
import uuid
import json
from datetime import datetime
import google.generativeai as genai
import asyncio
import logging
from config.models import get_model_config
from app.services.firecrawl_service import firecrawl_service

# Import from base module to avoid circular imports
from agents.base import Agent


class FirecrawlResearchAgent(Agent):
    """
    Firecrawl Research Agent provides comprehensive market research using web scraping
    capabilities to gather real-time information from various crypto sources.
    """
    
    def __init__(self, model_id=None, **kwargs):
        config = get_model_config("research")
        model_id = model_id or config["model_id"]
        super().__init__(
            name="Firecrawl Research Agent",
            agent_id="firecrawl_research",
            description="Advanced crypto market research using real-time web scraping and AI analysis",
        )
        
        # Configure Google Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
            self.logger = logging.getLogger("firecrawl_research")
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
        self.logger = logging.getLogger("firecrawl_research")
        
        # Enhanced system prompt for research agent
        research_system_prompt = """You are a specialized cryptocurrency market research agent with access to real-time web scraping capabilities. 

Your role is to:
1. Analyze user queries to determine what crypto research is needed
2. Use web scraping tools to gather current market information
3. Synthesize multiple sources into comprehensive research reports
4. Provide actionable insights based on current market conditions
5. Identify trends, opportunities, and risks in the crypto space

When responding to queries:
- Always use current, scraped data when available
- Cite your sources and mention when information was gathered
- Provide balanced analysis covering both opportunities and risks
- Structure responses clearly with headers and bullet points
- Include relevant metrics, prices, and market data
- Distinguish between factual data and analytical opinions

Research capabilities include:
- Real-time news and article scraping
- DeFi protocol analysis
- Social sentiment tracking
- Cross-platform market data aggregation
- Token and project research

Always be transparent about data sources and limitations."""
        
        # Set up the agent configuration
        self.config = {
            "temperature": config["temperature"],
            "max_output_tokens": config["max_output_tokens"],
            "system_prompt": research_system_prompt,
        }
        
        # Initialize Firecrawl service
        self.firecrawl_service = firecrawl_service
    
    async def _gather_research_data(self, query: str, research_type: str = "general") -> Dict:
        """
        Gather research data based on query and type
        
        Args:
            query: User's research query
            research_type: Type of research to conduct
            
        Returns:
            Dictionary containing gathered research data
        """
        research_data = {
            "news_articles": [],
            "defi_data": [],
            "social_sentiment": [],
            "query": query,
            "research_type": research_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.firecrawl_service.is_configured():
            self.logger.warning("Firecrawl service not configured, using basic research")
            return research_data
        
        try:
            # Determine what data to gather based on query
            query_lower = query.lower()
            
            # Always gather news for crypto queries
            if any(keyword in query_lower for keyword in ['crypto', 'bitcoin', 'ethereum', 'defi', 'nft', 'token']):
                self.logger.info(f"Gathering crypto news for query: {query}")
                news_data = await self.firecrawl_service.search_crypto_news(query)
                research_data["news_articles"] = news_data
            
            # Gather DeFi data if relevant
            if any(keyword in query_lower for keyword in ['defi', 'yield', 'liquidity', 'protocol', 'tvl']):
                self.logger.info("Gathering DeFi protocol data")
                defi_data = await self.firecrawl_service.scrape_defi_data()
                research_data["defi_data"] = defi_data
            
            # Gather social sentiment for specific tokens
            token_keywords = ['btc', 'eth', 'sol', 'ada', 'dot', 'link', 'uni', 'aave']
            mentioned_tokens = [token for token in token_keywords if token in query_lower]
            
            if mentioned_tokens or 'sentiment' in query_lower:
                self.logger.info(f"Gathering social sentiment for tokens: {mentioned_tokens}")
                sentiment_data = await self.firecrawl_service.scrape_social_sentiment(mentioned_tokens if mentioned_tokens else None)
                research_data["social_sentiment"] = sentiment_data
            
        except Exception as e:
            self.logger.error(f"Error gathering research data: {str(e)}")
            research_data["error"] = str(e)
        
        return research_data
    
    async def _format_research_context(self, research_data: Dict) -> str:
        """
        Format research data into context for the AI model
        
        Args:
            research_data: Dictionary containing research data
            
        Returns:
            Formatted string for AI context
        """
        context_parts = []
        
        # Add timestamp
        context_parts.append(f"Research conducted at: {research_data['timestamp']}")
        context_parts.append(f"Query: {research_data['query']}")
        context_parts.append("")
        
        # Add news articles
        if research_data.get("news_articles"):
            context_parts.append("=== RECENT NEWS ARTICLES ===")
            for i, article in enumerate(research_data["news_articles"][:5]):  # Limit to 5 articles
                context_parts.append(f"Article {i+1}:")
                context_parts.append(f"Source: {article.get('source', 'Unknown')}")
                context_parts.append(f"Title: {article.get('title', 'Unknown')}")
                # Truncate content to avoid overwhelming the model
                content = article.get('content', '')
                if len(content) > 1000:
                    content = content[:1000] + "..."
                context_parts.append(f"Content: {content}")
                context_parts.append("")
        
        # Add DeFi data
        if research_data.get("defi_data"):
            context_parts.append("=== DEFI PROTOCOL DATA ===")
            for i, defi in enumerate(research_data["defi_data"][:3]):  # Limit to 3 sources
                context_parts.append(f"DeFi Source {i+1}:")
                context_parts.append(f"Source: {defi.get('source', 'Unknown')}")
                if defi.get('data', {}).get('markdown'):
                    content = defi['data']['markdown']
                    if len(content) > 800:
                        content = content[:800] + "..."
                    context_parts.append(f"Data: {content}")
                context_parts.append("")
        
        # Add social sentiment
        if research_data.get("social_sentiment"):
            context_parts.append("=== SOCIAL SENTIMENT DATA ===")
            for i, sentiment in enumerate(research_data["social_sentiment"][:3]):  # Limit to 3 sources
                context_parts.append(f"Sentiment Source {i+1}:")
                context_parts.append(f"Source: {sentiment.get('source', 'Unknown')}")
                context_parts.append(f"Title: {sentiment.get('title', 'Unknown')}")
                if sentiment.get('tokens_mentioned'):
                    context_parts.append(f"Tokens mentioned: {', '.join(sentiment['tokens_mentioned'])}")
                # Truncate content
                content = sentiment.get('content', '')
                if len(content) > 600:
                    content = content[:600] + "..."
                context_parts.append(f"Content: {content}")
                context_parts.append("")
        
        # Add error information if any
        if research_data.get("error"):
            context_parts.append("=== RESEARCH LIMITATIONS ===")
            context_parts.append(f"Note: Some data gathering encountered issues: {research_data['error']}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def generate_response(self, messages: List, **kwargs):
        """
        Generate a non-streaming response with research data
        
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
            
            # Extract the latest user message for research
            user_message = ""
            for msg in reversed(messages):
                if hasattr(msg, 'dict'):
                    msg_dict = msg.dict()
                elif hasattr(msg, 'model_dump'):
                    msg_dict = msg.model_dump()
                else:
                    msg_dict = msg
                
                if msg_dict.get('role') == 'user':
                    user_message = msg_dict.get('content', '')
                    break
            
            # Gather research data
            self.logger.info(f"Starting research for query: {user_message}")
            research_data = await self._gather_research_data(user_message)
            
            # Format research context
            research_context = await self._format_research_context(research_data)
            
            # Create enhanced messages with research context
            enhanced_messages = []
            
            # Add system prompt with research context
            system_message = f"{self.config['system_prompt']}\n\n=== CURRENT RESEARCH DATA ===\n{research_context}"
            enhanced_messages.append({
                'role': 'user',
                'parts': [{'text': system_message}]
            })
            enhanced_messages.append({
                'role': 'model',
                'parts': [{'text': 'I understand. I will use this research data to provide comprehensive analysis.'}]
            })
            
            # Add original conversation
            formatted_messages = self._format_messages_for_gemini(messages)
            enhanced_messages.extend(formatted_messages)
            
            # Generate response using Google Gemini
            generation_config = {
                "temperature": self.config["temperature"],
                "max_output_tokens": self.config["max_output_tokens"],
            }
            
            response = await self.model.generate_content_async(
                enhanced_messages,
                generation_config=generation_config
            )
            
            # Return formatted response
            return {
                "role": "assistant",
                "content": response.text,
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                "role": "assistant",
                "content": f"I apologize, but I encountered an error while conducting research. Please try again later. Error: {str(e)}",
            }
    
    async def generate_streaming_response(self, messages: List, **kwargs) -> AsyncGenerator[Dict, None]:
        """
        Generate a streaming response with research data
        
        Args:
            messages: List of message objects with role and content
            
        Yields:
            dict: Chunks of the response with content and done flag
        """
        try:
            # Check if API is configured
            if not getattr(self, 'api_configured', False):
                yield {"content": "I'm sorry, but I can't process your request because the GEMINI_API_KEY is missing. ", "done": False}
                yield {"content": "Please add your Gemini API key to the .env file and restart the server.", "done": False}
                yield {"content": "", "done": True}
                return
            
            # Extract the latest user message for research
            user_message = ""
            for msg in reversed(messages):
                if hasattr(msg, 'dict'):
                    msg_dict = msg.dict()
                elif hasattr(msg, 'model_dump'):
                    msg_dict = msg.model_dump()
                else:
                    msg_dict = msg
                
                if msg_dict.get('role') == 'user':
                    user_message = msg_dict.get('content', '')
                    break
            
            # Notify user that research is starting
            yield {"content": "🔍 Starting comprehensive market research...\n\n", "done": False}
            
            # Gather research data
            self.logger.info(f"Starting research for query: {user_message}")
            research_data = await self._gather_research_data(user_message)
            
            # Notify about research completion
            news_count = len(research_data.get("news_articles", []))
            defi_count = len(research_data.get("defi_data", []))
            sentiment_count = len(research_data.get("social_sentiment", []))
            
            yield {"content": f"✅ Research incomplete! Gathered {news_count} news sources, {defi_count} DeFi sources, and {sentiment_count} sentiment sources.\n\n", "done": False}
            
            # Format research context
            research_context = await self._format_research_context(research_data)
            
            # Create enhanced messages with research context
            enhanced_messages = []
            
            # Add system prompt with research context
            system_message = f"{self.config['system_prompt']}\n\n=== CURRENT RESEARCH DATA ===\n{research_context}"
            enhanced_messages.append({
                'role': 'user',
                'parts': [{'text': system_message}]
            })
            enhanced_messages.append({
                'role': 'model',
                'parts': [{'text': 'I understand. I will use this research data to provide comprehensive analysis.'}]
            })
            
            # Add original conversation
            formatted_messages = self._format_messages_for_gemini(messages)
            enhanced_messages.extend(formatted_messages)
            
            # Generate streaming response
            generation_config = {
                "temperature": self.config["temperature"],
                "max_output_tokens": self.config["max_output_tokens"],
            }
            
            stream = await self.model.generate_content_async(
                enhanced_messages,
                generation_config=generation_config,
                stream=True
            )
            
            # Stream the response
            async for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield {"content": chunk.text, "done": False}
                    await asyncio.sleep(0.01)
            
            # Final chunk indicating end of stream
            yield {"content": "", "done": True}
            
        except Exception as e:
            self.logger.error(f"Error in streaming response: {str(e)}")
            yield {"content": f"\n\n❌ Error conducting research: {str(e)}", "done": False}
            yield {"content": "", "done": True}
    
    def _format_messages_for_gemini(self, messages):
        """
        Format messages for Gemini API
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            list: Formatted messages for Gemini
        """
        try:
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
                    # System messages handled separately
                    pass
            
            # If we have a properly formatted conversation
            if formatted_messages:
                return formatted_messages
            
            # Fallback to just sending the last user message
            for msg in reversed(message_objects):
                if msg.get('role') == 'user':
                    return [{'role': 'user', 'parts': [{'text': msg.get('content', '')}]}]
            
            # Final fallback
            return [{'role': 'user', 'parts': [{'text': 'Hello, how can I help you with crypto market research?'}]}]
            
        except Exception as e:
            self.logger.error(f"Error formatting messages: {str(e)}")
            return [{'role': 'user', 'parts': [{'text': 'Hello, how can I help you with crypto market research?'}]}]


def get_firecrawl_research_agent(
    model_id: str = "gemini-2.0-flash-lite",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """Get a Firecrawl Research agent"""
    return FirecrawlResearchAgent(
        model_id=model_id,
        user_id=user_id,
        session_id=session_id,
        debug_mode=debug_mode,
    )