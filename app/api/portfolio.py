from fastapi import APIRouter, HTTPException, Query

from app.models.portfolio import Portfolio, PortfolioPerformanceResponse
from app.services.portfolio import (PortfolioWatcher,
                                    calculate_portfolio_performance)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# Create a single instance of the PortfolioWatcher
portfolio_watcher = PortfolioWatcher()


@router.get("/performance", response_model=PortfolioPerformanceResponse)
def get_portfolio_performance(user_id: str = Query(..., description="User ID")):
    """Get performance metrics for a user's portfolio."""
    return calculate_portfolio_performance(user_id)


@router.get("/{user_id}", response_model=Portfolio)
def get_portfolio(user_id: str):
    """
    Get a user's portfolio with up-to-date cryptocurrency prices from DexScreener.

    This endpoint uses the DexScreener MCP server to fetch real-time prices
    for all cryptocurrency assets in the user's portfolio.
    """
    portfolio = portfolio_watcher.get_portfolio(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.get("/price/{token_address}")
def get_token_price(token_address: str):
    """
    Get the current price of a token using DexScreener.

    This endpoint uses the DexScreener MCP server to fetch the price
    of a cryptocurrency token by its contract address.
    """
    from app.services.crypto_price import CryptoPriceService

    price_service = CryptoPriceService()
    price = price_service.get_token_price(token_address)

    if price is None:
        raise HTTPException(status_code=404, detail="Token price not found")

    return {"token_address": token_address, "price_usd": price}
