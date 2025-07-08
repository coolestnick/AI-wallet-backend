# Example of how to use the agents
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.selector import get_agent


def main():
    # Create a crypto advisor agent
    crypto_agent = get_agent("crypto_advisor")
    print(f"Created agent: {crypto_agent.name}")
    print(f"Agent description: {crypto_agent.description}")
    print()

    # Create a market research agent
    market_agent = get_agent("market_research")
    print(f"Created agent: {market_agent.name}")
    print(f"Agent description: {market_agent.description}")
    print()

    # Create a portfolio management agent
    portfolio_agent = get_agent("portfolio_management")
    print(f"Created agent: {portfolio_agent.name}")
    print(f"Agent description: {portfolio_agent.description}")
    print()

    # Create a crypto advisor agent with a custom model
    custom_agent = get_agent(
        agent_id="crypto_advisor",
        model_id="custom-model",
        user_id="test-user",
        session_id="test-session",
    )
    print(f"Created custom agent: {custom_agent.name}")
    print(f"Agent description: {custom_agent.description}")

    # This would raise an error because the agent doesn't exist
    try:
        unknown_agent = get_agent("unknown_agent")
    except ValueError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
