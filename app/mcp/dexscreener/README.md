# DexScreener MCP Server

This is a Model Context Protocol (MCP) server for DexScreener, allowing AI agents to fetch cryptocurrency prices from the DexScreener API.

## Overview

The DexScreener MCP server provides access to the DexScreener API, which offers information about cryptocurrency trading pairs across various decentralized exchanges. This server allows AI agents to:

1. Search for trading pairs by token name, symbol, or address
2. Get detailed information about a specific trading pair
3. Get all pairs for a specific token

## Installation

Ensure you have Python 3.8+ installed, along with the following dependencies:

```bash
pip install requests flask
```

These dependencies should already be included in the main project's requirements.txt file.

## Usage

### Standard MCP Server (STDIO)

The standard MCP server uses STDIO for communication with the AI agent. To start the server:

```bash
python -m app.mcp.dexscreener.run
```

### Server-Sent Events (SSE) MCP Server

The SSE version can be hosted on a remote server and accessed via HTTP. To start the SSE server:

```bash
python -m app.mcp.dexscreener.run_sse --host 0.0.0.0 --port 5000
```

## Integration with Portfolio Agent

The DexScreener MCP server has been integrated with the portfolio agent to provide real-time cryptocurrency price data. This integration allows the portfolio agent to:

1. Fetch current prices for all assets in a user's portfolio
2. Calculate the total value of a portfolio in USD
3. Analyze portfolio performance based on current market data

### Services

The integration is implemented through the following services:

- **CryptoPriceService**: A service that communicates with the DexScreener MCP server to fetch cryptocurrency prices.
- **PortfolioWatcher**: A service that uses CryptoPriceService to update prices for all assets in a portfolio.
- **PortfolioPerformanceAgent**: A service that analyzes portfolio performance based on current prices.

### API Endpoints

The following API endpoints are available for interacting with portfolios:

- `GET /portfolio/{user_id}`: Get a user's portfolio with current prices from DexScreener
- `GET /portfolio/performance`: Get performance metrics for a user's portfolio
- `GET /portfolio/price/{token_address}`: Get the current price of a specific token

### Testing the Integration

To test the integration, run the provided test script:

```bash
python app/mcp/dexscreener/test_integration.py
```

This script demonstrates:
1. Fetching prices for individual tokens
2. Searching for trading pairs
3. Creating a portfolio and updating all asset prices
4. Calculating the total portfolio value

## Integration with Claude Desktop

To integrate with Claude Desktop, edit the `claude_desktop_config.json` file:

### On MacOS
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### On Windows
```bash
code $env:AppData\Claude\claude_desktop_config.json
```

Add the following configuration:

```json
{
  "mcpServers": {
    "dexscreener": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/app/mcp/dexscreener/run.py"
      ]
    }
  }
}
```

## API Actions

### search_pairs
Search for pairs by token name, token symbol, or pair address.

Parameters:
- `query`: Search query (token name, symbol, or address)

### get_pair
Get data for a specific trading pair by address.

Parameters:
- `pairAddress`: The pair contract address

### get_token
Get all pairs for a specific token by address.

Parameters:
- `tokenAddress`: The token contract address

## Example Usage in Agent Prompt

```
You can check cryptocurrency prices using the DexScreener API by calling the DexScreener MCP server.

Example commands:
- To search for a token: search_pairs with query="ethereum"
- To get a specific pair: get_pair with pairAddress="0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
- To get pairs for a token: get_token with tokenAddress="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
```

## Credits

This MCP server is built using the [DexScreener API](https://docs.dexscreener.com/api/reference), which is free and open for public use. 