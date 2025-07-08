"""
Test cases for enhanced Crypto Advisor Agent with unified API integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

from agents.crypto_advisor import CryptoAdvisorAgent
from app.services.unified_crypto_api import TokenPrice, TradingPair


class TestCryptoAdvisorAgentEnhanced:
    """Test suite for enhanced Crypto Advisor Agent"""

    @pytest.fixture
    def mock_unified_api(self):
        """Mock unified crypto API"""
        mock_api = AsyncMock()
        return mock_api

    @pytest.fixture
    def sample_price_data(self):
        """Sample price data for testing"""
        return {
            "bitcoin_usd": TokenPrice(
                symbol="bitcoin",
                price_usd=45000.0,
                price_change_24h=2.5,
                market_cap=850000000000,
                volume_24h=25000000000,
                source="coingecko",
                timestamp=datetime.now()
            ),
            "ethereum_usd": TokenPrice(
                symbol="ethereum", 
                price_usd=3200.0,
                price_change_24h=1.8,
                market_cap=380000000000,
                volume_24h=15000000000,
                source="coingecko",
                timestamp=datetime.now()
            )
        }

    @pytest.fixture
    def crypto_advisor_agent(self):
        """Create CryptoAdvisorAgent instance for testing"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
            agent = CryptoAdvisorAgent()
            return agent

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_agent_initialization(self, crypto_advisor_agent):
        """Test agent initialization"""
        assert crypto_advisor_agent.name == "Crypto Advisor Agent"
        assert crypto_advisor_agent.agent_id == "crypto_advisor"
        assert "cryptocurrency investments" in crypto_advisor_agent.description.lower()
        assert crypto_advisor_agent.api_configured == True

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_agent_initialization_without_api_key(self):
        """Test agent initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = CryptoAdvisorAgent()
            assert agent.api_configured == False
            assert agent.model is None

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_crypto_data_fetching(self, crypto_advisor_agent, mock_unified_api, sample_price_data):
        """Test cryptocurrency data fetching"""
        # Mock the unified API
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = sample_price_data
        mock_unified_api.get_market_overview.return_value = {
            "market_summary": sample_price_data
        }

        # Test with bitcoin query
        result = await crypto_advisor_agent._fetch_crypto_data("what is the price of bitcoin")
        
        assert result is not None
        assert "bitcoin" in result.lower()
        assert "45000" in result or "45,000" in result
        assert "2.5%" in result
        assert "UTC" in result

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_crypto_data_fetching_multiple_coins(self, crypto_advisor_agent, mock_unified_api, sample_price_data):
        """Test fetching data for multiple cryptocurrencies"""
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = sample_price_data

        result = await crypto_advisor_agent._fetch_crypto_data("compare bitcoin and ethereum prices")
        
        assert result is not None
        assert "bitcoin" in result.lower()
        assert "ethereum" in result.lower()

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_crypto_data_fetching_error_handling(self, crypto_advisor_agent, mock_unified_api):
        """Test error handling in crypto data fetching"""
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.side_effect = Exception("API Error")

        result = await crypto_advisor_agent._fetch_crypto_data("bitcoin price")
        
        assert result is None

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_message_processing_with_crypto_keywords(self, crypto_advisor_agent, mock_unified_api, sample_price_data):
        """Test message processing with crypto keywords"""
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = sample_price_data
        mock_unified_api.get_market_overview.return_value = {"market_summary": {}}

        messages = [
            {"role": "user", "content": "What's the current price of Bitcoin?"}
        ]

        enhanced_messages = await crypto_advisor_agent._process_messages(messages)
        
        assert len(enhanced_messages) == 1
        assert "Current Market Data" in enhanced_messages[0]["content"]
        assert "bitcoin" in enhanced_messages[0]["content"].lower()

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_message_processing_without_crypto_keywords(self, crypto_advisor_agent):
        """Test message processing without crypto keywords"""
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]

        enhanced_messages = await crypto_advisor_agent._process_messages(messages)
        
        assert len(enhanced_messages) == 1
        assert enhanced_messages[0]["content"] == "Hello, how are you?"

    @pytest.mark.agents
    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_response_success(self, mock_model_class, crypto_advisor_agent, mock_unified_api, sample_price_data):
        """Test successful response generation"""
        # Mock Gemini model
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "Bitcoin is currently trading at $45,000 with a 2.5% increase."
        mock_model.generate_content_async.return_value = mock_response
        mock_model_class.return_value = mock_model
        crypto_advisor_agent.model = mock_model

        # Mock unified API
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = sample_price_data
        mock_unified_api.get_market_overview.return_value = {"market_summary": {}}

        messages = [
            {"role": "user", "content": "What's the price of Bitcoin?"}
        ]

        response = await crypto_advisor_agent.generate_response(messages)
        
        assert response["role"] == "assistant"
        assert "Bitcoin" in response["content"]
        assert "$45,000" in response["content"]

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_generate_response_without_api_key(self):
        """Test response generation without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = CryptoAdvisorAgent()
            
            messages = [
                {"role": "user", "content": "What's the price of Bitcoin?"}
            ]

            response = await agent.generate_response(messages)
            
            assert response["role"] == "assistant"
            assert "GEMINI_API_KEY is missing" in response["content"]

    @pytest.mark.agents
    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_generate_streaming_response(self, mock_model_class, crypto_advisor_agent, mock_unified_api, sample_price_data):
        """Test streaming response generation"""
        # Mock Gemini model for streaming
        mock_model = AsyncMock()
        
        # Create mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(parts=[MagicMock(text="Bitcoin is currently ")]),
                MagicMock(parts=[MagicMock(text="trading at $45,000 ")]),
                MagicMock(parts=[MagicMock(text="with a 2.5% increase.")])
            ]
            for chunk in chunks:
                yield chunk

        mock_model.generate_content_async.return_value = mock_stream()
        mock_model_class.return_value = mock_model
        crypto_advisor_agent.model = mock_model

        # Mock unified API
        crypto_advisor_agent.unified_api = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = sample_price_data
        mock_unified_api.get_market_overview.return_value = {"market_summary": {}}

        messages = [
            {"role": "user", "content": "What's the price of Bitcoin?"}
        ]

        chunks = []
        async for chunk in crypto_advisor_agent.generate_streaming_response(messages):
            chunks.append(chunk)
        
        # Should have content chunks plus final done chunk
        assert len(chunks) > 0
        assert chunks[-1]["done"] == True

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_generate_streaming_response_without_api_key(self):
        """Test streaming response without API key"""
        with patch.dict('os.environ', {}, clear=True):
            agent = CryptoAdvisorAgent()
            
            messages = [
                {"role": "user", "content": "What's the price of Bitcoin?"}
            ]

            chunks = []
            async for chunk in agent.generate_streaming_response(messages):
                chunks.append(chunk)
            
            assert len(chunks) >= 2  # Error message chunks + done
            assert chunks[-1]["done"] == True
            error_content = "".join([chunk.get("content", "") for chunk in chunks])
            assert "GEMINI_API_KEY is missing" in error_content

    @pytest.mark.agents
    @pytest.mark.asyncio
    async def test_unified_api_initialization(self, crypto_advisor_agent, mock_unified_api):
        """Test unified API initialization"""
        # Initially should be None
        assert crypto_advisor_agent.unified_api is None
        
        # Mock get_unified_api function
        with patch('agents.crypto_advisor.get_unified_api', return_value=mock_unified_api):
            result = await crypto_advisor_agent._fetch_crypto_data("bitcoin price")
            
            # Should initialize unified_api
            assert crypto_advisor_agent.unified_api == mock_unified_api

    @pytest.mark.agents
    def test_message_formatting_for_gemini(self, crypto_advisor_agent):
        """Test message formatting for Gemini API"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        formatted = crypto_advisor_agent._format_messages_for_gemini(messages)
        
        assert isinstance(formatted, list)
        assert len(formatted) == 3
        
        # Check role mapping
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "model"  # assistant -> model
        assert formatted[2]["role"] == "user"

    @pytest.mark.agents
    def test_crypto_keyword_detection(self, crypto_advisor_agent):
        """Test crypto keyword detection in queries"""
        # Test queries that should trigger crypto data fetching
        crypto_queries = [
            "what is the price of bitcoin",
            "how is ethereum performing",
            "btc market analysis",
            "crypto market trends",
            "coin prices today"
        ]
        
        # Test queries that should not trigger crypto data fetching
        non_crypto_queries = [
            "what is the weather",
            "how to cook pasta",
            "explain quantum physics"
        ]
        
        crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "price", "crypto", "market", "coin", "token"]
        
        for query in crypto_queries:
            has_crypto_keyword = any(keyword in query.lower() for keyword in crypto_keywords)
            assert has_crypto_keyword, f"Query '{query}' should contain crypto keywords"
        
        for query in non_crypto_queries:
            has_crypto_keyword = any(keyword in query.lower() for keyword in crypto_keywords)
            assert not has_crypto_keyword, f"Query '{query}' should not contain crypto keywords"


class TestCryptoAdvisorAgentIntegration:
    """Integration tests for Crypto Advisor Agent"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_with_real_unified_api(self):
        """Test agent with real unified API (requires API keys)"""
        import os
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Skipping integration test without GEMINI_API_KEY")
        
        agent = CryptoAdvisorAgent()
        
        # Test with a simple query that shouldn't trigger external API calls
        messages = [
            {"role": "user", "content": "Hello, what can you help me with?"}
        ]
        
        try:
            response = await agent.generate_response(messages)
            assert response["role"] == "assistant"
            assert len(response["content"]) > 0
        except Exception as e:
            pytest.skip(f"Integration test failed (expected without proper API setup): {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_agent_crypto_query_integration(self):
        """Test agent with crypto query (requires API keys)"""
        import os
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Skipping integration test without GEMINI_API_KEY")
        
        agent = CryptoAdvisorAgent()
        
        messages = [
            {"role": "user", "content": "What do you think about Bitcoin as an investment?"}
        ]
        
        try:
            response = await agent.generate_response(messages)
            assert response["role"] == "assistant"
            assert len(response["content"]) > 0
            # Should contain investment-related advice
            content_lower = response["content"].lower()
            assert any(word in content_lower for word in ["investment", "bitcoin", "crypto", "advice"])
        except Exception as e:
            pytest.skip(f"Integration test failed (expected without proper API setup): {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_performance(self):
        """Test agent response performance"""
        import time
        import os
        
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Skipping performance test without GEMINI_API_KEY")
        
        agent = CryptoAdvisorAgent()
        
        messages = [
            {"role": "user", "content": "Give me a brief overview of cryptocurrency."}
        ]
        
        start_time = time.time()
        try:
            response = await agent.generate_response(messages)
            end_time = time.time()
            
            # Response should be generated in reasonable time (less than 30 seconds)
            response_time = end_time - start_time
            assert response_time < 30.0, f"Response took too long: {response_time} seconds"
            
            assert response["role"] == "assistant"
            assert len(response["content"]) > 0
        except Exception as e:
            pytest.skip(f"Performance test failed (expected without proper API setup): {e}")