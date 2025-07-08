#!/usr/bin/env python
"""
DexScreener MCP Server SSE Launcher

This script launches the DexScreener MCP server with Server-Sent Events (SSE)
for use with AI agents over HTTP.
"""

import argparse
import os
import sys

# Add the parent directory to the Python path to allow imports
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from app.mcp.dexscreener.server_sse import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DexScreener MCP SSE Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )

    args = parser.parse_args()
    main(host=args.host, port=args.port)
