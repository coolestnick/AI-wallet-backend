# RugCheck MCP Server

This is a Model Context Protocol (MCP) server for RugCheck, allowing AI agents to analyze Solana tokens for potential risks using the Solsniffer API.

## Overview

The RugCheck MCP server provides access to the Solsniffer API, which offers risk analysis for Solana tokens. This server allows AI agents to:

1. Analyze a Solana token for its risk profile
2. Retrieve structured risk and audit information

## Installation

Ensure you have Python 3.10+ installed, along with the following dependencies:

```bash
pip install requests python-dotenv
```

These dependencies should already be included in the main project's requirements.txt and pyproject.toml files.

## Configuration

Set your Solsniffer API key as an environment variable:

```
SOLSNIFFER_API_KEY=your_solsniffer_api_key_here
```

You can add this to your `.env` file or export it in your shell.

## Usage

### Standard MCP Server (STDIO)

The standard MCP server uses STDIO for communication with the AI agent. To start the server:

```bash
python -m app.mcp.rugcheck.run
```

## API Actions

### analysis_token
Analyze a Solana token for risk profile using the Solsniffer API.

Parameters:
- `token_address`: The Solana token address to analyze (string)

## Example Usage in Agent Prompt

```
You can check Solana token risks using the RugCheck MCP server.

Example command:
- To analyze a token: analysis_token with token_address="9VxExA1iRPbuLLdSJ2rB3nyBxsyLReT4aqzZBMaBaY1p"
```

## Credits

This MCP server is built using the [Solsniffer API](https://solsniffer.com/), which requires an API key. 