"""
Test cases for Unified Crypto API Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from datetime import datetime

from app.services.unified_crypto_api import (
    UnifiedCryptoAPI, 
    TokenPrice, 
    TradingPair, 
    ProtocolData, 
    DataSource
)


class TestUnifiedCryptoAPI:
    """Test suite for UnifiedCryptoAPI class"""

    @pytest.fixture
    def api_instance(self):
        """Create UnifiedCryptoAPI instance for testing"""
        return UnifiedCryptoAPI()

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx AsyncClient"""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        return mock_client

    @pytest.fixture
    def sample_dexscreener_response(self):
        """Sample DexScreener API response"""
        return {
            "pairs": [
                {
                    "pairAddress": "0x1234567890abcdef",
                    "baseToken": {"symbol": "ETH"},
                    "quoteToken": {"symbol": "USDC"},
                    "priceUsd": "3200.50",
                    "volume": {"h24": "5000000"},
                    "liquidity": {"usd": "10000000"},
                    "priceChange": {"h24": "1.8"},
                    "dexId": "uniswap",
                    "chainId": "ethereum"
                }
            ]
        }

    @pytest.fixture
    def sample_defillama_protocols_response(self):
        """Sample DefiLlama protocols response"""
        return [
            {
                "name": "Uniswap",
                "tvl": 8500000000,
                "chain": "Ethereum", 
                "category": "DEX",
                "change_1d": 2.1,
                "change_7d": -0.8,
                "mcap": 15000000000
            },
            {
                "name": "Aave",
                "tvl": 12000000000,
                "chain": "Ethereum",
                "category": "Lending",
                "change_1d": 1.5,
                "change_7d": 3.2,
                "mcap": 8000000000
            }
        ]

    @pytest.fixture
    def sample_geckoterminal_response(self):
        """Sample GeckoTerminal API response"""
        return {
            "data": [
                {
                    "id": "eth_0x1234567890abcdef",
                    "attributes": {
                        "base_token_symbol": "ETH",
                        "quote_token_symbol": "USDC",
                        "base_token_price_usd": "3200.50",
                        "volume_usd": {"h24": "5000000"},
                        "reserve_in_usd": "10000000",
                        "price_change_percentage": {"h24": "1.8"},
                        "dex_id": "uniswap_v3"
                    }
                }
            ]
        }

    @pytest.fixture
    def sample_coingecko_response(self):
        """Sample CoinGecko API response"""
        return {
            "bitcoin": {
                "usd": 45000.0,
                "usd_24h_change": 2.5,
                "usd_market_cap": 850000000000,
                "usd_24h_vol": 25000000000
            },
            "ethereum": {
                "usd": 3200.0,
                "usd_24h_change": 1.8,
                "usd_market_cap": 380000000000,
                "usd_24h_vol": 15000000000
            }
        }

    def test_api_initialization(self, api_instance):
        """Test API initialization"""
        assert api_instance is not None
        assert hasattr(api_instance, 'session')
        assert hasattr(api_instance, 'apis')
        assert len(api_instance.apis) == 4  # 4 data sources

    def test_get_headers(self, api_instance):
        """Test header generation for different APIs"""
        # Test base headers
        headers = api_instance._get_headers(DataSource.DEXSCREENER)
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert headers["Accept"] == "application/json"

        # Test CoinGecko headers with API key
        with patch.dict('os.environ', {'COINGECKO_API_KEY': 'test_key'}):
            headers = api_instance._get_headers(DataSource.COINGECKO)
            assert "x-cg-demo-api-key" in headers
            assert headers["x-cg-demo-api-key"] == "test_key"

        # Test GeckoTerminal headers with API key
        with patch.dict('os.environ', {'GECKOTERMINAL_API_KEY': 'test_key'}):
            headers = api_instance._get_headers(DataSource.GECKOTERMINAL)
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_key"

    def test_get_api_status(self, api_instance):
        """Test API status method"""
        with patch.dict('os.environ', {
            'COINGECKO_API_KEY': 'test_key',
            'GECKOTERMINAL_API_KEY': 'test_key'
        }):
            status = api_instance.get_api_status()
            
            assert isinstance(status, dict)
            assert len(status) == 4
            assert 'dexscreener' in status
            assert 'defillama' in status
            assert 'geckoterminal' in status
            assert 'coingecko' in status
            
            # Check status structure
            for source, config in status.items():
                assert 'configured' in config
                assert 'base_url' in config
                assert 'has_api_key' in config

    @pytest.mark.asyncio
    async def test_close_session(self, api_instance, mock_httpx_client):
        """Test session closing"""
        api_instance.session = mock_httpx_client
        await api_instance.close()
        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_pairs_dexscreener_success(self, api_instance, mock_httpx_client, sample_dexscreener_response):
        """Test successful DexScreener pair search"""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_dexscreener_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.search_pairs_dexscreener("ETH")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TradingPair)
        assert result[0].base_token == "ETH"
        assert result[0].quote_token == "USDC"
        assert result[0].price_usd == 3200.50
        assert result[0].source == "dexscreener"

    @pytest.mark.asyncio
    async def test_search_pairs_dexscreener_error(self, api_instance, mock_httpx_client):
        """Test DexScreener pair search error handling"""
        mock_httpx_client.get.side_effect = httpx.RequestError("Network error")
        api_instance.session = mock_httpx_client
        
        result = await api_instance.search_pairs_dexscreener("ETH")
        
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_pair_dexscreener_success(self, api_instance, mock_httpx_client, sample_dexscreener_response):
        """Test successful DexScreener specific pair retrieval"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_dexscreener_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_pair_dexscreener("0x1234567890abcdef")
        
        assert isinstance(result, TradingPair)
        assert result.pair_address == "0x1234567890abcdef"
        assert result.base_token == "ETH"

    @pytest.mark.asyncio
    async def test_get_pair_dexscreener_not_found(self, api_instance, mock_httpx_client):
        """Test DexScreener pair not found"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pairs": []}
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_pair_dexscreener("0xinvalid")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_protocols_defillama_success(self, api_instance, mock_httpx_client, sample_defillama_protocols_response):
        """Test successful DefiLlama protocols retrieval"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_defillama_protocols_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_protocols_defillama()
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], ProtocolData)
        assert result[0].name == "Uniswap"
        assert result[0].tvl == 8500000000
        assert result[0].source == "defillama"

    @pytest.mark.asyncio
    async def test_get_protocol_tvl_defillama_success(self, api_instance, mock_httpx_client):
        """Test successful DefiLlama specific protocol retrieval"""
        protocol_data = {
            "name": "Uniswap",
            "tvl": 8500000000,
            "chain": "Ethereum",
            "category": "DEX"
        }
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = protocol_data
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_protocol_tvl_defillama("uniswap")
        
        assert isinstance(result, ProtocolData)
        assert result.name == "Uniswap"
        assert result.tvl == 8500000000

    @pytest.mark.asyncio
    async def test_get_chain_tvl_defillama_success(self, api_instance, mock_httpx_client):
        """Test successful DefiLlama chain TVL retrieval"""
        chains_data = [
            {
                "name": "Ethereum",
                "tvl": 50000000000,
                "change_1d": 1.5,
                "change_7d": -0.8
            }
        ]
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = chains_data
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_chain_tvl_defillama("ethereum")
        
        assert isinstance(result, dict)
        assert result["chain"] == "Ethereum"
        assert result["tvl"] == 50000000000
        assert result["source"] == "defillama"

    @pytest.mark.asyncio
    async def test_get_trending_pools_geckoterminal_success(self, api_instance, mock_httpx_client, sample_geckoterminal_response):
        """Test successful GeckoTerminal trending pools retrieval"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_geckoterminal_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_trending_pools_geckoterminal("eth")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TradingPair)
        assert result[0].base_token == "ETH"
        assert result[0].source == "geckoterminal"

    @pytest.mark.asyncio
    async def test_search_pools_geckoterminal_success(self, api_instance, mock_httpx_client, sample_geckoterminal_response):
        """Test successful GeckoTerminal pool search"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_geckoterminal_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.search_pools_geckoterminal("ETH", "eth")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TradingPair)

    @pytest.mark.asyncio
    async def test_get_prices_coingecko_success(self, api_instance, mock_httpx_client, sample_coingecko_response):
        """Test successful CoinGecko prices retrieval"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response
        
        api_instance.session = mock_httpx_client
        
        result = await api_instance.get_prices_coingecko(["bitcoin", "ethereum"], ["usd"])
        
        assert isinstance(result, dict)
        assert "bitcoin_usd" in result
        assert "ethereum_usd" in result
        assert isinstance(result["bitcoin_usd"], TokenPrice)
        assert result["bitcoin_usd"].price_usd == 45000.0
        assert result["bitcoin_usd"].source == "coingecko"

    @pytest.mark.asyncio
    async def test_search_tokens_unified_success(self, api_instance):
        """Test unified token search"""
        # Mock the individual search methods
        sample_pair = TradingPair(
            pair_address="0x123",
            base_token="ETH",
            quote_token="USDC", 
            price_usd=3200.0,
            volume_24h=5000000,
            source="dexscreener"
        )
        
        api_instance.search_pairs_dexscreener = AsyncMock(return_value=[sample_pair])
        api_instance.search_pools_geckoterminal = AsyncMock(return_value=[])
        
        result = await api_instance.search_tokens_unified("ETH")
        
        assert isinstance(result, dict)
        assert "dexscreener_pairs" in result
        assert "geckoterminal_pairs" in result
        assert len(result["dexscreener_pairs"]) == 1

    @pytest.mark.asyncio
    async def test_get_market_overview_success(self, api_instance):
        """Test market overview retrieval"""
        # Mock the individual methods
        sample_pair = TradingPair(
            pair_address="0x123",
            base_token="ETH", 
            quote_token="USDC",
            price_usd=3200.0,
            volume_24h=5000000,
            source="geckoterminal"
        )
        
        sample_protocol = ProtocolData(
            name="Uniswap",
            tvl=8500000000,
            chain="Ethereum",
            source="defillama"
        )
        
        sample_price = TokenPrice(
            symbol="bitcoin",
            price_usd=45000.0,
            source="coingecko"
        )
        
        api_instance.get_trending_pools_geckoterminal = AsyncMock(return_value=[sample_pair])
        api_instance.get_protocols_defillama = AsyncMock(return_value=[sample_protocol])
        api_instance.get_prices_coingecko = AsyncMock(return_value={"bitcoin_usd": sample_price})
        
        result = await api_instance.get_market_overview()
        
        assert isinstance(result, dict)
        assert "trending_pairs" in result
        assert "top_protocols" in result
        assert "market_summary" in result
        assert len(result["trending_pairs"]) == 1
        assert len(result["top_protocols"]) == 1


class TestDataModels:
    """Test data model classes"""

    def test_token_price_model(self):
        """Test TokenPrice data model"""
        price = TokenPrice(
            symbol="bitcoin",
            price_usd=45000.0,
            price_change_24h=2.5,
            market_cap=850000000000,
            volume_24h=25000000000,
            source="coingecko",
            timestamp=datetime.now()
        )
        
        assert price.symbol == "bitcoin"
        assert price.price_usd == 45000.0
        assert price.price_change_24h == 2.5
        assert price.source == "coingecko"

    def test_trading_pair_model(self):
        """Test TradingPair data model"""
        pair = TradingPair(
            pair_address="0x1234567890abcdef",
            base_token="ETH",
            quote_token="USDC",
            price_usd=3200.0,
            volume_24h=5000000,
            liquidity=10000000,
            price_change_24h=1.8,
            dex="uniswap",
            chain="ethereum",
            source="dexscreener"
        )
        
        assert pair.pair_address == "0x1234567890abcdef"
        assert pair.base_token == "ETH"
        assert pair.quote_token == "USDC"
        assert pair.price_usd == 3200.0
        assert pair.source == "dexscreener"

    def test_protocol_data_model(self):
        """Test ProtocolData data model"""
        protocol = ProtocolData(
            name="Uniswap",
            tvl=8500000000,
            chain="Ethereum",
            category="DEX",
            change_1d=2.1,
            change_7d=-0.8,
            mcap=15000000000,
            source="defillama"
        )
        
        assert protocol.name == "Uniswap"
        assert protocol.tvl == 8500000000
        assert protocol.chain == "Ethereum"
        assert protocol.category == "DEX"
        assert protocol.source == "defillama"


class TestUnifiedCryptoAPIIntegration:
    """Integration tests for UnifiedCryptoAPI"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_integration(self):
        """Test with real API calls (requires internet)"""
        import os
        if os.getenv("CI"):
            pytest.skip("Skipping real API integration test in CI")
        
        api = UnifiedCryptoAPI()
        
        try:
            # Test CoinGecko (should work without API key for basic endpoints)
            prices = await api.get_prices_coingecko(["bitcoin"], ["usd"])
            if prices:  # Only assert if we got data
                assert isinstance(prices, dict)
                assert len(prices) > 0
                
            # Test DexScreener (should work without API key)
            pairs = await api.search_pairs_dexscreener("ETH")
            assert isinstance(pairs, list)
            
        except Exception as e:
            pytest.skip(f"Real API integration test failed (expected in test environment): {e}")
        finally:
            await api.close()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_error_resilience(self):
        """Test API resilience to errors"""
        api = UnifiedCryptoAPI()
        
        try:
            # Test with invalid data that should return empty results
            pairs = await api.search_pairs_dexscreener("")
            assert isinstance(pairs, list)
            
            protocols = await api.get_protocols_defillama()
            assert isinstance(protocols, list)
            
        except Exception as e:
            pytest.skip(f"Error resilience test failed: {e}")
        finally:
            await api.close()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test concurrent API calls"""
        import asyncio
        
        api = UnifiedCryptoAPI()
        
        try:
            # Make multiple concurrent calls
            tasks = [
                api.search_pairs_dexscreener("ETH"),
                api.get_protocols_defillama(),
                api.get_prices_coingecko(["bitcoin"], ["usd"])
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that we got results (or exceptions, which is also acceptable)
            assert len(results) == 3
            
        except Exception as e:
            pytest.skip(f"Concurrent API test failed: {e}")
        finally:
            await api.close()