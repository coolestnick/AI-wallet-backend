"""
DexScreener MCP Server

This module implements a Model Context Protocol (MCP) server for DexScreener,
allowing AI agents to fetch cryptocurrency prices from the DexScreener API.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("dexscreener-mcp")

# DexScreener API base URL
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest"


def read_request() -> Dict[str, Any]:
    """Read a request from stdin."""
    request_line = sys.stdin.readline()
    if not request_line:
        logger.error("Failed to read request from stdin")
        sys.exit(1)

    try:
        return json.loads(request_line)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse request: {request_line}")
        sys.exit(1)


def write_response(response: Dict[str, Any]) -> None:
    """Write a response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def handle_search_pairs(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle search pairs request.

    Args:
        params: Dictionary containing search parameters

    Returns:
        Response dictionary with search results
    """
    search_query = params.get("query")
    if not search_query:
        return {"error": "Missing required parameter: query"}

    try:
        response = requests.get(
            f"{DEXSCREENER_API_URL}/dex/search", params={"q": search_query}
        )
        response.raise_for_status()
        data = response.json()
        return {"pairs": data.get("pairs", [])}
    except requests.RequestException as e:
        logger.error(f"Error searching pairs: {str(e)}")
        return {"error": f"Failed to search pairs: {str(e)}"}


def handle_get_pair(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get pair request.

    Args:
        params: Dictionary containing pair parameters

    Returns:
        Response dictionary with pair data
    """
    pair_address = params.get("pairAddress")
    if not pair_address:
        return {"error": "Missing required parameter: pairAddress"}

    try:
        response = requests.get(f"{DEXSCREENER_API_URL}/dex/pairs/{pair_address}")
        response.raise_for_status()
        data = response.json()
        return {"pair": data.get("pairs", [])[0] if data.get("pairs") else None}
    except requests.RequestException as e:
        logger.error(f"Error getting pair: {str(e)}")
        return {"error": f"Failed to get pair: {str(e)}"}


def handle_get_token(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle get token request.

    Args:
        params: Dictionary containing token parameters

    Returns:
        Response dictionary with token data
    """
    token_address = params.get("tokenAddress")
    if not token_address:
        return {"error": "Missing required parameter: tokenAddress"}

    try:
        response = requests.get(f"{DEXSCREENER_API_URL}/dex/tokens/{token_address}")
        response.raise_for_status()
        data = response.json()
        return {"pairs": data.get("pairs", [])}
    except requests.RequestException as e:
        logger.error(f"Error getting token: {str(e)}")
        return {"error": f"Failed to get token: {str(e)}"}


def process_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an MCP request.

    Args:
        request: MCP request dictionary

    Returns:
        Response dictionary
    """
    request_type = request.get("type")

    if request_type == "init":
        # Initialize the server
        return {
            "actions": [
                {
                    "name": "search_pairs",
                    "description": "Search for pairs by token name, token symbol, or pair address",
                    "parameters": {
                        "query": {
                            "type": "string",
                            "description": "Search query (token name, symbol, or address)",
                        }
                    },
                },
                {
                    "name": "get_pair",
                    "description": "Get data for a specific trading pair by address",
                    "parameters": {
                        "pairAddress": {
                            "type": "string",
                            "description": "The pair contract address",
                        }
                    },
                },
                {
                    "name": "get_token",
                    "description": "Get all pairs for a specific token by address",
                    "parameters": {
                        "tokenAddress": {
                            "type": "string",
                            "description": "The token contract address",
                        }
                    },
                },
            ]
        }

    elif request_type == "action":
        action = request.get("action")
        params = request.get("parameters", {})

        if action == "search_pairs":
            return handle_search_pairs(params)
        elif action == "get_pair":
            return handle_get_pair(params)
        elif action == "get_token":
            return handle_get_token(params)
        else:
            return {"error": f"Unknown action: {action}"}

    else:
        return {"error": f"Unknown request type: {request_type}"}


def main():
    """Main function to run the MCP server."""
    logger.info("Starting DexScreener MCP server")

    while True:
        try:
            request = read_request()
            response = process_request(request)
            write_response(response)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            write_response({"error": f"Internal server error: {str(e)}"})


if __name__ == "__main__":
    main()
