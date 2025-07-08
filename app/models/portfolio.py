from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class CryptoAsset(BaseModel):
    """Represents a cryptocurrency asset in a portfolio."""

    token_address: str
    symbol: str
    name: str
    quantity: float
    network: str
    current_price: Optional[float] = None
    value_usd: Optional[float] = None


class Portfolio(BaseModel):
    """Represents a user's investment portfolio."""

    user_id: str
    crypto_assets: List[CryptoAsset] = []
    total_value_usd: Optional[float] = None
    last_updated: Optional[str] = None


class PortfolioPerformance(BaseModel):
    growth: float
    drawdown: float
    volatility: float
    summary: str


class PortfolioPerformanceResponse(BaseModel):
    user_id: str
    performance: PortfolioPerformance
