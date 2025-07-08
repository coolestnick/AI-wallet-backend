import os
import logging
import base58
from typing import List, Dict, Any, Optional, Union
import asyncio

# Updated Solana imports
try:
    # First try the newer package structure
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey as PublicKey
    from solana.transaction import Transaction
    from solana.rpc.types import TxOpts
    from solders.keypair import Keypair
    from solders.signature import Signature
except ImportError:
    # Fallback to older package structure if needed
    from solana.rpc.async_api import AsyncClient
    from solana.publickey import PublicKey
    from solana.transaction import Transaction
    from solana.rpc.types import TxOpts
    from solders.keypair import Keypair
    from solders.signature import Signature

# Define Token Program ID constant directly since spl.token may not be available
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

# We'll handle Token client functionality directly when needed

# Setup logging
logger = logging.getLogger("solana_utils")

# Default RPC URLs
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
SOLANA_DEVNET_URL = os.getenv("SOLANA_DEVNET_URL", "https://api.devnet.solana.com")

# Use environment variable to determine network
SOLANA_NETWORK = os.getenv("SOLANA_NETWORK", "mainnet")

# SPL Token Constants
try:
    WRAPPED_SOL_MINT = PublicKey("So11111111111111111111111111111111111111112")
except:
    # Fallback in case PublicKey format changed
    WRAPPED_SOL_MINT = "So11111111111111111111111111111111111111112"

# Cache for token info
token_info_cache = {}


class SolanaClient:
    """Client for interacting with the Solana blockchain"""
    
    def __init__(self, rpc_url: Optional[str] = None, network: str = SOLANA_NETWORK):
        """
        Initialize Solana client
        
        Args:
            rpc_url: Custom RPC URL (optional)
            network: Network to use ('mainnet' or 'devnet')
        """
        if rpc_url:
            self.rpc_url = rpc_url
        else:
            # Use appropriate URL based on network
            self.rpc_url = SOLANA_DEVNET_URL if network == "devnet" else SOLANA_RPC_URL
            
        self.client = AsyncClient(self.rpc_url)
        self.network = network
        logger.info(f"Initialized Solana client with {network} network: {self.rpc_url}")
    
    async def get_sol_balance(self, wallet_address: str) -> float:
        """
        Get SOL balance for a wallet
        
        Args:
            wallet_address: Solana wallet address (base58 string)
            
        Returns:
            Balance in SOL
        """
        try:
            # Convert address to PublicKey
            pubkey = PublicKey(wallet_address)
            
            # Get balance in lamports
            response = await self.client.get_balance(pubkey)
            
            if response.value is not None:
                # Convert lamports to SOL (1 SOL = 10^9 lamports)
                return response.value / 10**9
            else:
                logger.error(f"Failed to get SOL balance: {response}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting SOL balance: {str(e)}")
            return 0.0
    
    async def get_token_accounts(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get all token accounts for a wallet
        
        Args:
            wallet_address: Solana wallet address (base58 string)
            
        Returns:
            List of token accounts with associated metadata
        """
        try:
            # Convert address to PublicKey
            pubkey = PublicKey(wallet_address)
            
            # Get all token accounts
            response = await self.client.get_token_accounts_by_owner(
                pubkey,
                {"programId": TOKEN_PROGRAM_ID}
            )
            
            if not response.value:
                return []
                
            # Process token accounts
            token_accounts = []
            for account in response.value:
                account_data = account.account.data
                
                # Parse token data
                token_mint = account_data.parsed["info"]["mint"]
                token_amount = account_data.parsed["info"]["tokenAmount"]
                
                # Get token metadata
                token_metadata = await self.get_token_metadata(token_mint)
                
                # Create token account object
                token_account = {
                    "mint": token_mint,
                    "name": token_metadata.get("name", "Unknown Token"),
                    "symbol": token_metadata.get("symbol", "???"),
                    "decimals": token_amount["decimals"],
                    "amount": token_amount["uiAmount"],
                    "raw_amount": token_amount["amount"],
                    "logo": token_metadata.get("logoURI"),
                    "account": account.pubkey.to_base58()
                }
                
                token_accounts.append(token_account)
                
            return token_accounts
                
        except Exception as e:
            logger.error(f"Error getting token accounts: {str(e)}")
            return []
    
    async def get_token_metadata(self, mint_address: str) -> Dict[str, Any]:
        """
        Get metadata for a token
        
        Args:
            mint_address: Token mint address
            
        Returns:
            Token metadata
        """
        # Check cache first
        if mint_address in token_info_cache:
            return token_info_cache[mint_address]
            
        # Default data
        token_data = {
            "name": "Unknown Token",
            "symbol": "???",
            "logoURI": None,
            "decimals": 0
        }
        
        try:
            # For special tokens like Wrapped SOL, use hardcoded values
            if mint_address == str(WRAPPED_SOL_MINT):
                token_data = {
                    "name": "Wrapped SOL",
                    "symbol": "SOL",
                    "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
                    "decimals": 9
                }
            else:
                # Try to get token data from Solana token list API
                # Use the Jupiter/Solana token list API
                async with asyncio.timeout(5):
                    import httpx
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.get(
                            "https://token.jup.ag/all"
                        )
                        
                        if response.status_code == 200:
                            token_list = response.json()
                            for token in token_list:
                                if token.get("address") == mint_address:
                                    token_data = {
                                        "name": token.get("name", "Unknown Token"),
                                        "symbol": token.get("symbol", "???"),
                                        "logoURI": token.get("logoURI"),
                                        "decimals": token.get("decimals", 0)
                                    }
                                    break
                
            # Cache the result
            token_info_cache[mint_address] = token_data
            return token_data
                
        except Exception as e:
            logger.error(f"Error getting token metadata for {mint_address}: {str(e)}")
            return token_data
    
    async def get_wallet_nfts(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get NFTs owned by a wallet
        
        Args:
            wallet_address: Solana wallet address (base58 string)
            
        Returns:
            List of NFTs with metadata
        """
        try:
            # Convert address to PublicKey
            pubkey = PublicKey(wallet_address)
            
            # Get all token accounts
            response = await self.client.get_token_accounts_by_owner(
                pubkey,
                {"programId": TOKEN_PROGRAM_ID}
            )
            
            if not response.value:
                return []
                
            # Filter for NFTs (tokens with amount = 1 and decimals = 0)
            nfts = []
            for account in response.value:
                account_data = account.account.data
                
                # Parse token data
                token_mint = account_data.parsed["info"]["mint"]
                token_amount = account_data.parsed["info"]["tokenAmount"]
                
                # Check if this is an NFT
                if token_amount["decimals"] == 0 and token_amount["amount"] == "1":
                    # Try to get metadata
                    nft_metadata = await self._get_nft_metadata(token_mint)
                    
                    nft = {
                        "mint": token_mint,
                        "name": nft_metadata.get("name", "Unknown NFT"),
                        "symbol": nft_metadata.get("symbol", "NFT"),
                        "image": nft_metadata.get("image"),
                        "attributes": nft_metadata.get("attributes", []),
                        "account": account.pubkey.to_base58()
                    }
                    
                    nfts.append(nft)
            
            return nfts
                
        except Exception as e:
            logger.error(f"Error getting wallet NFTs: {str(e)}")
            return []
    
    async def _get_nft_metadata(self, mint_address: str) -> Dict[str, Any]:
        """
        Get metadata for an NFT
        
        Args:
            mint_address: NFT mint address
            
        Returns:
            NFT metadata
        """
        try:
            # Default metadata
            metadata = {
                "name": "Unknown NFT",
                "symbol": "NFT",
                "image": None,
                "attributes": []
            }
            
            # Get metadata from Metaplex
            # This is a simplified implementation - in production, you'd want to use the Metaplex libraries
            
            # For now, we'll use a public API to fetch metadata
            async with asyncio.timeout(5):
                import httpx
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(
                        f"https://api.helius.xyz/v0/tokens/metadata?api-key=a8f6b5f9-8ecd-479d-8f1d-3d1e40bc163c",
                        json={"mintAccounts": [mint_address]}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            nft_data = data[0]
                            
                            # Extract metadata from response
                            metadata = {
                                "name": nft_data.get("name", "Unknown NFT"),
                                "symbol": nft_data.get("symbol", "NFT"),
                                "image": nft_data.get("image"),
                                "attributes": nft_data.get("attributes", [])
                            }
            
            return metadata
                
        except Exception as e:
            logger.error(f"Error getting NFT metadata for {mint_address}: {str(e)}")
            return {
                "name": "Unknown NFT",
                "symbol": "NFT",
                "image": None,
                "attributes": []
            }
    
    async def get_transaction_history(self, wallet_address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transaction history for a wallet
        
        Args:
            wallet_address: Solana wallet address (base58 string)
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        try:
            # Convert address to PublicKey
            pubkey = PublicKey(wallet_address)
            
            # Get signature list
            response = await self.client.get_signatures_for_address(pubkey, limit=limit)
            
            if not response.value:
                return []
                
            # Process transactions
            transactions = []
            for item in response.value:
                # Get full transaction data
                tx_response = await self.client.get_transaction(item.signature)
                
                if not tx_response.value:
                    continue
                
                tx_data = tx_response.value
                
                # Basic transaction info
                transaction = {
                    "signature": item.signature,
                    "slot": item.slot,
                    "timestamp": tx_data.block_time,
                    "success": not item.err,
                    "fee": tx_data.meta.fee / 10**9 if tx_data.meta else 0,
                }
                
                transactions.append(transaction)
            
            return transactions
                
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return []
    
    async def get_wallet_summary(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get a summary of wallet assets and activity
        
        Args:
            wallet_address: Solana wallet address (base58 string)
            
        Returns:
            Wallet summary including balances and recent activity
        """
        try:
            # Get SOL balance
            sol_balance = await self.get_sol_balance(wallet_address)
            
            # Get token accounts
            token_accounts = await self.get_token_accounts(wallet_address)
            
            # Get recent transactions
            recent_transactions = await self.get_transaction_history(wallet_address, 5)
            
            # Calculate estimated value (in a real app, you'd fetch prices)
            # For now, just SOL value based on a hardcoded price
            sol_price = 100  # Example price in USD
            estimated_value = sol_balance * sol_price
            
            # Count tokens
            token_count = len(token_accounts)
            
            # Create summary
            summary = {
                "wallet_address": wallet_address,
                "sol_balance": sol_balance,
                "token_count": token_count,
                "token_accounts": token_accounts,
                "estimated_value_usd": estimated_value,
                "recent_transactions": recent_transactions,
                "network": self.network
            }
            
            return summary
                
        except Exception as e:
            logger.error(f"Error getting wallet summary: {str(e)}")
            return {
                "wallet_address": wallet_address,
                "sol_balance": 0,
                "token_count": 0,
                "token_accounts": [],
                "estimated_value_usd": 0,
                "recent_transactions": [],
                "network": self.network,
                "error": str(e)
            }

    async def close(self):
        """Close the client connection"""
        await self.client.close()


# Singleton client
_solana_client = None

def get_solana_client() -> SolanaClient:
    """Get or create a Solana client instance"""
    global _solana_client
    if _solana_client is None:
        _solana_client = SolanaClient()
    return _solana_client


async def verify_solana_signature(message: str, signature: str, wallet_address: str) -> bool:
    """
    Verify a Solana wallet signature
    
    Args:
        message: The message that was signed
        signature: Base58 encoded signature
        wallet_address: Solana wallet address that signed the message
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Decode signature from base58
        signature_bytes = base58.b58decode(signature)
        
        # Create PublicKey from wallet address
        public_key = PublicKey(wallet_address)
        
        # Verify signature (message should be UTF-8 encoded)
        return public_key.verify(message.encode('utf-8'), signature_bytes)
    except Exception as e:
        logger.error(f"Error verifying Solana signature: {str(e)}")
        return False 