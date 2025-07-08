"""
Cryptocurrency Price Service

This service integrates with the DexScreener MCP server to provide
cryptocurrency price data for the portfolio agent.
"""

import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union
from app.mcp.ccxt import client as ccxt_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("crypto-price-service")


class CryptoPriceService:
    """Service to fetch cryptocurrency prices from the CCXT MCP server (Hyperliquid)."""

    def __init__(self):
        pass

    def get_token_price(self, symbol: str, quote: str = "USDT") -> Optional[float]:
        """
        Get the price of a token in the specified quote currency using Hyperliquid via MCP.

        Args:
            symbol: The base symbol (e.g., 'ETH', 'BTC')
            quote: The quote currency (default: 'USDT')

        Returns:
            Token price as a float, or None if not found
        """
        result = ccxt_client.get_price(symbol, quote, exchange="hyperliquid")
        if "error" in result:
            logger.error(f"Error getting price for {symbol}/{quote}: {result['error']}")
            return None
        price = result.get("price")
        if price is not None:
            try:
                return float(price)
            except (ValueError, TypeError):
                logger.error(f"Failed to convert price to float: {price}")
        logger.warning(f"Could not determine price for {symbol}/{quote}")
        return None

    def search_pairs(self, query: str) -> Dict[str, Any]:
        """
        Search for trading pairs matching a query.

        Args:
            query: Search query (token name, symbol, or address)

        Returns:
            Dictionary containing search results
        """
        request = {
            "type": "action",
            "action": "search_pairs",
            "parameters": {"query": query},
        }
        return self._send_request(request)

    def get_pair_info(self, pair_address: str) -> Dict[str, Any]:
        """
        Get information about a specific trading pair.

        Args:
            pair_address: The contract address of the trading pair

        Returns:
            Dictionary containing pair information
        """
        request = {
            "type": "action",
            "action": "get_pair",
            "parameters": {"pairAddress": pair_address},
        }
        return self._send_request(request)

    def get_token_pairs(self, token_address: str) -> Dict[str, Any]:
        """
        Get all trading pairs for a specific token.

        Args:
            token_address: The contract address of the token

        Returns:
            Dictionary containing token's trading pairs
        """
        request = {
            "type": "action",
            "action": "get_token",
            "parameters": {"tokenAddress": token_address},
        }
        return self._send_request(request)
