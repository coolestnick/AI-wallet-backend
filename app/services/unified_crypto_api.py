import os
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger("unified_crypto_api")


class DataSource(Enum):
    """Enumeration of supported data sources"""
    DEXSCREENER = "dexscreener"
    DEFILLAMA = "defillama" 
    GECKOTERMINAL = "geckoterminal"
    COINGECKO = "coingecko"


@dataclass
class TokenPrice:
    """Token price data structure"""
    symbol: str
    price_usd: float
    price_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class TradingPair:
    """Trading pair data structure"""
    pair_address: str
    base_token: str
    quote_token: str
    price_usd: float
    volume_24h: float
    liquidity: Optional[float] = None
    price_change_24h: Optional[float] = None
    dex: Optional[str] = None
    chain: Optional[str] = None
    source: Optional[str] = None


@dataclass
class ProtocolData:
    """DeFi protocol data structure"""
    name: str
    tvl: float
    chain: str
    category: Optional[str] = None
    change_1d: Optional[float] = None
    change_7d: Optional[float] = None
    mcap: Optional[float] = None
    source: Optional[str] = None


class UnifiedCryptoAPI:
    """
    Unified API service that integrates multiple crypto data sources:
    - DexScreener: DEX trading data
    - DefiLlama: DeFi protocol TVL data
    - GeckoTerminal: Advanced trading analytics
    - CoinGecko: General crypto market data
    """

    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        
        # API configuration from environment
        self.apis = {
            DataSource.DEXSCREENER: {
                "base_url": os.getenv("DEXSCREENER_API_URL", "https://api.dexscreener.com/latest"),
                "api_key": os.getenv("DEXSCREENER_API_KEY"),
                "headers": self._get_headers(DataSource.DEXSCREENER)
            },
            DataSource.DEFILLAMA: {
                "base_url": os.getenv("DEFILLAMA_API_URL", "https://api.llama.fi"),
                "api_key": os.getenv("DEFILLAMA_API_KEY"), 
                "headers": self._get_headers(DataSource.DEFILLAMA)
            },
            DataSource.GECKOTERMINAL: {
                "base_url": os.getenv("GECKOTERMINAL_API_URL", "https://api.geckoterminal.com/api/v2"),
                "api_key": os.getenv("GECKOTERMINAL_API_KEY"),
                "headers": self._get_headers(DataSource.GECKOTERMINAL)
            },
            DataSource.COINGECKO: {
                "base_url": os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3"),
                "api_key": os.getenv("COINGECKO_API_KEY"),
                "headers": self._get_headers(DataSource.COINGECKO)
            }
        }

    def _get_headers(self, source: DataSource) -> Dict[str, str]:
        """Get appropriate headers for each API"""
        base_headers = {
            "User-Agent": "Salt Wallet/1.0",
            "Accept": "application/json"
        }
        
        api_key = os.getenv(f"{source.value.upper()}_API_KEY")
        if api_key:
            if source == DataSource.COINGECKO:
                base_headers["x-cg-demo-api-key"] = api_key
            elif source == DataSource.GECKOTERMINAL:
                base_headers["Authorization"] = f"Bearer {api_key}"
            # DexScreener and DefiLlama typically don't require API keys for basic endpoints
                
        return base_headers

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

    # =============================================================================
    # DEXSCREENER API METHODS
    # =============================================================================

    async def search_pairs_dexscreener(self, query: str) -> List[TradingPair]:
        """Search for trading pairs on DexScreener"""
        try:
            url = f"{self.apis[DataSource.DEXSCREENER]['base_url']}/dex/search"
            params = {"q": query}
            
            response = await self.session.get(
                url, 
                params=params,
                headers=self.apis[DataSource.DEXSCREENER]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            pairs = []
            for pair_data in data.get("pairs", []):
                pairs.append(TradingPair(
                    pair_address=pair_data.get("pairAddress", ""),
                    base_token=pair_data.get("baseToken", {}).get("symbol", ""),
                    quote_token=pair_data.get("quoteToken", {}).get("symbol", ""),
                    price_usd=float(pair_data.get("priceUsd", 0)),
                    volume_24h=float(pair_data.get("volume", {}).get("h24", 0)),
                    liquidity=float(pair_data.get("liquidity", {}).get("usd", 0)) if pair_data.get("liquidity") else None,
                    price_change_24h=float(pair_data.get("priceChange", {}).get("h24", 0)) if pair_data.get("priceChange") else None,
                    dex=pair_data.get("dexId", ""),
                    chain=pair_data.get("chainId", ""),
                    source=DataSource.DEXSCREENER.value
                ))
            
            return pairs
            
        except Exception as e:
            logger.error(f"Error searching DexScreener pairs: {e}")
            return []

    async def get_pair_dexscreener(self, pair_address: str) -> Optional[TradingPair]:
        """Get specific pair data from DexScreener"""
        try:
            url = f"{self.apis[DataSource.DEXSCREENER]['base_url']}/dex/pairs/{pair_address}"
            
            response = await self.session.get(
                url,
                headers=self.apis[DataSource.DEXSCREENER]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("pairs") and len(data["pairs"]) > 0:
                pair_data = data["pairs"][0]
                return TradingPair(
                    pair_address=pair_data.get("pairAddress", ""),
                    base_token=pair_data.get("baseToken", {}).get("symbol", ""),
                    quote_token=pair_data.get("quoteToken", {}).get("symbol", ""),
                    price_usd=float(pair_data.get("priceUsd", 0)),
                    volume_24h=float(pair_data.get("volume", {}).get("h24", 0)),
                    liquidity=float(pair_data.get("liquidity", {}).get("usd", 0)) if pair_data.get("liquidity") else None,
                    price_change_24h=float(pair_data.get("priceChange", {}).get("h24", 0)) if pair_data.get("priceChange") else None,
                    dex=pair_data.get("dexId", ""),
                    chain=pair_data.get("chainId", ""),
                    source=DataSource.DEXSCREENER.value
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting DexScreener pair: {e}")
            return None

    # =============================================================================
    # DEFILLAMA API METHODS
    # =============================================================================

    async def get_protocols_defillama(self) -> List[ProtocolData]:
        """Get all DeFi protocols from DefiLlama"""
        try:
            url = f"{self.apis[DataSource.DEFILLAMA]['base_url']}/protocols"
            
            response = await self.session.get(
                url,
                headers=self.apis[DataSource.DEFILLAMA]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            protocols = []
            for protocol in data:
                protocols.append(ProtocolData(
                    name=protocol.get("name", ""),
                    tvl=float(protocol.get("tvl", 0)),
                    chain=protocol.get("chain", ""),
                    category=protocol.get("category"),
                    change_1d=float(protocol.get("change_1d", 0)) if protocol.get("change_1d") else None,
                    change_7d=float(protocol.get("change_7d", 0)) if protocol.get("change_7d") else None,
                    mcap=float(protocol.get("mcap", 0)) if protocol.get("mcap") else None,
                    source=DataSource.DEFILLAMA.value
                ))
            
            return protocols
            
        except Exception as e:
            logger.error(f"Error getting DefiLlama protocols: {e}")
            return []

    async def get_protocol_tvl_defillama(self, protocol_slug: str) -> Optional[ProtocolData]:
        """Get specific protocol TVL from DefiLlama"""
        try:
            url = f"{self.apis[DataSource.DEFILLAMA]['base_url']}/protocol/{protocol_slug}"
            
            response = await self.session.get(
                url,
                headers=self.apis[DataSource.DEFILLAMA]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                return ProtocolData(
                    name=data.get("name", ""),
                    tvl=float(data.get("tvl", 0)),
                    chain=data.get("chain", ""),
                    category=data.get("category"),
                    source=DataSource.DEFILLAMA.value
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting DefiLlama protocol TVL: {e}")
            return None

    async def get_chain_tvl_defillama(self, chain: str) -> Dict[str, Any]:
        """Get TVL for a specific chain from DefiLlama"""
        try:
            url = f"{self.apis[DataSource.DEFILLAMA]['base_url']}/chains"
            
            response = await self.session.get(
                url,
                headers=self.apis[DataSource.DEFILLAMA]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            for chain_data in data:
                if chain_data.get("name", "").lower() == chain.lower():
                    return {
                        "chain": chain_data.get("name", ""),
                        "tvl": float(chain_data.get("tvl", 0)),
                        "change_1d": float(chain_data.get("change_1d", 0)) if chain_data.get("change_1d") else None,
                        "change_7d": float(chain_data.get("change_7d", 0)) if chain_data.get("change_7d") else None,
                        "source": DataSource.DEFILLAMA.value
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting DefiLlama chain TVL: {e}")
            return {}

    # =============================================================================
    # GECKOTERMINAL API METHODS  
    # =============================================================================

    async def get_trending_pools_geckoterminal(self, network: str = "eth") -> List[TradingPair]:
        """Get trending pools from GeckoTerminal"""
        try:
            url = f"{self.apis[DataSource.GECKOTERMINAL]['base_url']}/networks/{network}/trending_pools"
            
            response = await self.session.get(
                url,
                headers=self.apis[DataSource.GECKOTERMINAL]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            pairs = []
            for pool in data.get("data", []):
                attributes = pool.get("attributes", {})
                pairs.append(TradingPair(
                    pair_address=pool.get("id", ""),
                    base_token=attributes.get("base_token_symbol", ""),
                    quote_token=attributes.get("quote_token_symbol", ""),
                    price_usd=float(attributes.get("base_token_price_usd", 0)),
                    volume_24h=float(attributes.get("volume_usd", {}).get("h24", 0)),
                    liquidity=float(attributes.get("reserve_in_usd", 0)) if attributes.get("reserve_in_usd") else None,
                    price_change_24h=float(attributes.get("price_change_percentage", {}).get("h24", 0)) if attributes.get("price_change_percentage") else None,
                    dex=attributes.get("dex_id", ""),
                    chain=network,
                    source=DataSource.GECKOTERMINAL.value
                ))
            
            return pairs
            
        except Exception as e:
            logger.error(f"Error getting GeckoTerminal trending pools: {e}")
            return []

    async def search_pools_geckoterminal(self, query: str, network: str = "eth") -> List[TradingPair]:
        """Search pools on GeckoTerminal"""
        try:
            url = f"{self.apis[DataSource.GECKOTERMINAL]['base_url']}/search/pools"
            params = {"query": query, "network": network}
            
            response = await self.session.get(
                url,
                params=params,
                headers=self.apis[DataSource.GECKOTERMINAL]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            pairs = []
            for pool in data.get("data", []):
                attributes = pool.get("attributes", {})
                pairs.append(TradingPair(
                    pair_address=pool.get("id", ""),
                    base_token=attributes.get("base_token_symbol", ""),
                    quote_token=attributes.get("quote_token_symbol", ""),
                    price_usd=float(attributes.get("base_token_price_usd", 0)),
                    volume_24h=float(attributes.get("volume_usd", {}).get("h24", 0)),
                    liquidity=float(attributes.get("reserve_in_usd", 0)) if attributes.get("reserve_in_usd") else None,
                    price_change_24h=float(attributes.get("price_change_percentage", {}).get("h24", 0)) if attributes.get("price_change_percentage") else None,
                    dex=attributes.get("dex_id", ""),
                    chain=network,
                    source=DataSource.GECKOTERMINAL.value
                ))
            
            return pairs
            
        except Exception as e:
            logger.error(f"Error searching GeckoTerminal pools: {e}")
            return []

    # =============================================================================
    # COINGECKO API METHODS
    # =============================================================================

    async def get_prices_coingecko(self, coin_ids: List[str], vs_currencies: List[str] = ["usd"]) -> Dict[str, TokenPrice]:
        """Get token prices from CoinGecko"""
        try:
            url = f"{self.apis[DataSource.COINGECKO]['base_url']}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": ",".join(vs_currencies),
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            response = await self.session.get(
                url,
                params=params,
                headers=self.apis[DataSource.COINGECKO]["headers"]
            )
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for coin_id, coin_data in data.items():
                for currency in vs_currencies:
                    if currency in coin_data:
                        prices[f"{coin_id}_{currency}"] = TokenPrice(
                            symbol=coin_id,
                            price_usd=float(coin_data[currency]),
                            price_change_24h=float(coin_data.get(f"{currency}_24h_change", 0)),
                            market_cap=float(coin_data.get(f"{currency}_market_cap", 0)) if coin_data.get(f"{currency}_market_cap") else None,
                            volume_24h=float(coin_data.get(f"{currency}_24h_vol", 0)) if coin_data.get(f"{currency}_24h_vol") else None,
                            source=DataSource.COINGECKO.value,
                            timestamp=datetime.now()
                        )
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko prices: {e}")
            return {}

    # =============================================================================
    # UNIFIED METHODS
    # =============================================================================

    async def search_tokens_unified(self, query: str) -> Dict[str, List[Union[TradingPair, TokenPrice]]]:
        """Search for tokens across all data sources"""
        results = {
            "dexscreener_pairs": [],
            "geckoterminal_pairs": [],
            "coingecko_prices": []
        }
        
        # Search in parallel across all sources
        tasks = [
            self.search_pairs_dexscreener(query),
            self.search_pools_geckoterminal(query),
            # Note: CoinGecko search requires specific coin IDs
        ]
        
        try:
            dex_results, gecko_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(dex_results, Exception):
                results["dexscreener_pairs"] = dex_results
            if not isinstance(gecko_results, Exception):
                results["geckoterminal_pairs"] = gecko_results
                
        except Exception as e:
            logger.error(f"Error in unified token search: {e}")
        
        return results

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview from all sources"""
        overview = {
            "trending_pairs": [],
            "top_protocols": [],
            "market_summary": {}
        }
        
        try:
            # Get data from all sources in parallel
            tasks = [
                self.get_trending_pools_geckoterminal(),
                self.get_protocols_defillama(),
                self.get_prices_coingecko(["bitcoin", "ethereum", "solana"])
            ]
            
            trending, protocols, prices = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(trending, Exception):
                overview["trending_pairs"] = trending[:10]  # Top 10
            if not isinstance(protocols, Exception):
                overview["top_protocols"] = sorted(protocols, key=lambda x: x.tvl, reverse=True)[:10]  # Top 10 by TVL
            if not isinstance(prices, Exception):
                overview["market_summary"] = prices
                
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
        
        return overview

    def get_api_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured APIs"""
        status = {}
        
        for source, config in self.apis.items():
            status[source.value] = {
                "configured": bool(config["api_key"]) if source != DataSource.DEXSCREENER else True,  # DexScreener doesn't require API key
                "base_url": config["base_url"],
                "has_api_key": bool(config["api_key"])
            }
        
        return status


# Global instance
unified_api = UnifiedCryptoAPI()


async def get_unified_api() -> UnifiedCryptoAPI:
    """Get the global unified API instance"""
    return unified_api