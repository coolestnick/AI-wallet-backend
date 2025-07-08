# Example of how to use the API
import json

import requests

# API base URL - in a real scenario, this would be your server address
BASE_URL = "http://localhost:8000/api/v1"


def list_agents():
    """List all available agents"""
    print("\n=== Listing all agents ===")
    response = requests.get(f"{BASE_URL}/agents")
    if response.status_code == 200:
        agents = response.json()["agents"]
        for agent in agents:
            print(f"- {agent['name']} ({agent['agent_id']})")
            print(f"  {agent['description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def chat_with_agent(agent_id, message):
    """Chat with a specific agent"""
    print(f"\n=== Chatting with {agent_id} ===")
    print(f"User: {message}")

    payload = {"messages": [{"role": "user", "content": message}], "agent_id": agent_id}

    response = requests.post(f"{BASE_URL}/agents/{agent_id}/chat", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"Agent: {data['message']['content']}")
        print(f"Session ID: {data['session_id']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def chat_with_invalid_agent():
    """Try to chat with an invalid agent"""
    print("\n=== Chatting with invalid agent ===")

    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "agent_id": "nonexistent_agent",
    }

    response = requests.post(f"{BASE_URL}/agents/nonexistent_agent/chat", json=payload)

    if response.status_code != 200:
        print(f"Expected error: {response.status_code} - {response.text}")
    else:
        print("Error: Expected a 400 error but got a 200 success")


def main():
    """Run the example"""
    print("API Usage Example\n")
    print("Note: Make sure the API server is running on http://localhost:8000")

    # List all agents
    list_agents()

    # Chat with each agent
    chat_with_agent("crypto_advisor", "What's Bitcoin?")
    chat_with_agent("market_research", "How is the crypto market doing today?")
    chat_with_agent(
        "portfolio_management", "How should I diversify my crypto portfolio?"
    )

    # Try with an invalid agent
    chat_with_invalid_agent()


if __name__ == "__main__":
    main()
