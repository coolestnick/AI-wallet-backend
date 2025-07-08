import os
import logging
import jwt
from datetime import datetime, timedelta
from eth_account.messages import encode_defunct
from eth_account import Account
from typing import Dict, Any, Optional, Literal

# Try to import Solana utilities, but don't fail if not available
try:
    from app.utils.solana_utils import verify_solana_signature
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    # Define a fallback function if Solana utilities are not available
    def verify_solana_signature(message: str, signature: str, address: str) -> bool:
        logger.warning("Solana verification requested but dependencies are not installed")
        return False

# Setup logging
logger = logging.getLogger("wallet_auth")

# Get JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-replace-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24  # Token validity in hours

def verify_signature(message: str, signature: str, address: str, wallet_type: str = "ethereum") -> bool:
    """
    Verifies a wallet signature against the original message and address
    
    Args:
        message: The original message that was signed
        signature: The signature to verify
        address: The wallet address that supposedly signed the message
        wallet_type: Type of wallet ("ethereum" or "solana")
        
    Returns:
        True if signature is valid, False otherwise
    """
    # Check wallet type
    if wallet_type.lower() == "solana":
        if not SOLANA_AVAILABLE:
            logger.warning("Solana functionality requested but dependencies are not installed")
            return False
        return verify_solana_signature(message, signature, address)
    else:
        # Default to Ethereum verification
        return verify_ethereum_signature(message, signature, address)

def verify_ethereum_signature(message: str, signature: str, address: str) -> bool:
    """
    Verifies an Ethereum signature against the original message and address
    
    Args:
        message: The original message that was signed
        signature: The signature to verify (hex string)
        address: The Ethereum address that supposedly signed the message
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Prepare message for verification
        message_hash = encode_defunct(text=message)
        
        # Recover the address from the signature
        recovered_address = Account.recover_message(message_hash, signature=signature)
        
        # Compare addresses (case-insensitive)
        return recovered_address.lower() == address.lower()
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        return False

def create_token(user_id: str, wallet_address: str, wallet_type: str = "ethereum") -> Dict[str, Any]:
    """
    Creates a JWT token for user authentication
    
    Args:
        user_id: User ID
        wallet_address: User's wallet address
        wallet_type: Type of wallet ("ethereum" or "solana")
        
    Returns:
        Dictionary with token details
    """
    # Set expiration time
    expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # Create token payload
    payload = {
        "sub": user_id,
        "wallet": wallet_address,
        "wallet_type": wallet_type,
        "exp": expires_at.timestamp(),
        "iat": datetime.utcnow().timestamp()
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user_id": user_id,
        "wallet_address": wallet_address,
        "wallet_type": wallet_type
    }

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

def create_auth_message(wallet_address: str, nonce: str, wallet_type: str = "ethereum") -> str:
    """
    Creates an authentication message for the user to sign
    
    Args:
        wallet_address: User's wallet address
        nonce: Random nonce to prevent replay attacks
        wallet_type: Type of wallet ("ethereum" or "solana")
        
    Returns:
        Message to be signed
    """
    # Format the message
    app_name = os.getenv("APP_NAME", "Salt Wallet")
    
    message = f"""
{app_name} Authentication

Please sign this message to verify you own this wallet:
{wallet_address}

Nonce: {nonce}

This signature will not trigger a blockchain transaction or cost any gas fees.
"""

    # For Solana, we might want to format differently
    if wallet_type.lower() == "solana":
        message = f"""
{app_name} Solana Authentication

Please sign this message to verify you own this Solana wallet:
{wallet_address}

Nonce: {nonce}

This signature will not trigger a blockchain transaction or cost any SOL fees.
"""

    return message

def is_solana_address(address: str) -> bool:
    """
    Check if an address is a valid Solana address format
    
    Args:
        address: Wallet address to check
        
    Returns:
        True if it's a Solana address format, False otherwise
    """
    # Simple check - Solana addresses are base58 encoded and typically 32-44 characters
    # They don't start with 0x like Ethereum addresses
    return not address.startswith("0x") and len(address) >= 32 and len(address) <= 44

def is_ethereum_address(address: str) -> bool:
    """
    Check if an address is a valid Ethereum address format
    
    Args:
        address: Wallet address to check
        
    Returns:
        True if it's an Ethereum address format, False otherwise
    """
    # Simple check - Ethereum addresses start with 0x and are 42 characters (including 0x)
    return address.startswith("0x") and len(address) == 42

def detect_wallet_type(address: str) -> str:
    """
    Detect the wallet type based on address format
    
    Args:
        address: Wallet address
        
    Returns:
        Wallet type ("ethereum" or "solana")
    """
    if is_solana_address(address):
        return "solana"
    elif is_ethereum_address(address):
        return "ethereum"
    else:
        # Default to ethereum if we can't determine
        return "ethereum" 