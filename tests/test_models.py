import pytest
from pydantic import ValidationError

from api.models import (AgentListResponse, AgentMetadata, AgentRequest,
                        AgentResponse, Message)


def test_message_model():
    """Test Message model validation"""
    # Valid data
    valid_data = {"role": "user", "content": "Hello"}
    message = Message(**valid_data)
    assert message.role == "user"
    assert message.content == "Hello"

    # Missing role
    with pytest.raises(ValidationError):
        Message(content="Hello")

    # Missing content
    with pytest.raises(ValidationError):
        Message(role="user")


def test_agent_request_model():
    """Test AgentRequest model validation"""
    # Valid data with minimum required fields
    valid_data = {
        "messages": [{"role": "user", "content": "Hello"}],
        "agent_id": "crypto_advisor",
    }
    request = AgentRequest(**valid_data)
    assert request.messages[0].role == "user"
    assert request.messages[0].content == "Hello"
    assert request.agent_id == "crypto_advisor"
    assert request.model_id is None  # Default value
    assert request.user_id is None  # Default value
    assert request.session_id is None  # Default value
    assert request.stream is False  # Default value

    # Valid data with all fields
    full_data = {
        "messages": [{"role": "user", "content": "Hello"}],
        "agent_id": "crypto_advisor",
        "model_id": "gemini-2.0-flash-lite",
        "user_id": "test-user",
        "session_id": "test-session",
        "stream": True,
    }
    request = AgentRequest(**full_data)
    assert request.model_id == "gemini-2.0-flash-lite"
    assert request.user_id == "test-user"
    assert request.session_id == "test-session"
    assert request.stream is True

    # Missing required fields
    with pytest.raises(ValidationError):
        AgentRequest(messages=[{"role": "user", "content": "Hello"}])

    with pytest.raises(ValidationError):
        AgentRequest(agent_id="crypto_advisor")


def test_agent_response_model():
    """Test AgentResponse model validation"""
    # Valid data with minimum required fields
    valid_data = {
        "message": {"role": "assistant", "content": "Hello, how can I help?"},
        "session_id": "test-session",
    }
    response = AgentResponse(**valid_data)
    assert response.message["role"] == "assistant"
    assert response.message["content"] == "Hello, how can I help?"
    assert response.session_id == "test-session"
    assert response.user_id is None  # Default value

    # Valid data with all fields
    full_data = {
        "message": {"role": "assistant", "content": "Hello, how can I help?"},
        "session_id": "test-session",
        "user_id": "test-user",
    }
    response = AgentResponse(**full_data)
    assert response.user_id == "test-user"

    # Missing required fields
    with pytest.raises(ValidationError):
        AgentResponse(message={"role": "assistant", "content": "Hello"})

    with pytest.raises(ValidationError):
        AgentResponse(session_id="test-session")


def test_agent_metadata_model():
    """Test AgentMetadata model validation"""
    # Valid data
    valid_data = {
        "agent_id": "crypto_advisor",
        "name": "Crypto Advisor",
        "description": "A helpful crypto advisor agent",
    }
    metadata = AgentMetadata(**valid_data)
    assert metadata.agent_id == "crypto_advisor"
    assert metadata.name == "Crypto Advisor"
    assert metadata.description == "A helpful crypto advisor agent"

    # Missing fields
    with pytest.raises(ValidationError):
        AgentMetadata(agent_id="crypto_advisor", name="Crypto Advisor")

    with pytest.raises(ValidationError):
        AgentMetadata(agent_id="crypto_advisor", description="A helpful agent")

    with pytest.raises(ValidationError):
        AgentMetadata(name="Crypto Advisor", description="A helpful agent")


def test_agent_list_response_model():
    """Test AgentListResponse model validation"""
    # Valid data
    valid_data = {
        "agents": [
            {
                "agent_id": "crypto_advisor",
                "name": "Crypto Advisor",
                "description": "A helpful crypto advisor agent",
            },
            {
                "agent_id": "market_research",
                "name": "Market Research",
                "description": "A helpful market research agent",
            },
        ]
    }
    response = AgentListResponse(**valid_data)
    assert len(response.agents) == 2
    assert response.agents[0].agent_id == "crypto_advisor"
    assert response.agents[1].name == "Market Research"

    # Empty list is valid
    empty_data = {"agents": []}
    response = AgentListResponse(**empty_data)
    assert len(response.agents) == 0

    # Missing required field
    with pytest.raises(ValidationError):
        AgentListResponse()
