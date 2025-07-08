from fastapi import APIRouter, HTTPException, Depends, status, Request
from datetime import datetime
import logging
import uuid

from app.models.user import User
from app.models.auth import WalletChallenge, SignatureVerification, AuthToken, Session
from app.db.database import (
    get_user_by_wallet, 
    create_user, 
    update_user_nonce, 
    create_session
)
from app.utils.wallet_auth import (
    create_auth_message, 
    verify_signature, 
    create_token,
    detect_wallet_type,
    is_ethereum_address,
    is_solana_address
)
from app.utils.auth_deps import get_client_info

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Logger
logger = logging.getLogger("auth_api")

@router.post("/challenge", response_model=WalletChallenge)
async def get_authentication_challenge(wallet_address: str):
    """
    Get an authentication challenge for a wallet address.
    
    This endpoint generates a nonce and creates a message for the user to sign
    with their wallet to prove ownership.
    
    Args:
        wallet_address: The wallet address to authenticate
        
    Returns:
        WalletChallenge object with the wallet address and nonce
    """
    # Detect wallet type
    wallet_type = detect_wallet_type(wallet_address)
    
    # Validate wallet address format
    if wallet_type == "ethereum" and not is_ethereum_address(wallet_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum wallet address format"
        )
    elif wallet_type == "solana" and not is_solana_address(wallet_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Solana wallet address format"
        )
        
    try:
        # Check if user already exists
        user = await get_user_by_wallet(wallet_address)
        
        if user:
            # User exists, update their nonce
            new_nonce = await update_user_nonce(wallet_address)
            if not new_nonce:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update authentication nonce"
                )
            nonce = new_nonce
            # Use the stored wallet type
            wallet_type = user.get("wallet_type", wallet_type)
        else:
            # User doesn't exist, create a new nonce
            nonce = str(uuid.uuid4())
            
            # Create new user
            new_user = User(
                wallet_address=wallet_address,
                wallet_type=wallet_type,
                nonce=nonce
            )
            
            # Save to database
            await create_user(new_user.dict())
        
        # Return challenge
        return WalletChallenge(
            wallet_address=wallet_address,
            nonce=nonce
        )
        
    except Exception as e:
        logger.error(f"Error generating challenge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the authentication challenge"
        )

@router.post("/verify", response_model=AuthToken)
async def verify_wallet_signature(
    verification: SignatureVerification,
    request: Request
):
    """
    Verify a wallet signature and issue an authentication token.
    
    Args:
        verification: SignatureVerification object with wallet address and signature
        request: FastAPI request object
        
    Returns:
        AuthToken object with access token
    """
    try:
        # Get user by wallet address
        user = await get_user_by_wallet(verification.wallet_address)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please request a challenge first."
            )
        
        # Get the nonce for this user
        nonce = user.get("nonce")
        if not nonce:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authentication nonce not found. Please request a new challenge."
            )
        
        # Get the wallet type
        wallet_type = user.get("wallet_type", "ethereum")
        
        # Create the message that should have been signed
        message = create_auth_message(verification.wallet_address, nonce, wallet_type)
        
        # Verify the signature
        is_valid = verify_signature(
            message=message,
            signature=verification.signature,
            address=verification.wallet_address,
            wallet_type=wallet_type
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature. Authentication failed."
            )
        
        # Get client info
        client_info = get_client_info(request)
        
        # Create a new session
        session = Session(
            user_id=user["id"],
            wallet_address=verification.wallet_address,
            user_agent=client_info["user_agent"],
            ip_address=client_info["ip_address"]
        )
        
        # Save session to database
        await create_session(session.dict())
        
        # Create JWT token
        token_data = create_token(user["id"], verification.wallet_address, wallet_type)
        
        # Update user nonce to prevent replay attacks
        await update_user_nonce(verification.wallet_address)
        
        return AuthToken(**token_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        ) 