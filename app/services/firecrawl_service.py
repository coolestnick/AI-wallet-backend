from typing import List, Dict, Optional, Any
import os
import logging
from firecrawl import FirecrawlApp
from urllib.parse import urljoin, urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class FirecrawlService:
    """Service for web scraping and crawling using Firecrawl API"""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.app = None
        else:
            self.app = FirecrawlApp(api_key=self.api_key)
        
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    async def scrape_url(self, url: str, formats: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Scrape a single URL and return the content
        
        Args:
            url: The URL to scrape
            formats: List of output formats ['markdown', 'html', 'structured', 'screenshot']
            **kwargs: Additional scraping options
            
        Returns:
            Dictionary containing scraped content
        """
        if not self.app:
            raise ValueError("Firecrawl API key not configured")
        
        if formats is None:
            formats = ['markdown']
        
        try:
            # Run the synchronous scraping operation in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: self.app.scrape_url(url, formats=formats, **kwargs)
            )
            
            logger.info(f"Successfully scraped URL: {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise
    
    async def scrape_multiple_urls(self, urls: List[str], formats: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently
        
        Args:
            urls: List of URLs to scrape
            formats: List of output formats
            **kwargs: Additional scraping options
            
        Returns:
            List of dictionaries containing scraped content
        """
        if not self.app:
            raise ValueError("Firecrawl API key not configured")
        
        if formats is None:
            formats = ['markdown']
        
        tasks = []
        for url in urls:
            task = self.scrape_url(url, formats=formats, **kwargs)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to scrape URL {urls[i]}: {str(result)}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def crawl_website(self, url: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Crawl an entire website starting from a URL
        
        Args:
            url: Starting URL for crawling
            limit: Maximum number of pages to crawl
            **kwargs: Additional crawling options
            
        Returns:
            Dictionary containing crawled content
        """
        if not self.app:
            raise ValueError("Firecrawl API key not configured")
        
        try:
            # Run the synchronous crawling operation in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: self.app.crawl_url(url, limit=limit, **kwargs)
            )
            
            logger.info(f"Successfully crawled website: {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error crawling website {url}: {str(e)}")
            raise
    
    async def search_crypto_news(self, query: str, sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for cryptocurrency news and articles
        
        Args:
            query: Search query
            sources: List of source URLs to search
            
        Returns:
            List of scraped news articles
        """
        if sources is None:
            # Default crypto news sources
            sources = [
                "https://coindesk.com",
                "https://cointelegraph.com",
                "https://decrypt.co",
                "https://theblock.co",
                "https://cryptoslate.com"
            ]
        
        # For now, we'll scrape the homepages of these sources
        # In a more advanced implementation, we could use their search APIs
        results = []
        
        for source in sources:
            try:
                scraped_content = await self.scrape_url(
                    source,
                    formats=['markdown'],
                    actions=[
                        {
                            "type": "wait",
                            "milliseconds": 2000
                        }
                    ]
                )
                
                if scraped_content and 'markdown' in scraped_content:
                    # Filter content based on query
                    content = scraped_content['markdown']
                    if query.lower() in content.lower():
                        results.append({
                            'source': source,
                            'content': content,
                            'url': source,
                            'title': scraped_content.get('title', 'Unknown'),
                            'query_match': True
                        })
                
            except Exception as e:
                logger.error(f"Error scraping {source}: {str(e)}")
                continue
        
        return results
    
    async def scrape_defi_data(self, protocols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape DeFi protocol data from various sources
        
        Args:
            protocols: List of specific protocols to scrape
            
        Returns:
            List of scraped DeFi data
        """
        defi_sources = [
            "https://defillama.com",
            "https://dexscreener.com",
            "https://coingecko.com/en/defi",
            "https://coinmarketcap.com/defi/",
        ]
        
        results = []
        
        for source in defi_sources:
            try:
                scraped_content = await self.scrape_url(
                    source,
                    formats=['markdown', 'structured'],
                    actions=[
                        {
                            "type": "wait",
                            "milliseconds": 3000
                        }
                    ]
                )
                
                if scraped_content:
                    results.append({
                        'source': source,
                        'data': scraped_content,
                        'timestamp': scraped_content.get('timestamp')
                    })
                
            except Exception as e:
                logger.error(f"Error scraping DeFi data from {source}: {str(e)}")
                continue
        
        return results
    
    async def scrape_social_sentiment(self, tokens: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape social media sentiment for crypto tokens
        
        Args:
            tokens: List of token symbols to track
            
        Returns:
            List of social sentiment data
        """
        # Note: This is a basic implementation
        # In production, you'd want to use proper social media APIs
        social_sources = [
            "https://cryptopanic.com",
            "https://santiment.net",
            "https://lunarcrush.com"
        ]
        
        results = []
        
        for source in social_sources:
            try:
                scraped_content = await self.scrape_url(
                    source,
                    formats=['markdown'],
                    actions=[
                        {
                            "type": "wait",
                            "milliseconds": 2000
                        }
                    ]
                )
                
                if scraped_content and 'markdown' in scraped_content:
                    # Basic sentiment analysis based on content
                    content = scraped_content['markdown']
                    
                    # If specific tokens are provided, filter for them
                    if tokens:
                        token_matches = []
                        for token in tokens:
                            if token.upper() in content.upper():
                                token_matches.append(token)
                        
                        if token_matches:
                            results.append({
                                'source': source,
                                'content': content,
                                'tokens_mentioned': token_matches,
                                'title': scraped_content.get('title', 'Unknown')
                            })
                    else:
                        results.append({
                            'source': source,
                            'content': content,
                            'title': scraped_content.get('title', 'Unknown')
                        })
                
            except Exception as e:
                logger.error(f"Error scraping social sentiment from {source}: {str(e)}")
                continue
        
        return results
    
    def is_configured(self) -> bool:
        """Check if Firecrawl service is properly configured"""
        return self.app is not None
    
    def __del__(self):
        """Clean up thread pool executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


# Global instance
firecrawl_service = FirecrawlService()