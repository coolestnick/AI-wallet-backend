import os
import motor.motor_asyncio
import logging
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "salt_wallet")

# Create client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db.users
sessions_collection = db.sessions

# Logger
logger = logging.getLogger("database")

# Helper functions for database operations
async def create_user(user_data: Dict[str, Any]) -> str:
    """
    Create a new user in the database
    
    Args:
        user_data: User data dictionary
        
    Returns:
        The ID of the created user
    """
    try:
        result = await users_collection.insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def get_user_by_wallet(wallet_address: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by wallet address
    
    Args:
        wallet_address: Ethereum wallet address
        
    Returns:
        User document or None if not found
    """
    try:
        user = await users_collection.find_one({"wallet_address": wallet_address})
        return user
    except Exception as e:
        logger.error(f"Error getting user by wallet: {str(e)}")
        return None

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID
    
    Args:
        user_id: User ID
        
    Returns:
        User document or None if not found
    """
    try:
        user = await users_collection.find_one({"id": user_id})
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        return None

async def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a user document
    
    Args:
        user_id: User ID
        update_data: Fields to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        result = await users_collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return False

async def update_user_nonce(wallet_address: str) -> Optional[str]:
    """
    Updates the nonce for a user with the given wallet address
    
    Args:
        wallet_address: Ethereum wallet address
        
    Returns:
        The new nonce or None if user not found
    """
    import uuid
    new_nonce = str(uuid.uuid4())
    
    try:
        result = await users_collection.update_one(
            {"wallet_address": wallet_address},
            {"$set": {"nonce": new_nonce, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return new_nonce
        return None
    except Exception as e:
        logger.error(f"Error updating user nonce: {str(e)}")
        return None

async def create_session(session_data: Dict[str, Any]) -> str:
    """
    Create a new session
    
    Args:
        session_data: Session data
        
    Returns:
        Session ID
    """
    try:
        result = await sessions_collection.insert_one(session_data)
        
        # Add session ID to user's sessions list
        if "user_id" in session_data:
            await users_collection.update_one(
                {"id": session_data["user_id"]},
                {"$push": {"session_ids": session_data["id"]}}
            )
            
        return session_data["id"]
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise

async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a session by ID
    
    Args:
        session_id: Session ID
        
    Returns:
        Session document or None if not found
    """
    try:
        return await sessions_collection.find_one({"id": session_id})
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return None 