# Unified Crypto API Integration

This document describes the comprehensive integration of multiple cryptocurrency data APIs in the Salt Wallet backend.

## Integrated APIs

### 1. DexScreener API
**Documentation**: https://docs.dexscreener.com/api/reference

**Purpose**: DEX trading data and pair analytics
**Base URL**: `https://api.dexscreener.com/latest`
**API Key Required**: No (for basic endpoints)

**Key Features**:
- Search trading pairs by token name/symbol/address
- Get specific pair data by contract address
- Token-based pair listings
- Real-time DEX trading metrics

**Implemented Endpoints**:
- `GET /api/v1/crypto/pairs/dexscreener?query={search_term}`
- `GET /api/v1/crypto/pairs/dexscreener/{pair_address}`

### 2. DefiLlama API
**Documentation**: https://defillama.com/docs/api

**Purpose**: DeFi protocol TVL (Total Value Locked) data
**Base URL**: `https://api.llama.fi`
**API Key Required**: No

**Key Features**:
- Protocol TVL tracking
- Chain-level TVL aggregation
- Historical TVL data
- Protocol categorization

**Implemented Endpoints**:
- `GET /api/v1/crypto/protocols/defillama`
- `GET /api/v1/crypto/protocols/defillama/{protocol_slug}`
- `GET /api/v1/crypto/chains/defillama/{chain}`

### 3. GeckoTerminal API
**Documentation**: https://www.geckoterminal.com/dex-api

**Purpose**: Advanced DEX analytics and trending data
**Base URL**: `https://api.geckoterminal.com/api/v2`
**API Key Required**: Optional (for higher rate limits)

**Key Features**:
- Trending pools across networks
- Pool search functionality
- Advanced trading analytics
- Multi-network support

**Implemented Endpoints**:
- `GET /api/v1/crypto/pools/geckoterminal/trending?network={network}`
- `GET /api/v1/crypto/pools/geckoterminal/search?query={search}&network={network}`

### 4. CoinGecko API
**Documentation**: https://www.coingecko.com/en/api/documentation

**Purpose**: General cryptocurrency market data
**Base URL**: `https://api.coingecko.com/api/v3`
**API Key Required**: Optional (for higher rate limits)

**Key Features**:
- Token price data
- Market capitalization
- 24h volume and price changes
- Global market statistics

**Implemented Endpoints**:
- `GET /api/v1/crypto/prices/coingecko?coin_ids={ids}&vs_currencies={currencies}`

## Unified Service Architecture

### UnifiedCryptoAPI Class
Location: `app/services/unified_crypto_api.py`

**Purpose**: Centralized service that provides a unified interface to all crypto data APIs.

**Key Methods**:
```python
# DexScreener methods
async def search_pairs_dexscreener(query: str) -> List[TradingPair]
async def get_pair_dexscreener(pair_address: str) -> Optional[TradingPair]

# DefiLlama methods  
async def get_protocols_defillama() -> List[ProtocolData]
async def get_protocol_tvl_defillama(protocol_slug: str) -> Optional[ProtocolData]
async def get_chain_tvl_defillama(chain: str) -> Dict[str, Any]

# GeckoTerminal methods
async def get_trending_pools_geckoterminal(network: str) -> List[TradingPair]
async def search_pools_geckoterminal(query: str, network: str) -> List[TradingPair]

# CoinGecko methods
async def get_prices_coingecko(coin_ids: List[str], vs_currencies: List[str]) -> Dict[str, TokenPrice]

# Unified methods
async def search_tokens_unified(query: str) -> Dict[str, List[Union[TradingPair, TokenPrice]]]
async def get_market_overview() -> Dict[str, Any]
```

### Data Models

**TokenPrice**:
```python
@dataclass
class TokenPrice:
    symbol: str
    price_usd: float
    price_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
```

**TradingPair**:
```python
@dataclass
class TradingPair:
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
```

**ProtocolData**:
```python
@dataclass
class ProtocolData:
    name: str
    tvl: float
    chain: str
    category: Optional[str] = None
    change_1d: Optional[float] = None
    change_7d: Optional[float] = None
    mcap: Optional[float] = None
    source: Optional[str] = None
```

## API Routes

### Base Path: `/api/v1/crypto`

#### Unified Search
- `GET /search?query={search_term}` - Search across all data sources

#### DexScreener Endpoints
- `GET /pairs/dexscreener?query={search_term}` - Search DexScreener pairs
- `GET /pairs/dexscreener/{pair_address}` - Get specific pair data

#### GeckoTerminal Endpoints
- `GET /pools/geckoterminal/trending?network={network}` - Get trending pools
- `GET /pools/geckoterminal/search?query={search}&network={network}` - Search pools

#### DefiLlama Endpoints
- `GET /protocols/defillama?limit={limit}` - Get DeFi protocols
- `GET /protocols/defillama/{protocol_slug}` - Get specific protocol
- `GET /chains/defillama/{chain}` - Get chain TVL data

#### CoinGecko Endpoints
- `GET /prices/coingecko?coin_ids={ids}&vs_currencies={currencies}` - Get token prices

#### Utility Endpoints
- `GET /market/overview` - Comprehensive market overview
- `GET /status` - API status and configuration
- `GET /health` - Health check

## Environment Configuration

### Required Environment Variables
```bash
# API Keys (Optional for most APIs)
COINGECKO_API_KEY=your-coingecko-api-key
DEXSCREENER_API_KEY=your-dexscreener-api-key  # Usually not required
DEFILLAMA_API_KEY=your-defillama-api-key      # Usually not required
GECKOTERMINAL_API_KEY=your-geckoterminal-api-key

# API Base URLs (Optional - defaults provided)
COINGECKO_API_URL=https://api.coingecko.com/api/v3
DEXSCREENER_API_URL=https://api.dexscreener.com/latest
DEFILLAMA_API_URL=https://api.llama.fi
GECKOTERMINAL_API_URL=https://api.geckoterminal.com/api/v2
```

## AI Agent Integration

### Crypto Advisor Agent Enhancement
The Crypto Advisor Agent now uses the unified API service for real-time market data:

**Key Features**:
- Automatic context enrichment with current prices
- Multi-source data aggregation
- Intelligent keyword detection for relevant data fetching
- Formatted market summaries in responses

**Usage in Agent**:
```python
# The agent automatically detects crypto-related queries and enriches responses
user_query = "What's the current price of Bitcoin?"
# Agent fetches real-time BTC price and includes it in the response context
```

## Rate Limiting & Error Handling

### Rate Limiting
- Each API has its own rate limits
- API keys generally provide higher rate limits
- Service implements proper error handling for rate limit exceeded scenarios

### Error Handling
- Graceful degradation when APIs are unavailable
- Comprehensive logging for debugging
- Fallback responses when data is unavailable
- Timeout handling for API requests

## Usage Examples

### Search for a Token Across All Sources
```bash
curl "http://localhost:8000/api/v1/crypto/search?query=ethereum"
```

### Get Trending Pools from GeckoTerminal
```bash
curl "http://localhost:8000/api/v1/crypto/pools/geckoterminal/trending?network=eth"
```

### Get Bitcoin Price from CoinGecko
```bash
curl "http://localhost:8000/api/v1/crypto/prices/coingecko?coin_ids=bitcoin&vs_currencies=usd"
```

### Get Market Overview
```bash
curl "http://localhost:8000/api/v1/crypto/market/overview"
```

### Check API Status
```bash
curl "http://localhost:8000/api/v1/crypto/status"
```

## Future Enhancements

1. **Caching Layer**: Implement Redis caching for frequently requested data
2. **WebSocket Streams**: Real-time price feeds for live updates
3. **Historical Data**: Extended historical price and volume data
4. **Advanced Analytics**: Technical indicators and trading signals
5. **Portfolio Tracking**: Integration with user portfolio management
6. **Price Alerts**: Notification system for price movements
7. **API Rate Limiting**: Internal rate limiting to prevent abuse
8. **Data Validation**: Enhanced data validation and sanitization

## Development Notes

- All API clients use `httpx.AsyncClient` for async operations
- Services are designed to be easily testable with mocking
- Environment variables provide flexibility for different deployment environments
- Error handling ensures the system remains stable even when external APIs fail
- The unified service pattern allows for easy addition of new data sources