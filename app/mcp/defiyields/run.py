#!/usr/bin/env python
"""
DeFi Yields MCP Server Launcher

This script launches the DeFi Yields MCP server for use with AI agents.
"""

import subprocess
import sys

if __name__ == "__main__":
    # Launch the server using uvx
    proc = subprocess.Popen([
        sys.executable.replace("python", "uvx"),
        "defi-yields-mcp"
    ])
    proc.wait() 