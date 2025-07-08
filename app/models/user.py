from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal
import uuid


class User(BaseModel):
    """User model for wallet-based authentication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    wallet_type: str = "ethereum"  # Either "ethereum" or "solana"
    nonce: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    name: Optional[str] = None
    email: Optional[str] = None
    session_ids: List[str] = []
    sol_balance: Optional[float] = None
    sol_token_accounts: Optional[List[dict]] = None
    last_wallet_sync: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "wallet_type": "ethereum",
                "nonce": "54321abcde",
                "created_at": "2023-04-01T12:00:00",
                "updated_at": "2023-04-01T12:00:00",
                "is_active": True,
                "name": "Crypto User",
                "email": "user@example.com",
                "session_ids": ["session1", "session2"],
                "sol_balance": None,
                "sol_token_accounts": None,
                "last_wallet_sync": None
            }
        } 