"""
Test cases for Crypto Data API endpoints
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

# Import the main app
from app.main import app
from app.services.unified_crypto_api import UnifiedCryptoAPI, TokenPrice, TradingPair, ProtocolData


class TestCryptoDataAPI:
    """Test suite for crypto data API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_unified_api(self):
        """Mock unified crypto API"""
        mock_api = AsyncMock(spec=UnifiedCryptoAPI)
        return mock_api

    @pytest.fixture
    def sample_token_price(self):
        """Sample token price data"""
        return TokenPrice(
            symbol="bitcoin",
            price_usd=45000.0,
            price_change_24h=2.5,
            market_cap=850000000000,
            volume_24h=25000000000,
            source="coingecko"
        )

    @pytest.fixture
    def sample_trading_pair(self):
        """Sample trading pair data"""
        return TradingPair(
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

    @pytest.fixture
    def sample_protocol_data(self):
        """Sample protocol data"""
        return ProtocolData(
            name="Uniswap",
            tvl=8500000000,
            chain="Ethereum",
            category="DEX",
            change_1d=2.1,
            change_7d=-0.8,
            source="defillama"
        )

    @pytest.mark.api
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/crypto/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "crypto_data_api"
        assert "apis" in data

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_search_tokens_success(self, mock_get_api, client, mock_unified_api, sample_trading_pair):
        """Test successful token search"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.search_tokens_unified.return_value = {
            "dexscreener_pairs": [sample_trading_pair],
            "geckoterminal_pairs": [],
            "coingecko_prices": []
        }

        response = client.get("/api/v1/crypto/search?query=ethereum")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "ethereum"
        assert "results" in data
        assert "total_results" in data
        assert data["total_results"]["dexscreener"] == 1

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_search_dexscreener_pairs(self, mock_get_api, client, mock_unified_api, sample_trading_pair):
        """Test DexScreener pair search"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.search_pairs_dexscreener.return_value = [sample_trading_pair]

        response = client.get("/api/v1/crypto/pairs/dexscreener?query=ETH")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "ETH"
        assert data["source"] == "dexscreener"
        assert data["count"] == 1
        assert len(data["pairs"]) == 1

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_dexscreener_pair_success(self, mock_get_api, client, mock_unified_api, sample_trading_pair):
        """Test getting specific DexScreener pair"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_pair_dexscreener.return_value = sample_trading_pair

        response = client.get("/api/v1/crypto/pairs/dexscreener/0x1234567890abcdef")
        assert response.status_code == 200
        data = response.json()
        assert data["pair_address"] == "0x1234567890abcdef"
        assert data["source"] == "dexscreener"
        assert "pair" in data

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_dexscreener_pair_not_found(self, mock_get_api, client, mock_unified_api):
        """Test getting non-existent DexScreener pair"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_pair_dexscreener.return_value = None

        response = client.get("/api/v1/crypto/pairs/dexscreener/0xinvalidaddress")
        assert response.status_code == 404
        data = response.json()
        assert "Trading pair not found" in data["detail"]

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_geckoterminal_trending(self, mock_get_api, client, mock_unified_api, sample_trading_pair):
        """Test GeckoTerminal trending pools"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_trending_pools_geckoterminal.return_value = [sample_trading_pair]

        response = client.get("/api/v1/crypto/pools/geckoterminal/trending?network=eth")
        assert response.status_code == 200
        data = response.json()
        assert data["network"] == "eth"
        assert data["source"] == "geckoterminal"
        assert data["count"] == 1

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_search_geckoterminal_pools(self, mock_get_api, client, mock_unified_api, sample_trading_pair):
        """Test GeckoTerminal pool search"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.search_pools_geckoterminal.return_value = [sample_trading_pair]

        response = client.get("/api/v1/crypto/pools/geckoterminal/search?query=ETH&network=eth")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "ETH"
        assert data["network"] == "eth"
        assert data["source"] == "geckoterminal"

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_defillama_protocols(self, mock_get_api, client, mock_unified_api, sample_protocol_data):
        """Test DefiLlama protocols endpoint"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_protocols_defillama.return_value = [sample_protocol_data]

        response = client.get("/api/v1/crypto/protocols/defillama?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "defillama"
        assert data["count"] == 1
        assert len(data["protocols"]) == 1

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_defillama_protocol_success(self, mock_get_api, client, mock_unified_api, sample_protocol_data):
        """Test getting specific DefiLlama protocol"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_protocol_tvl_defillama.return_value = sample_protocol_data

        response = client.get("/api/v1/crypto/protocols/defillama/uniswap")
        assert response.status_code == 200
        data = response.json()
        assert data["protocol_slug"] == "uniswap"
        assert data["source"] == "defillama"

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_defillama_protocol_not_found(self, mock_get_api, client, mock_unified_api):
        """Test getting non-existent DefiLlama protocol"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_protocol_tvl_defillama.return_value = None

        response = client.get("/api/v1/crypto/protocols/defillama/nonexistent")
        assert response.status_code == 404

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_defillama_chain_tvl_success(self, mock_get_api, client, mock_unified_api):
        """Test getting DefiLlama chain TVL"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_chain_tvl_defillama.return_value = {
            "chain": "ethereum",
            "tvl": 50000000000,
            "change_1d": 1.5,
            "source": "defillama"
        }

        response = client.get("/api/v1/crypto/chains/defillama/ethereum")
        assert response.status_code == 200
        data = response.json()
        assert data["chain"] == "ethereum"
        assert data["source"] == "defillama"

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_coingecko_prices(self, mock_get_api, client, mock_unified_api, sample_token_price):
        """Test CoinGecko prices endpoint"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_prices_coingecko.return_value = {
            "bitcoin_usd": sample_token_price
        }

        response = client.get("/api/v1/crypto/prices/coingecko?coin_ids=bitcoin&vs_currencies=usd")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "coingecko"
        assert "bitcoin" in data["coin_ids"]
        assert "usd" in data["vs_currencies"]

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_market_overview(self, mock_get_api, client, mock_unified_api, sample_trading_pair, sample_protocol_data, sample_token_price):
        """Test market overview endpoint"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_market_overview.return_value = {
            "trending_pairs": [sample_trading_pair],
            "top_protocols": [sample_protocol_data],
            "market_summary": {"bitcoin_usd": sample_token_price}
        }

        response = client.get("/api/v1/crypto/market/overview")
        assert response.status_code == 200
        data = response.json()
        assert "trending_pairs" in data
        assert "top_protocols" in data
        assert "market_summary" in data
        assert "sources" in data

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_get_api_status(self, mock_get_api, client, mock_unified_api):
        """Test API status endpoint"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.get_api_status.return_value = {
            "dexscreener": {"configured": True, "base_url": "https://api.dexscreener.com/latest"},
            "defillama": {"configured": True, "base_url": "https://api.llama.fi"},
            "geckoterminal": {"configured": False, "base_url": "https://api.geckoterminal.com/api/v2"},
            "coingecko": {"configured": True, "base_url": "https://api.coingecko.com/api/v3"}
        }

        response = client.get("/api/v1/crypto/status")
        assert response.status_code == 200
        data = response.json()
        assert "apis" in data
        assert "timestamp" in data

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_api_error_handling(self, mock_get_api, client, mock_unified_api):
        """Test API error handling"""
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.search_tokens_unified.side_effect = Exception("API Error")

        response = client.get("/api/v1/crypto/search?query=test")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to search tokens" in data["detail"]

    @pytest.mark.api
    def test_missing_query_parameter(self, client):
        """Test missing required query parameter"""
        response = client.get("/api/v1/crypto/search")
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    def test_missing_coin_ids_parameter(self, client):
        """Test missing required coin_ids parameter"""
        response = client.get("/api/v1/crypto/prices/coingecko?vs_currencies=usd")
        assert response.status_code == 422  # Validation error


class TestCryptoDataAPIIntegration:
    """Integration tests for crypto data API"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_unified_api_integration(self):
        """Test unified API integration"""
        from app.services.unified_crypto_api import UnifiedCryptoAPI
        
        api = UnifiedCryptoAPI()
        
        # Test that the API instance is created properly
        assert api is not None
        assert hasattr(api, 'session')
        assert hasattr(api, 'apis')
        
        # Test API status method
        status = api.get_api_status()
        assert isinstance(status, dict)
        assert len(status) == 4  # Should have 4 APIs configured
        
        await api.close()

    @pytest.mark.integration 
    @pytest.mark.asyncio
    async def test_real_api_calls(self):
        """Test real API calls (requires internet connection)"""
        from app.services.unified_crypto_api import UnifiedCryptoAPI
        
        # Skip if in CI/CD or if API keys are not available
        import os
        if os.getenv("CI") or not os.getenv("COINGECKO_API_KEY"):
            pytest.skip("Skipping real API test in CI or without API keys")
        
        api = UnifiedCryptoAPI()
        
        try:
            # Test CoinGecko prices (should work without API key)
            prices = await api.get_prices_coingecko(["bitcoin"], ["usd"])
            assert isinstance(prices, dict)
            
            # Test DexScreener search (should work without API key)
            pairs = await api.search_pairs_dexscreener("ETH")
            assert isinstance(pairs, list)
            
        except Exception as e:
            pytest.skip(f"API call failed (expected in test environment): {e}")
        finally:
            await api.close()


# Performance tests
class TestCryptoDataAPIPerformance:
    """Performance tests for crypto data API"""

    @pytest.mark.api
    @patch("app.api.crypto_data.get_unified_api")
    def test_concurrent_requests(self, mock_get_api, client, mock_unified_api):
        """Test handling concurrent requests"""
        import threading
        import time
        
        mock_get_api.return_value = mock_unified_api
        mock_unified_api.search_tokens_unified.return_value = {
            "dexscreener_pairs": [],
            "geckoterminal_pairs": [],
            "coingecko_prices": []
        }
        
        def make_request():
            response = client.get("/api/v1/crypto/search?query=test")
            return response.status_code
        
        # Make 5 concurrent requests
        threads = []
        results = []
        
        start_time = time.time()
        for _ in range(5):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Check that all requests succeeded
        assert all(status == 200 for status in results)
        assert len(results) == 5
        
        # Check that requests completed in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0