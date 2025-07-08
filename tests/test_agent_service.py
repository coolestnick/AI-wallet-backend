import pytest
import os
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_env_variables():
    """Mock environment variables for all tests in this file"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"}):
        yield

@pytest.fixture
def mock_gemini_response():
    mock_response = MagicMock()
    mock_response.text = "This is a response from the Gemini AI model about cryptocurrency investments."
    return mock_response

@pytest.fixture
def mock_gemini_client():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_model = MockModel.return_value
        mock_model.generate_content.return_value = MagicMock(
            text="This is a response from the Gemini AI model about cryptocurrency investments."
        )
        yield mock_model

def test_crypto_advisor_agent(mock_gemini_client):
    """Test that the Crypto Advisor agent can generate responses"""
    from agents.crypto_advisor import CryptoAdvisorAgent
    
    # Create agent instance with the mock client
    agent = CryptoAdvisorAgent()
    
    # Replace the agent's model with our mock
    agent.model = mock_gemini_client
    
    # Test generating a response
    response = agent.generate_response("Should I invest in Bitcoin?", "user123")
    
    # Check response
    assert response is not None
    assert "message_id" in response
    assert "content" in response
    assert "created_at" in response
    
    # Verify mock was called correctly
    mock_gemini_client.generate_content.assert_called_once()
    args, kwargs = mock_gemini_client.generate_content.call_args
    assert "Bitcoin" in str(args[0])

def test_market_research_agent(mock_gemini_client):
    """Test that the Market Research agent can generate responses"""
    from agents.market_research import MarketResearchAgent
    
    # Create agent instance with the mock client
    agent = MarketResearchAgent()
    
    # Replace the agent's model with our mock
    agent.model = mock_gemini_client
    
    # Test generating a response
    response = agent.generate_response("What are the current market trends for Ethereum?", "user123")
    
    # Check response
    assert response is not None
    assert "message_id" in response
    assert "content" in response
    assert "created_at" in response
    
    # Verify mock was called correctly
    mock_gemini_client.generate_content.assert_called_once()
    args, kwargs = mock_gemini_client.generate_content.call_args
    assert "Ethereum" in str(args[0])

def test_portfolio_management_agent(mock_gemini_client):
    """Test that the Portfolio Management agent can generate responses"""
    from agents.portfolio_management import PortfolioManagementAgent
    
    # Create agent instance with the mock client
    agent = PortfolioManagementAgent()
    
    # Replace the agent's model with our mock
    agent.model = mock_gemini_client
    
    # Test generating a response
    response = agent.generate_response("How should I diversify my crypto portfolio?", "user123")
    
    # Check response
    assert response is not None
    assert "message_id" in response
    assert "content" in response
    assert "created_at" in response
    
    # Verify mock was called correctly
    mock_gemini_client.generate_content.assert_called_once()
    args, kwargs = mock_gemini_client.generate_content.call_args
    assert "diversify" in str(args[0])
