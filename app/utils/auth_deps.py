from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, Dict, Any
import logging

from app.db.database import get_user_by_id
from app.utils.wallet_auth import verify_token

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

logger = logging.getLogger("auth_deps")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User document
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check if token exists
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user data from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_optional_user(token: str = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """
    Dependency to get the current user if authenticated, but allow anonymous access
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User document or None if not authenticated
    """
    # If no token is provided, allow anonymous access
    if not token:
        logger.info("Anonymous access allowed")
        return None
    
    try:
        # Verify the token
        payload = verify_token(token)
        if not payload:
            logger.warning("Invalid token provided, allowing anonymous access")
            return None
        
        # Get user data from database
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Invalid token format, allowing anonymous access")
            return None
        
        # Get user from database
        user = await get_user_by_id(user_id)
        if not user:
            logger.warning("User not found, allowing anonymous access")
            return None
        
        # Check if user is active
        if not user.get("is_active", True):
            logger.warning("User account is disabled, allowing anonymous access")
            return None
        
        return user
    except Exception as e:
        logger.error(f"Error in authentication: {str(e)}, allowing anonymous access")
        return None

def get_client_info(request: Request) -> Dict[str, str]:
    """
    Gets client information from the request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with client info
    """
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the client IP from the X-Forwarded-For header
        ip = forwarded_for.split(",")[0].strip()
    else:
        # Fallback to request client
        ip = request.client.host if request.client else "unknown"
    
    # Get User-Agent
    user_agent = request.headers.get("User-Agent", "unknown")
    
    return {
        "ip_address": ip,
        "user_agent": user_agent,
    } 