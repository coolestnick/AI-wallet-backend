"""
DexScreener MCP Server (SSE Version)

This module implements a Model Context Protocol (MCP) server for DexScreener using
Server-Sent Events (SSE), allowing AI agents to fetch cryptocurrency prices
from the DexScreener API over HTTP.
"""

import json
import logging
from typing import Any, Dict, Optional

import requests
from flask import Flask, Response, request, stream_with_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("dexscreener-mcp-sse")

# DexScreener API base URL
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest"

app = Flask(__name__)


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


def process_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an MCP request.

    Args:
        request_data: MCP request dictionary

    Returns:
        Response dictionary
    """
    request_type = request_data.get("type")

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
        action = request_data.get("action")
        params = request_data.get("parameters", {})

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


@app.route("/mcp/dexscreener", methods=["POST"])
def mcp_endpoint():
    """Handle MCP requests via HTTP POST."""
    try:
        request_data = request.json
        if not request_data:
            return {"error": "Invalid JSON request"}, 400

        response = process_request(request_data)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}, 500


@app.route("/mcp/dexscreener/sse", methods=["GET"])
def mcp_sse():
    """Handle MCP requests via Server-Sent Events (SSE)."""

    def event_stream():
        yield "data: " + json.dumps({"type": "ready"}) + "\n\n"

        # Keep the connection open
        while True:
            try:
                data = request.args.get("data")
                if not data:
                    continue

                request_data = json.loads(data)
                response = process_request(request_data)

                yield "data: " + json.dumps(response) + "\n\n"
            except Exception as e:
                logger.error(f"Error in SSE stream: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(event_stream()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def main(host="0.0.0.0", port=5000):
    """Main function to run the MCP SSE server."""
    logger.info(f"Starting DexScreener MCP SSE server on {host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
