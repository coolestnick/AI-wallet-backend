# AI Wallet Backend

A comprehensive crypto market research platform with AI-powered agents and real-time web scraping capabilities.

## 🚀 Features

### 🤖 AI Agents
- **Crypto Advisor Agent**: Expert cryptocurrency investment guidance
- **Market Research Agent**: Traditional crypto market analysis  
- **Portfolio Management Agent**: Portfolio optimization strategies
- **Firecrawl Research Agent**: Real-time web scraping & market research (NEW\!)

### 🔍 Research Capabilities
- **Real-time News Scraping**: Latest crypto news from major sources
- **DeFi Protocol Analysis**: TVL tracking, yield farming insights
- **Social Sentiment Analysis**: Community sentiment tracking
- **Multi-source Data Aggregation**: Comprehensive market intelligence

### 🎨 Modern UI
- **Agno UI Integration**: Clean, responsive chat interface
- **Streaming Responses**: Real-time AI agent interactions
- **Progress Indicators**: Live research status updates
- **Multi-modal Support**: Text, images, and rich content

## 📁 Project Structure

```
AI-wallet-backend/
├── agents/                     # AI agent implementations
│   ├── crypto_advisor.py      # Crypto investment advisor
│   ├── market_research.py     # Market analysis agent
│   ├── portfolio_management.py # Portfolio optimization
│   ├── firecrawl_research.py  # Web scraping research agent
│   └── selector.py            # Agent selection logic
├── api/                       # FastAPI routes and models
├── app/                       # Core application logic
│   ├── services/              # Business logic services
│   │   ├── firecrawl_service.py # Web scraping service
│   │   └── unified_crypto_api.py # Crypto data aggregation
│   └── main.py               # FastAPI application
├── agno_ui/                  # Modern chat interface
│   └── crypto-research-ui/   # Next.js frontend
├── config/                   # Configuration files
├── docs/                     # Documentation
├── tests/                    # Test suites
└── requirements.txt          # Python dependencies
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- pnpm (for frontend)

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/coolestnick/AI-wallet-backend.git
   cd AI-wallet-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --port 7777
   ```

### Frontend Setup (Agno UI)

1. **Navigate to frontend directory**:
   ```bash
   cd agno_ui/crypto-research-ui
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Start development server**:
   ```bash
   pnpm dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:7777

## 🔑 Required API Keys

Add these to your `.env` file:

```env
# AI Services
GEMINI_API_KEY=your_gemini_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Database
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET=your_secure_jwt_secret

# Optional: Additional crypto APIs
COINGECKO_API_KEY=your_coingecko_key
DEXSCREENER_API_KEY=your_dexscreener_key
```

## 🎯 Usage Examples

### Basic Market Research
```
"What's the latest Bitcoin news?"
"Analyze Solana sentiment trends"
"What are the current DeFi protocols with highest TVL?"
```

### Advanced Research Queries
```
"Research Layer 2 scaling solutions and their adoption rates"
"Compare social sentiment between Ethereum and Solana ecosystems"
"Analyze the correlation between news sentiment and price movements for top 10 tokens"
```

## 🧪 Testing

Run the test suite:
```bash
pytest
pytest --cov=.  # With coverage
```

Test specific components:
```bash
pytest tests/test_firecrawl_research.py  # Test research agent
pytest tests/test_crypto_data_api.py     # Test API endpoints
```

## 📊 API Endpoints

### Agent Management
- `GET /api/v1/agents` - List available agents
- `POST /api/v1/agents/{agent_id}/chat` - Chat with agent
- `POST /api/v1/agents/{agent_id}/chat/stream` - Streaming chat

### Health & Status
- `GET /health` - Service health check
- `GET /` - API welcome message

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙋‍♂️ Support

For questions and support:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [API integration guide](docs/AGNO_UI_INTEGRATION.md)
EOF < /dev/null