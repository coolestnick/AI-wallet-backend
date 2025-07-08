from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
import logging

from ..services.unified_crypto_api import get_unified_api, UnifiedCryptoAPI

# Configure logging
logger = logging.getLogger("crypto_data_api")

# Create router
router = APIRouter(prefix="/crypto", tags=["crypto-data"])


@router.get("/search")
async def search_tokens(
    query: str = Query(..., description="Search query (token name, symbol, or address)"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Search for tokens across all data sources (DexScreener, GeckoTerminal)
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary containing search results from multiple sources
    """
    try:
        results = await unified_api.search_tokens_unified(query)
        return {
            "query": query,
            "results": results,
            "total_results": {
                "dexscreener": len(results.get("dexscreener_pairs", [])),
                "geckoterminal": len(results.get("geckoterminal_pairs", [])),
            }
        }
    except Exception as e:
        logger.error(f"Error searching tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search tokens: {str(e)}")


@router.get("/pairs/dexscreener")
async def search_dexscreener_pairs(
    query: str = Query(..., description="Search query for DexScreener"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Search for trading pairs on DexScreener
    
    Args:
        query: Search query string
        
    Returns:
        List of trading pairs from DexScreener
    """
    try:
        pairs = await unified_api.search_pairs_dexscreener(query)
        return {
            "query": query,
            "source": "dexscreener",
            "pairs": [pair.__dict__ for pair in pairs],
            "count": len(pairs)
        }
    except Exception as e:
        logger.error(f"Error searching DexScreener pairs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search DexScreener pairs: {str(e)}")


@router.get("/pairs/dexscreener/{pair_address}")
async def get_dexscreener_pair(
    pair_address: str,
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get specific trading pair data from DexScreener
    
    Args:
        pair_address: The contract address of the trading pair
        
    Returns:
        Trading pair data from DexScreener
    """
    try:
        pair = await unified_api.get_pair_dexscreener(pair_address)
        if not pair:
            raise HTTPException(status_code=404, detail="Trading pair not found")
        
        return {
            "pair_address": pair_address,
            "source": "dexscreener", 
            "pair": pair.__dict__
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting DexScreener pair: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get DexScreener pair: {str(e)}")


@router.get("/pools/geckoterminal/trending")
async def get_geckoterminal_trending(
    network: str = Query("eth", description="Network to get trending pools from"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get trending pools from GeckoTerminal
    
    Args:
        network: Network identifier (e.g., 'eth', 'bsc', 'solana')
        
    Returns:
        List of trending trading pools
    """
    try:
        pools = await unified_api.get_trending_pools_geckoterminal(network)
        return {
            "network": network,
            "source": "geckoterminal",
            "pools": [pool.__dict__ for pool in pools],
            "count": len(pools)
        }
    except Exception as e:
        logger.error(f"Error getting GeckoTerminal trending pools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending pools: {str(e)}")


@router.get("/pools/geckoterminal/search")
async def search_geckoterminal_pools(
    query: str = Query(..., description="Search query for pools"),
    network: str = Query("eth", description="Network to search in"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Search for pools on GeckoTerminal
    
    Args:
        query: Search query string
        network: Network identifier
        
    Returns:
        List of matching pools from GeckoTerminal
    """
    try:
        pools = await unified_api.search_pools_geckoterminal(query, network)
        return {
            "query": query,
            "network": network,
            "source": "geckoterminal",
            "pools": [pool.__dict__ for pool in pools],
            "count": len(pools)
        }
    except Exception as e:
        logger.error(f"Error searching GeckoTerminal pools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search pools: {str(e)}")


@router.get("/protocols/defillama")
async def get_defillama_protocols(
    limit: int = Query(50, description="Maximum number of protocols to return"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get DeFi protocols from DefiLlama
    
    Args:
        limit: Maximum number of protocols to return
        
    Returns:
        List of DeFi protocols with TVL data
    """
    try:
        protocols = await unified_api.get_protocols_defillama()
        # Sort by TVL and limit results
        sorted_protocols = sorted(protocols, key=lambda x: x.tvl, reverse=True)[:limit]
        
        return {
            "source": "defillama",
            "protocols": [protocol.__dict__ for protocol in sorted_protocols],
            "count": len(sorted_protocols),
            "total_available": len(protocols)
        }
    except Exception as e:
        logger.error(f"Error getting DefiLlama protocols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get protocols: {str(e)}")


@router.get("/protocols/defillama/{protocol_slug}")
async def get_defillama_protocol(
    protocol_slug: str,
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get specific protocol data from DefiLlama
    
    Args:
        protocol_slug: Protocol identifier slug
        
    Returns:
        Protocol data from DefiLlama
    """
    try:
        protocol = await unified_api.get_protocol_tvl_defillama(protocol_slug)
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        return {
            "protocol_slug": protocol_slug,
            "source": "defillama",
            "protocol": protocol.__dict__
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting DefiLlama protocol: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get protocol: {str(e)}")


@router.get("/chains/defillama/{chain}")
async def get_defillama_chain_tvl(
    chain: str,
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get TVL data for a specific blockchain from DefiLlama
    
    Args:
        chain: Blockchain identifier (e.g., 'ethereum', 'bsc', 'solana')
        
    Returns:
        Chain TVL data from DefiLlama
    """
    try:
        chain_data = await unified_api.get_chain_tvl_defillama(chain)
        if not chain_data:
            raise HTTPException(status_code=404, detail="Chain not found")
        
        return {
            "chain": chain,
            "source": "defillama",
            "data": chain_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting DefiLlama chain TVL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chain TVL: {str(e)}")


@router.get("/prices/coingecko")
async def get_coingecko_prices(
    coin_ids: str = Query(..., description="Comma-separated list of CoinGecko coin IDs"),
    vs_currencies: str = Query("usd", description="Comma-separated list of vs currencies"),
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get token prices from CoinGecko
    
    Args:
        coin_ids: Comma-separated CoinGecko coin IDs (e.g., 'bitcoin,ethereum,solana')
        vs_currencies: Comma-separated currencies (e.g., 'usd,eur,btc')
        
    Returns:
        Token price data from CoinGecko
    """
    try:
        coin_list = [coin.strip() for coin in coin_ids.split(",")]
        currency_list = [curr.strip() for curr in vs_currencies.split(",")]
        
        prices = await unified_api.get_prices_coingecko(coin_list, currency_list)
        
        return {
            "coin_ids": coin_list,
            "vs_currencies": currency_list,
            "source": "coingecko",
            "prices": {k: v.__dict__ for k, v in prices.items()},
            "count": len(prices)
        }
    except Exception as e:
        logger.error(f"Error getting CoinGecko prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {str(e)}")


@router.get("/market/overview")
async def get_market_overview(
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get comprehensive market overview from all data sources
    
    Returns:
        Market overview including trending pairs, top protocols, and price summary
    """
    try:
        overview = await unified_api.get_market_overview()
        
        # Convert dataclass objects to dictionaries
        result = {
            "trending_pairs": [pair.__dict__ for pair in overview.get("trending_pairs", [])],
            "top_protocols": [protocol.__dict__ for protocol in overview.get("top_protocols", [])],
            "market_summary": {k: v.__dict__ for k, v in overview.get("market_summary", {}).items()},
            "sources": ["dexscreener", "geckoterminal", "defillama", "coingecko"]
        }
        
        return result
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market overview: {str(e)}")


@router.get("/status")
async def get_api_status(
    unified_api: UnifiedCryptoAPI = Depends(get_unified_api)
) -> Dict[str, Any]:
    """
    Get status of all configured APIs
    
    Returns:
        Status information for all integrated APIs
    """
    try:
        status = unified_api.get_api_status()
        return {
            "apis": status,
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get API status: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for crypto data API"""
    return {
        "status": "healthy",
        "service": "crypto_data_api",
        "apis": ["dexscreener", "defillama", "geckoterminal", "coingecko"]
    }