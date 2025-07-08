import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from agents.firecrawl_research import FirecrawlResearchAgent
from app.services.firecrawl_service import FirecrawlService


class TestFirecrawlResearchAgent:
    """Test suite for the Firecrawl Research Agent"""
    
    @pytest.fixture
    def mock_firecrawl_service(self):
        """Mock Firecrawl service for testing"""
        service = AsyncMock(spec=FirecrawlService)
        service.is_configured.return_value = True
        service.search_crypto_news.return_value = [
            {
                'source': 'https://coindesk.com',
                'content': 'Bitcoin price rises to new highs amid institutional adoption',
                'title': 'Bitcoin Hits New ATH',
                'url': 'https://coindesk.com/bitcoin-ath',
                'query_match': True
            }
        ]
        service.scrape_defi_data.return_value = [
            {
                'source': 'https://defillama.com',
                'data': {
                    'markdown': 'Total Value Locked across DeFi protocols reaches $50B',
                    'timestamp': '2024-01-15T10:00:00Z'
                }
            }
        ]
        service.scrape_social_sentiment.return_value = [
            {
                'source': 'https://cryptopanic.com',
                'content': 'Community sentiment around BTC remains bullish',
                'title': 'BTC Sentiment Update',
                'tokens_mentioned': ['BTC']
            }
        ]
        return service
    
    @pytest.fixture
    def mock_gemini_model(self):
        """Mock Gemini model for testing"""
        model = AsyncMock()
        model.generate_content_async.return_value = MagicMock(
            text="Based on recent market research, Bitcoin shows strong bullish momentum..."
        )
        return model
    
    @pytest.fixture
    def research_agent(self, mock_firecrawl_service, mock_gemini_model):
        """Create a research agent with mocked dependencies"""
        with patch('agents.firecrawl_research.firecrawl_service', mock_firecrawl_service):
            with patch('agents.firecrawl_research.genai.GenerativeModel', return_value=mock_gemini_model):
                with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
                    agent = FirecrawlResearchAgent(model_id="gemini-2.0-flash-lite")
                    agent.firecrawl_service = mock_firecrawl_service
                    return agent
    
    def test_agent_initialization(self, research_agent):
        """Test agent initialization"""
        assert research_agent.name == "Firecrawl Research Agent"
        assert research_agent.agent_id == "firecrawl_research"
        assert "crypto market research" in research_agent.description.lower()
        assert research_agent.api_configured == True
    
    def test_agent_initialization_no_api_key(self):
        """Test agent initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = FirecrawlResearchAgent()
            assert agent.api_configured == False
            assert agent.model is None
    
    @pytest.mark.asyncio
    async def test_gather_research_data_crypto_query(self, research_agent, mock_firecrawl_service):
        """Test gathering research data for crypto query"""
        query = "What's the latest on Bitcoin and Ethereum?"
        
        research_data = await research_agent._gather_research_data(query)
        
        assert research_data["query"] == query
        assert research_data["research_type"] == "general"
        assert len(research_data["news_articles"]) > 0
        assert research_data["news_articles"][0]["source"] == "https://coindesk.com"
        
        # Verify service methods were called
        mock_firecrawl_service.search_crypto_news.assert_called_once_with(query)
    
    @pytest.mark.asyncio
    async def test_gather_research_data_defi_query(self, research_agent, mock_firecrawl_service):
        """Test gathering research data for DeFi query"""
        query = "Analyze current DeFi protocols and TVL"
        
        research_data = await research_agent._gather_research_data(query)
        
        assert len(research_data["defi_data"]) > 0
        assert research_data["defi_data"][0]["source"] == "https://defillama.com"
        
        # Verify service methods were called
        mock_firecrawl_service.search_crypto_news.assert_called_once()
        mock_firecrawl_service.scrape_defi_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_gather_research_data_sentiment_query(self, research_agent, mock_firecrawl_service):
        """Test gathering research data for sentiment query"""
        query = "What's the sentiment around BTC and ETH?"
        
        research_data = await research_agent._gather_research_data(query)
        
        assert len(research_data["social_sentiment"]) > 0
        assert research_data["social_sentiment"][0]["tokens_mentioned"] == ["BTC"]
        
        # Verify service methods were called
        mock_firecrawl_service.scrape_social_sentiment.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_gather_research_data_firecrawl_not_configured(self, research_agent):
        """Test gathering research data when Firecrawl is not configured"""
        research_agent.firecrawl_service.is_configured.return_value = False
        
        research_data = await research_agent._gather_research_data("test query")
        
        assert research_data["news_articles"] == []
        assert research_data["defi_data"] == []
        assert research_data["social_sentiment"] == []
    
    @pytest.mark.asyncio
    async def test_format_research_context(self, research_agent):
        """Test formatting research context"""
        research_data = {
            "query": "Bitcoin analysis",
            "timestamp": "2024-01-15T10:00:00Z",
            "news_articles": [
                {
                    "source": "https://coindesk.com",
                    "title": "Bitcoin News",
                    "content": "Bitcoin price content..."
                }
            ],
            "defi_data": [
                {
                    "source": "https://defillama.com",
                    "data": {"markdown": "DeFi TVL data..."}
                }
            ],
            "social_sentiment": [
                {
                    "source": "https://cryptopanic.com",
                    "title": "Sentiment Update",
                    "content": "Bullish sentiment...",
                    "tokens_mentioned": ["BTC"]
                }
            ]
        }
        
        context = await research_agent._format_research_context(research_data)
        
        assert "Bitcoin analysis" in context
        assert "2024-01-15T10:00:00Z" in context
        assert "=== RECENT NEWS ARTICLES ===" in context
        assert "=== DEFI PROTOCOL DATA ===" in context
        assert "=== SOCIAL SENTIMENT DATA ===" in context
        assert "coindesk.com" in context
        assert "defillama.com" in context
        assert "cryptopanic.com" in context
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, research_agent, mock_firecrawl_service):
        """Test successful response generation"""
        messages = [
            {"role": "user", "content": "What's the latest on Bitcoin?"}
        ]
        
        response = await research_agent.generate_response(messages)
        
        assert response["role"] == "assistant"
        assert "Bitcoin" in response["content"] or "bullish" in response["content"]
        
        # Verify research was conducted
        mock_firecrawl_service.search_crypto_news.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_no_api_key(self, mock_firecrawl_service):
        """Test response generation without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = FirecrawlResearchAgent()
            agent.firecrawl_service = mock_firecrawl_service
            
            messages = [{"role": "user", "content": "Test query"}]
            response = await agent.generate_response(messages)
            
            assert response["role"] == "assistant"
            assert "GEMINI_API_KEY is missing" in response["content"]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_response_success(self, research_agent, mock_firecrawl_service):
        """Test successful streaming response generation"""
        messages = [
            {"role": "user", "content": "Analyze Bitcoin market trends"}
        ]
        
        # Mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(text="Bitcoin analysis: "),
                MagicMock(text="shows strong momentum"),
                MagicMock(text=" with institutional adoption")
            ]
            for chunk in chunks:
                yield chunk
        
        research_agent.model.generate_content_async.return_value = mock_stream()
        
        response_chunks = []
        async for chunk in research_agent.generate_streaming_response(messages):
            response_chunks.append(chunk)
        
        # Should have research status updates and content chunks
        assert len(response_chunks) > 3  # At least research updates + content + done
        
        # Check for research status updates
        research_updates = [chunk for chunk in response_chunks if "research" in chunk.get("content", "").lower()]
        assert len(research_updates) >= 2  # Starting and completion messages
        
        # Check for final done chunk
        done_chunks = [chunk for chunk in response_chunks if chunk.get("done", False)]
        assert len(done_chunks) == 1
    
    @pytest.mark.asyncio
    async def test_generate_streaming_response_no_api_key(self, mock_firecrawl_service):
        """Test streaming response generation without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = FirecrawlResearchAgent()
            agent.firecrawl_service = mock_firecrawl_service
            
            messages = [{"role": "user", "content": "Test query"}]
            
            chunks = []
            async for chunk in agent.generate_streaming_response(messages):
                chunks.append(chunk)
            
            # Should have error message chunks
            assert len(chunks) >= 2  # Error message + done
            assert any("GEMINI_API_KEY is missing" in chunk.get("content", "") for chunk in chunks)
            assert chunks[-1].get("done", False) == True
    
    def test_format_messages_for_gemini(self, research_agent):
        """Test message formatting for Gemini API"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        formatted = research_agent._format_messages_for_gemini(messages)
        
        assert len(formatted) == 3
        assert formatted[0]["role"] == "user"
        assert formatted[0]["parts"][0]["text"] == "Hello"
        assert formatted[1]["role"] == "model"
        assert formatted[1]["parts"][0]["text"] == "Hi there!"
        assert formatted[2]["role"] == "user"
        assert formatted[2]["parts"][0]["text"] == "How are you?"
    
    def test_format_messages_for_gemini_with_pydantic(self, research_agent):
        """Test message formatting with Pydantic models"""
        # Mock Pydantic-like objects
        class MockMessage:
            def __init__(self, role, content):
                self.role = role
                self.content = content
            
            def dict(self):
                return {"role": self.role, "content": self.content}
        
        messages = [
            MockMessage("user", "Test message"),
            MockMessage("assistant", "Test response")
        ]
        
        formatted = research_agent._format_messages_for_gemini(messages)
        
        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[0]["parts"][0]["text"] == "Test message"
        assert formatted[1]["role"] == "model"
        assert formatted[1]["parts"][0]["text"] == "Test response"
    
    def test_format_messages_for_gemini_empty_messages(self, research_agent):
        """Test message formatting with empty messages"""
        messages = []
        
        formatted = research_agent._format_messages_for_gemini(messages)
        
        assert len(formatted) == 1
        assert formatted[0]["role"] == "user"
        assert "crypto market research" in formatted[0]["parts"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_error_handling_in_research(self, research_agent, mock_firecrawl_service):
        """Test error handling during research data gathering"""
        # Make service methods raise exceptions
        mock_firecrawl_service.search_crypto_news.side_effect = Exception("API Error")
        
        query = "Bitcoin analysis"
        research_data = await research_agent._gather_research_data(query)
        
        assert research_data["error"] == "API Error"
        assert research_data["news_articles"] == []
    
    @pytest.mark.asyncio
    async def test_token_extraction_from_query(self, research_agent, mock_firecrawl_service):
        """Test token extraction from user queries"""
        query = "What's the sentiment around BTC and ETH tokens?"
        
        await research_agent._gather_research_data(query)
        
        # Should call sentiment scraping with extracted tokens
        mock_firecrawl_service.scrape_social_sentiment.assert_called_once_with(['btc', 'eth'])


class TestFirecrawlResearchAgentFactory:
    """Test the agent factory function"""
    
    def test_get_firecrawl_research_agent(self):
        """Test the factory function"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            from agents.firecrawl_research import get_firecrawl_research_agent
            
            agent = get_firecrawl_research_agent(
                model_id="gemini-2.0-flash-lite",
                user_id="test-user",
                session_id="test-session",
                debug_mode=True
            )
            
            assert isinstance(agent, FirecrawlResearchAgent)
            assert agent.model_id == "gemini-2.0-flash-lite"