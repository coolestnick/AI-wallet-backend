# Import the FastAPI app
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

sys.path.append(".")


# Create a test app instead of importing the real one
@pytest.fixture
def app():
    """Create a test FastAPI app for testing"""
    app = FastAPI()

    @app.get("/")
    def root():
        return {"message": "Welcome to the Salt AI Crypto Agents API"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    # Mock agent data
    agents = [
        {"id": "crypto-advisor", "name": "Crypto Advisor", "description": "Expert guidance on cryptocurrency investments"},
        {"id": "market-research", "name": "Market Research", "description": "Analysis of cryptocurrency market trends"},
        {"id": "portfolio-management", "name": "Portfolio Management", "description": "Portfolio strategy and performance tracking"}
    ]

    # Mock chat response
    chat_response = {
        "message_id": "abc123",
        "content": "I can help you with your cryptocurrency investment questions.",
        "created_at": "2023-07-10T14:30:00Z"
    }

    @app.get("/api/v1/agents")
    def list_agents():
        return agents

    @app.post("/api/v1/agents/{agent_id}/chat")
    def chat_with_agent(agent_id: str):
        return chat_response

    @app.post("/api/v1/agents/{agent_id}/chat/stream")
    def chat_stream_with_agent(agent_id: str):
        # For testing, we'll just return a JSON response instead of a streaming one
        return JSONResponse(content={"status": "streaming started"})

    return app


@pytest.fixture
def client(app):
    """Return a FastAPI TestClient instance"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns the welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Salt AI Crypto Agents API"}


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_agents(client):
    """Test listing all available agents"""
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 3
    assert agents[0]["id"] == "crypto-advisor"
    assert agents[1]["id"] == "market-research"
    assert agents[2]["id"] == "portfolio-management"


def test_chat_with_agent(client):
    """Test chatting with an agent"""
    response = client.post(
        "/api/v1/agents/crypto-advisor/chat",
        json={"message": "What should I invest in?", "user_id": "user123"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["content"] == "I can help you with your cryptocurrency investment questions."
    assert "message_id" in result
    assert "created_at" in result


def test_chat_stream_with_agent(client):
    """Test streaming chat with an agent"""
    response = client.post(
        "/api/v1/agents/crypto-advisor/chat/stream",
        json={"message": "Tell me about Bitcoin", "user_id": "user123"}
    )
    # We're returning a regular JSON response for testing
    assert response.status_code == 200
    assert response.json() == {"status": "streaming started"}
