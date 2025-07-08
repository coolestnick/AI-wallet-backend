import sys
from typing import Dict, Optional

# Import base agent class
from agents.base import Agent

# Agent creator function types
def get_crypto_advisor_agent(model_id=None, **kwargs):
    # Import within function to avoid circular imports
    from agents.crypto_advisor import CryptoAdvisorAgent
    return CryptoAdvisorAgent(model_id=model_id, **kwargs)


def get_market_research_agent(model_id=None, **kwargs):
    # Import within function to avoid circular imports
    from agents.market_research import MarketResearchAgent
    return MarketResearchAgent(model_id=model_id, **kwargs)


def get_portfolio_management_agent(model_id=None, **kwargs):
    # Import within function to avoid circular imports
    from agents.portfolio_management import PortfolioManagementAgent
    return PortfolioManagementAgent(model_id=model_id, **kwargs)


def get_firecrawl_research_agent(model_id=None, **kwargs):
    # Import within function to avoid circular imports
    from agents.firecrawl_research import FirecrawlResearchAgent
    return FirecrawlResearchAgent(model_id=model_id, **kwargs)


# Map of agent_id to agent creator function
AGENT_CREATORS = {
    "crypto_advisor": get_crypto_advisor_agent,
    "market_research": get_market_research_agent,
    "portfolio_management": get_portfolio_management_agent,
    "firecrawl_research": get_firecrawl_research_agent,
}


def get_agent(
    agent_id: str,
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """Get an agent by ID

    Args:
        agent_id: The ID of the agent to get
        model_id: The ID of the model to use (overrides default)
        user_id: The ID of the user
        session_id: The ID of the session
        debug_mode: Whether to enable debug mode

    Returns:
        The agent instance
    """
    creator = AGENT_CREATORS.get(agent_id)
    if creator is None:
        raise ValueError(f"Unknown agent_id: {agent_id}")

    return creator(
        model_id=model_id
        or "gemini-2.0-flash-lite",  # Default to Gemini 2.0 Flash-Lite
        user_id=user_id,
        session_id=session_id,
        debug_mode=debug_mode,
    )
