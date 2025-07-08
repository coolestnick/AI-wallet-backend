from unittest.mock import MagicMock, patch

import pytest

# Import directly from our simplified selector module
from agents.selector import AGENT_CREATORS, Agent, get_agent


def test_agent_creators():
    """Test that all agent creators are registered"""
    assert "crypto_advisor" in AGENT_CREATORS
    assert "market_research" in AGENT_CREATORS
    assert "portfolio_management" in AGENT_CREATORS
    assert len(AGENT_CREATORS) == 3


def test_get_agent_unknown_id():
    """Test that get_agent raises ValueError for unknown agent_id"""
    with pytest.raises(ValueError, match="Unknown agent_id: unknown_agent"):
        get_agent("unknown_agent")


def test_get_agent_returns_agent():
    """Test that get_agent returns an agent instance"""
    agent = get_agent("crypto_advisor")
    assert isinstance(agent, Agent)
    assert agent.agent_id == "crypto_advisor"
    assert agent.name == "Crypto Advisor Agent"


def test_get_agent_with_custom_model():
    """Test getting an agent with a custom model"""
    agent = get_agent("market_research", model_id="custom-model")
    assert isinstance(agent, Agent)
    assert agent.agent_id == "market_research"


def test_portfolio_agent():
    """Test getting the portfolio management agent"""
    agent = get_agent("portfolio_management")
    assert isinstance(agent, Agent)
    assert agent.agent_id == "portfolio_management"
    assert "Portfolio" in agent.name
