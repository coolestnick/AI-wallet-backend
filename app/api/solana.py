from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, Optional, List

from app.utils.solana_utils import SolanaClient, get_solana_client
from app.utils.auth_deps import get_current_user
from app.db.database import update_user
from datetime import datetime

# Create router
router = APIRouter(prefix="/solana", tags=["Solana"])

@router.get("/balance/{wallet_address}")
async def get_sol_balance(
    wallet_address: str,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get SOL balance for a wallet address
    
    Args:
        wallet_address: Solana wallet address
        user: Authenticated user (optional)
        
    Returns:
        SOL balance
    """
    # Create Solana client
    client = get_solana_client()
    
    try:
        # Get balance
        balance = await client.get_sol_balance(wallet_address)
        
        # Check if this is the user's wallet and update if needed
        if user and user.get("wallet_address").lower() == wallet_address.lower():
            # Update user's cached SOL balance
            await update_user(user["id"], {
                "sol_balance": balance,
                "last_wallet_sync": datetime.utcnow()
            })
        
        return {"wallet_address": wallet_address, "sol_balance": balance}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching SOL balance: {str(e)}"
        )

@router.get("/tokens/{wallet_address}")
async def get_wallet_tokens(
    wallet_address: str,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get token balances for a Solana wallet
    
    Args:
        wallet_address: Solana wallet address
        user: Authenticated user (optional)
        
    Returns:
        List of token accounts with metadata
    """
    # Create Solana client
    client = get_solana_client()
    
    try:
        # Get token accounts
        token_accounts = await client.get_token_accounts(wallet_address)
        
        # Check if this is the user's wallet and update if needed
        if user and user.get("wallet_address").lower() == wallet_address.lower():
            # Update user's cached token accounts
            await update_user(user["id"], {
                "sol_token_accounts": token_accounts,
                "last_wallet_sync": datetime.utcnow()
            })
        
        return {"wallet_address": wallet_address, "tokens": token_accounts}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching token balances: {str(e)}"
        )

@router.get("/nfts/{wallet_address}")
async def get_wallet_nfts(
    wallet_address: str,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get NFTs for a Solana wallet
    
    Args:
        wallet_address: Solana wallet address
        user: Authenticated user (optional)
        
    Returns:
        List of NFTs with metadata
    """
    # Create Solana client
    client = get_solana_client()
    
    try:
        # Get NFTs
        nfts = await client.get_wallet_nfts(wallet_address)
        
        return {"wallet_address": wallet_address, "nfts": nfts}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching NFTs: {str(e)}"
        )

@router.get("/transactions/{wallet_address}")
async def get_wallet_transactions(
    wallet_address: str,
    limit: int = Query(10, ge=1, le=100),
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get transaction history for a Solana wallet
    
    Args:
        wallet_address: Solana wallet address
        limit: Number of transactions to return (max 100)
        user: Authenticated user (optional)
        
    Returns:
        List of transactions
    """
    # Create Solana client
    client = get_solana_client()
    
    try:
        # Get transactions
        transactions = await client.get_transaction_history(wallet_address, limit)
        
        return {"wallet_address": wallet_address, "transactions": transactions}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transactions: {str(e)}"
        )

@router.get("/summary/{wallet_address}")
async def get_wallet_summary(
    wallet_address: str,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Get a summary of wallet assets and activity
    
    Args:
        wallet_address: Solana wallet address
        user: Authenticated user (optional)
        
    Returns:
        Wallet summary
    """
    # Create Solana client
    client = get_solana_client()
    
    try:
        # Get wallet summary
        summary = await client.get_wallet_summary(wallet_address)
        
        # Check if this is the user's wallet and update if needed
        if user and user.get("wallet_address").lower() == wallet_address.lower():
            # Update user's cached wallet data
            await update_user(user["id"], {
                "sol_balance": summary.get("sol_balance"),
                "sol_token_accounts": summary.get("token_accounts"),
                "last_wallet_sync": datetime.utcnow()
            })
        
        return summary
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching wallet summary: {str(e)}"
        ) 