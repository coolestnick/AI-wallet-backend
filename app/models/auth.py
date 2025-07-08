from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timedelta


class WalletChallenge(BaseModel):
    """Model for wallet authentication challenge"""
    wallet_address: str
    nonce: str
    

class SignatureVerification(BaseModel):
    """Model for verifying wallet signatures"""
    wallet_address: str
    signature: str


class AuthToken(BaseModel):
    """Model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: str
    wallet_address: str


class Session(BaseModel):
    """Session model for tracking user sessions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    wallet_address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    is_active: bool = True
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "abc12345-e89b-12d3-a456-426614174000",
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "created_at": "2023-04-01T12:00:00",
                "expires_at": "2023-04-08T12:00:00",
                "is_active": True,
                "user_agent": "Mozilla/5.0",
                "ip_address": "127.0.0.1"
            }
        } 