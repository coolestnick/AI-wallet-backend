# Agno UI Integration Guide

This guide explains how to integrate the Firecrawl Research Agent with Agno UI for enhanced crypto market research capabilities.

## Overview

The Firecrawl Research Agent (`firecrawl_research`) has been integrated into the Salt Wallet backend and can be used with Agno UI for a modern chat interface with real-time streaming capabilities.

## Features

- **Real-time Web Scraping**: Uses Firecrawl API to gather current market data
- **Multi-source Research**: Aggregates data from news, DeFi protocols, and social sentiment
- **Streaming Responses**: Provides real-time updates during research process
- **Modern UI**: Clean, responsive interface via Agno UI

## Setup Instructions

### 1. Backend Setup

1. **Install dependencies**:
   ```bash
   cd salt_backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Add your API keys to `.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   ```

3. **Start the backend server**:
   ```bash
   uvicorn main:app --reload --port 7777
   ```

### 2. Agno UI Setup

1. **Install Agno UI**:
   ```bash
   npx create-agent-ui@latest crypto-research-ui
   cd crypto-research-ui
   ```

2. **Configure backend endpoint**:
   Edit the configuration to point to your backend:
   ```
   Backend URL: http://localhost:7777
   ```

3. **Start Agno UI**:
   ```bash
   pnpm dev
   ```

## Agent Configuration

The Firecrawl Research Agent is available with the following details:

- **Agent ID**: `firecrawl_research` or `firecrawl-research`
- **Name**: "Firecrawl Research Agent"
- **Description**: "Advanced crypto market research using real-time web scraping and AI analysis"

## API Endpoints

### List Available Agents
```
GET /api/v1/agents
```

### Chat with Firecrawl Research Agent
```
POST /api/v1/agents/firecrawl-research/chat
```

### Stream Chat with Firecrawl Research Agent
```
POST /api/v1/agents/firecrawl-research/chat/stream
```

## Usage Examples

### 1. Basic Market Research Query
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the latest news on Bitcoin and Ethereum?"
    }
  ],
  "session_id": "research-session-1",
  "user_id": "user-123"
}
```

### 2. DeFi Protocol Analysis
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze the current DeFi landscape and TVL trends"
    }
  ],
  "session_id": "defi-analysis-1",
  "user_id": "user-123"
}
```

### 3. Social Sentiment Analysis
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the social sentiment around SOL and ADA tokens?"
    }
  ],
  "session_id": "sentiment-analysis-1",
  "user_id": "user-123"
}
```

## Research Capabilities

The agent can perform the following types of research:

### 1. **News Aggregation**
- Scrapes major crypto news sources
- Filters content based on user queries
- Provides sourced information with links

### 2. **DeFi Protocol Analysis**
- Gathers data from DeFiLlama, DexScreener
- Analyzes TVL, yield farming opportunities
- Tracks protocol performance metrics

### 3. **Social Sentiment Tracking**
- Monitors social media mentions
- Analyzes sentiment for specific tokens
- Provides community insights

## Response Format

The agent provides structured responses with:

- **Research Status**: Real-time updates during data gathering
- **Source Attribution**: Clear citation of all data sources
- **Timestamp**: When the research was conducted
- **Categorized Data**: Organized by news, DeFi, sentiment
- **Analysis**: AI-powered insights and recommendations

## Example Streaming Response

```
🔍 Starting comprehensive market research...

✅ Research complete! Gathered 5 news sources, 3 DeFi sources, and 2 sentiment sources.

## Bitcoin Market Analysis

Based on recent data from CoinDesk and Cointelegraph:
- Current price action showing...
- Institutional sentiment remains...
- Technical indicators suggest...

*Sources: CoinDesk, Cointelegraph (scraped at 2024-01-15 14:30 UTC)*
```

## Error Handling

The agent gracefully handles various error conditions:

- **Missing API Keys**: Clear error messages when Firecrawl/Gemini keys are missing
- **Scraping Failures**: Continues research with available sources
- **Rate Limiting**: Implements delays and retry logic
- **Data Parsing**: Fallback mechanisms for malformed data

## Performance Optimization

- **Concurrent Scraping**: Multiple sources scraped in parallel
- **Content Filtering**: Relevant content extraction to reduce noise
- **Response Caching**: Implements caching for frequently requested data
- **Streaming Updates**: Real-time progress feedback to users

## Customization Options

### 1. **Custom News Sources**
Modify the `search_crypto_news` method to add custom sources:
```python
sources = [
    "https://your-custom-source.com",
    "https://another-source.com"
]
```

### 2. **Research Parameters**
Adjust research depth and scope:
```python
# Increase/decrease number of sources
news_data = await self.firecrawl_service.search_crypto_news(query, max_sources=10)
```

### 3. **Content Filtering**
Customize content relevance filtering:
```python
# Add custom keywords for filtering
if any(keyword in content.lower() for keyword in custom_keywords):
    # Include in results
```

## Troubleshooting

### Common Issues

1. **"FIRECRAWL_API_KEY not found"**
   - Ensure API key is set in `.env` file
   - Restart the backend server after adding the key

2. **"Scraping failed"**
   - Check internet connectivity
   - Verify Firecrawl API key is valid
   - Check if target websites are accessible

3. **Slow response times**
   - Reduce number of sources being scraped
   - Implement caching for frequently accessed data
   - Consider using async optimization

### Debug Mode

Enable debug logging for troubleshooting:
```python
agent = get_agent(
    agent_id="firecrawl_research",
    debug_mode=True
)
```

## Future Enhancements

Potential improvements for the research agent:

1. **Advanced Filtering**: ML-based content relevance scoring
2. **Data Persistence**: Store research results for historical analysis
3. **Custom Dashboards**: Specialized views for different research types
4. **Real-time Alerts**: Notification system for significant market events
5. **Multi-language Support**: International news sources and analysis

## Support

For issues or questions:
- Check the Salt Wallet documentation
- Review Firecrawl API documentation
- Consult Agno UI documentation
- Submit issues to the project repository