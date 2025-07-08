#!/usr/bin/env python
"""
DexScreener MCP Server Launcher

This script launches the DexScreener MCP server for use with AI agents.
"""

import os
import sys

# Add the parent directory to the Python path to allow imports
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from app.mcp.dexscreener.server import main

if __name__ == "__main__":
    main()
