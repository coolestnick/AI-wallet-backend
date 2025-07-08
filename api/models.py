from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    messages: List[Message]
    agent_id: Optional[str] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    stream: bool = False


class AgentResponse(BaseModel):
    message: Dict[str, Any]
    session_id: str
    user_id: Optional[str] = None


class AgentMetadata(BaseModel):
    agent_id: str
    name: str
    description: str


class AgentListResponse(BaseModel):
    agents: List[AgentMetadata]
