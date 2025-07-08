from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
from typing import Dict, Any, Optional

from agents.selector import AGENT_CREATORS, get_agent
from api.models import (AgentListResponse, AgentMetadata, AgentRequest,
                        AgentResponse)
from app.utils.auth_deps import get_optional_user

# Create API router
router = APIRouter()
logger = logging.getLogger("api_routes")


@router.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """List all available agents"""
    agents = []
    
    # Create agent metadata for each agent creator
    for agent_id, creator in AGENT_CREATORS.items():
        agent = creator(debug_mode=False)
        
        # Add the agent with the original underscore ID
        agents.append(
            AgentMetadata(
                agent_id=agent_id,
                name=agent.name,
                description=agent.description,
            )
        )
        
        # Also add the agent with a hyphenated ID for compatibility
        hyphenated_id = agent_id.replace('_', '-')
        agents.append(
            AgentMetadata(
                agent_id=hyphenated_id,
                name=agent.name,
                description=agent.description,
            )
        )

    return AgentListResponse(agents=agents)


@router.post("/agents/{agent_id}/chat", response_model=AgentResponse)
async def chat_with_agent(
    agent_id: str, 
    request: AgentRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Chat with an agent"""
    try:
        # Normalize agent_id by replacing hyphens with underscores
        normalized_agent_id = agent_id.replace('-', '_')
        
        if normalized_agent_id not in AGENT_CREATORS:
            raise ValueError(f"Unknown agent_id: {agent_id}")
        
        # Set user ID from authenticated user
        user_id = user.get("id") if user else request.user_id
        
        if not user_id:
            logger.info(f"Anonymous user accessing agent {agent_id}")
            user_id = "anonymous"
            
        agent = get_agent(
            agent_id=normalized_agent_id,
            model_id=request.model_id,
            user_id=user_id,
            session_id=request.session_id,
        )
        
        response = await agent.generate_response(request.messages)
        
        return AgentResponse(
            message=response,
            session_id=request.session_id or "test-session",
            user_id=user_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/chat/stream")
async def stream_chat_with_agent(
    agent_id: str, 
    request: AgentRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Stream a chat with an agent"""
    # Normalize agent_id by replacing hyphens with underscores
    normalized_agent_id = agent_id.replace('-', '_')
    
    if normalized_agent_id not in AGENT_CREATORS:
        raise HTTPException(status_code=400, detail=f"Unknown agent_id: {agent_id}")

    # Set user ID from authenticated user
    user_id = user.get("id") if user else request.user_id
    
    if not user_id:
        logger.info(f"Anonymous user accessing streaming agent {agent_id}")
        user_id = "anonymous"

    async def event_generator():
        try:
            # Get the agent instance
            agent = get_agent(
                agent_id=normalized_agent_id,
                model_id=request.model_id,
                user_id=user_id,
                session_id=request.session_id,
            )
            
            # Use the agent's streaming method to generate responses
            async for chunk in agent.generate_streaming_response(request.messages):
                # Add session_id to the final chunk
                if chunk.get("done", False):
                    chunk["session_id"] = request.session_id or "test-session"
                    if user_id:
                        chunk["user_id"] = user_id
                
                # Send the chunk as SSE
                yield f"data: {json.dumps(chunk)}\n\n"
        
        except Exception as e:
            # Handle errors in the stream
            error_msg = str(e)
            logger.error(f"Stream error for agent {agent_id}: {error_msg}")
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
