#!/usr/bin/env python
"""
DexScreener MCP Integration Test

This script demonstrates the integration of the DexScreener MCP server
with the portfolio agent for fetching cryptocurrency prices.
"""

import json
import os
import sys
from datetime import datetime

# Add the parent directory to the Python path to allow imports
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)

from app.models.portfolio import CryptoAsset, Portfolio
from app.services.crypto_price import CryptoPriceService
from app.services.portfolio import PortfolioWatcher


def test_price_service():
    """Test the CryptoPriceService with a few well-known tokens."""
    print("\n=== Testing CryptoPriceService ===")

    # Create the price service
    price_service = CryptoPriceService()

    # Test tokens
    tokens = [
        {
            "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "symbol": "WETH",
        },  # Wrapped Ethereum
        {
            "address": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
            "symbol": "WBTC",
        },  # Wrapped Bitcoin
        {
            "address": "0x6b175474e89094c44da98b954eedeac495271d0f",
            "symbol": "DAI",
        },  # Dai Stablecoin
    ]

    for token in tokens:
        print(f"\nFetching price for {token['symbol']} ({token['address']}):")
        price = price_service.get_token_price(token["address"])
        print(f"Price: ${price if price is not None else 'Not found'}")

        # Search for the token
        print(f"\nSearching for {token['symbol']}:")
        search_result = price_service.search_pairs(token["symbol"])
        if "error" in search_result:
            print(f"Error: {search_result['error']}")
        else:
            # Print the first few results
            pairs = search_result.get("pairs", [])
            print(f"Found {len(pairs)} pairs")
            for i, pair in enumerate(pairs[:3]):  # Print first 3 results
                base_token = pair.get("baseToken", {})
                quote_token = pair.get("quoteToken", {})
                price_usd = pair.get("priceUsd", "N/A")
                print(
                    f"  {i+1}. {base_token.get('symbol', 'N/A')}/{quote_token.get('symbol', 'N/A')} - ${price_usd}"
                )


def test_portfolio_integration():
    """Test the integration with the portfolio agent."""
    print("\n=== Testing Portfolio Integration ===")

    # Create a sample portfolio
    portfolio = Portfolio(
        user_id="test_user",
        crypto_assets=[
            CryptoAsset(
                token_address="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
                symbol="WETH",
                name="Wrapped Ethereum",
                quantity=2.5,
                network="ethereum",
            ),
            CryptoAsset(
                token_address="0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
                symbol="WBTC",
                name="Wrapped Bitcoin",
                quantity=0.15,
                network="ethereum",
            ),
            CryptoAsset(
                token_address="0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
                symbol="DAI",
                name="Dai Stablecoin",
                quantity=1000,
                network="ethereum",
            ),
        ],
    )

    # Create the portfolio watcher and update prices
    watcher = PortfolioWatcher()
    updated_portfolio = watcher.update_portfolio_prices(portfolio)

    # Print the portfolio
    print(f"\nPortfolio for user {updated_portfolio.user_id}")
    print(f"Last updated: {updated_portfolio.last_updated}")
    print(f"Total value: ${updated_portfolio.total_value_usd:.2f}")
    print("\nAssets:")

    for asset in updated_portfolio.crypto_assets:
        print(f"  {asset.symbol} ({asset.name})")
        print(f"    Quantity: {asset.quantity}")
        print(
            f"    Price: ${asset.current_price:.2f}"
            if asset.current_price
            else "    Price: Not available"
        )
        print(
            f"    Value: ${asset.value_usd:.2f}"
            if asset.value_usd
            else "    Value: Not available"
        )


if __name__ == "__main__":
    # Run the tests
    test_price_service()
    test_portfolio_integration()
