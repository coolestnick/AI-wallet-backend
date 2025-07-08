#!/usr/bin/env python
"""
DeFiLlama MCP Server Launcher

This script launches the DeFiLlama MCP server for use with AI agents.
"""

import subprocess
import sys

if __name__ == "__main__":
    # Launch the server using uv
    proc = subprocess.Popen([
        "uv", "run", "defillama.py"
    ])
    proc.wait() 