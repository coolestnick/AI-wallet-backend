from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional

from app.db.database import get_user_by_id, update_user
from app.utils.auth_deps import get_current_user

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_current_user_info(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get information about the current authenticated user
    
    Args:
        user: User document from auth dependency
        
    Returns:
        User information without sensitive fields
    """
    # Remove sensitive fields
    if "nonce" in user:
        del user["nonce"]
    
    return user

@router.put("/me")
async def update_current_user_info(
    user_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update information for the current authenticated user
    
    Args:
        user_data: Fields to update
        user: User document from auth dependency
        
    Returns:
        Updated user information
    """
    # Prevent updating certain fields
    protected_fields = ["id", "wallet_address", "nonce", "created_at", "is_active", "session_ids"]
    for field in protected_fields:
        if field in user_data:
            del user_data[field]
    
    # Update user
    success = await update_user(user["id"], user_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )
    
    # Get updated user data
    updated_user = await get_user_by_id(user["id"])
    
    # Remove sensitive fields
    if "nonce" in updated_user:
        del updated_user["nonce"]
    
    return updated_user 