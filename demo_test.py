#!/usr/bin/env python3
"""
Demo script to test Salt Wallet Backend functionality

This script demonstrates how to test the complete backend system
including API endpoints, AI agents, and external integrations.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
import httpx

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class BackendDemo:
    """Demo class for testing backend functionality"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    async def test_server_health(self) -> bool:
        """Test if the server is running and healthy"""
        self.print_header("Testing Server Health")
        
        try:
            # Test main health endpoint
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.print_success("Main server health check passed")
                health_data = response.json()
                print(f"   Status: {health_data.get('status', 'unknown')}")
                return True
            else:
                self.print_error(f"Health check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Cannot connect to server: {e}")
            self.print_info("Make sure the server is running: uvicorn app.main:app --reload")
            return False

    async def test_crypto_api_endpoints(self) -> bool:
        """Test crypto data API endpoints"""
        self.print_header("Testing Crypto Data API Endpoints")
        
        success = True
        
        # Test health endpoint
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/crypto/health")
            if response.status_code == 200:
                self.print_success("Crypto API health check passed")
            else:
                self.print_error("Crypto API health check failed")
                success = False
        except Exception as e:
            self.print_error(f"Crypto API health check error: {e}")
            success = False

        # Test API status
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/crypto/status")
            if response.status_code == 200:
                self.print_success("API status endpoint working")
                status_data = response.json()
                print("   API Configuration:")
                for api_name, config in status_data.get("apis", {}).items():
                    status = "✅" if config.get("configured") else "⚠️"
                    print(f"     {status} {api_name}: {config.get('base_url', 'N/A')}")
            else:
                self.print_error("API status endpoint failed")
                success = False
        except Exception as e:
            self.print_error(f"API status error: {e}")
            success = False

        # Test search functionality
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/crypto/search",
                params={"query": "bitcoin"}
            )
            if response.status_code == 200:
                self.print_success("Token search endpoint working")
                search_data = response.json()
                total_results = search_data.get("total_results", {})
                print(f"   Search results for 'bitcoin':")
                print(f"     DexScreener: {total_results.get('dexscreener', 0)} pairs")
                print(f"     GeckoTerminal: {total_results.get('geckoterminal', 0)} pairs")
            else:
                self.print_error("Token search endpoint failed")
                success = False
        except Exception as e:
            self.print_error(f"Search endpoint error: {e}")
            success = False

        return success

    async def test_ai_agents(self) -> bool:
        """Test AI agent endpoints"""
        self.print_header("Testing AI Agent Endpoints")
        
        success = True
        
        # Test agent list
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents")
            if response.status_code == 200:
                self.print_success("Agent list endpoint working")
                agents = response.json()
                print("   Available agents:")
                for agent in agents.get("agents", []):
                    print(f"     • {agent.get('name', 'Unknown')}: {agent.get('description', 'No description')}")
            else:
                self.print_error("Agent list endpoint failed")
                success = False
        except Exception as e:
            self.print_error(f"Agent list error: {e}")
            success = False

        # Test agent chat (simple query)
        try:
            chat_data = {
                "message": "Hello, what can you help me with?",
                "user_id": "demo_user"
            }
            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/crypto_advisor/chat",
                json=chat_data
            )
            if response.status_code == 200:
                self.print_success("Crypto Advisor chat working")
                chat_response = response.json()
                message_content = chat_response.get("message", {}).get("content", "")
                print(f"   Response preview: {message_content[:100]}...")
            else:
                self.print_error("Crypto Advisor chat failed")
                success = False
        except Exception as e:
            self.print_error(f"Agent chat error: {e}")
            success = False

        return success

    async def test_market_data_integration(self) -> bool:
        """Test market data integration"""
        self.print_header("Testing Market Data Integration")
        
        success = True
        
        # Test market overview
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/crypto/market/overview")
            if response.status_code == 200:
                self.print_success("Market overview endpoint working")
                overview = response.json()
                print(f"   Trending pairs: {len(overview.get('trending_pairs', []))}")
                print(f"   Top protocols: {len(overview.get('top_protocols', []))}")
                print(f"   Market summary coins: {len(overview.get('market_summary', {}))}")
            else:
                self.print_error("Market overview endpoint failed")
                success = False
        except Exception as e:
            self.print_error(f"Market overview error: {e}")
            success = False

        # Test DexScreener integration
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/crypto/pairs/dexscreener",
                params={"query": "ETH"}
            )
            if response.status_code == 200:
                self.print_success("DexScreener integration working")
                pairs_data = response.json()
                print(f"   Found {pairs_data.get('count', 0)} ETH pairs")
            else:
                self.print_error("DexScreener integration failed")
                success = False
        except Exception as e:
            self.print_error(f"DexScreener integration error: {e}")
            success = False

        return success

    async def test_performance(self) -> bool:
        """Test API performance"""
        self.print_header("Testing API Performance")
        
        success = True
        
        # Test response time
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/crypto/health")
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                if response_time < 1000:  # Less than 1 second
                    self.print_success(f"API response time: {response_time:.2f}ms")
                else:
                    self.print_error(f"API response time too slow: {response_time:.2f}ms")
                    success = False
            else:
                self.print_error("Performance test failed - API not responding")
                success = False
                
        except Exception as e:
            self.print_error(f"Performance test error: {e}")
            success = False

        # Test concurrent requests
        try:
            tasks = []
            for _ in range(5):
                task = self.client.get(f"{self.base_url}/api/v1/crypto/health")
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_responses = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            total_time = (end_time - start_time) * 1000
            
            if successful_responses == 5:
                self.print_success(f"Concurrent requests: 5/5 successful in {total_time:.2f}ms")
            else:
                self.print_error(f"Concurrent requests: {successful_responses}/5 successful")
                success = False
                
        except Exception as e:
            self.print_error(f"Concurrent test error: {e}")
            success = False

        return success

    async def run_complete_test(self):
        """Run complete backend test suite"""
        self.print_header("Salt Wallet Backend Demo & Test Suite")
        
        print("🚀 Starting comprehensive backend testing...")
        print("This will test all major components of the Salt Wallet backend.")
        
        test_results = []
        
        # Run all tests
        test_results.append(("Server Health", await self.test_server_health()))
        test_results.append(("Crypto API Endpoints", await self.test_crypto_api_endpoints()))
        test_results.append(("AI Agents", await self.test_ai_agents()))
        test_results.append(("Market Data Integration", await self.test_market_data_integration()))
        test_results.append(("Performance", await self.test_performance()))
        
        # Print summary
        self.print_header("Test Results Summary")
        
        all_passed = True
        for test_name, result in test_results:
            if result:
                self.print_success(f"{test_name}: PASSED")
            else:
                self.print_error(f"{test_name}: FAILED")
                all_passed = False
        
        print(f"\n{'='*60}")
        if all_passed:
            print("🎉 ALL TESTS PASSED! Your backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        print(f"{'='*60}")
        
        return all_passed


async def main():
    """Main function"""
    demo = BackendDemo()
    
    try:
        success = await demo.run_complete_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        return 1
    finally:
        await demo.close()


if __name__ == "__main__":
    print("Salt Wallet Backend Demo")
    print("="*40)
    print("Make sure your backend server is running:")
    print("  cd salt_backend")
    print("  uvicorn app.main:app --reload")
    print("="*40)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)