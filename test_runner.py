#!/usr/bin/env python3
"""
Comprehensive test runner for Salt Wallet Backend

This script provides different testing modes for the Salt Wallet backend:
- Unit tests only
- Integration tests
- API tests
- Agent tests
- Full test suite
- Performance tests
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestRunner:
    """Test runner for Salt Wallet backend"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        
    def print_header(self, message: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")
        
    def check_environment(self) -> bool:
        """Check if the environment is set up correctly"""
        self.print_header("Checking Environment")
        
        # Check if pytest is installed
        try:
            subprocess.run(["pytest", "--version"], capture_output=True, check=True)
            self.print_success("pytest is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("pytest is not installed. Run: pip install pytest")
            return False
            
        # Check if test directory exists
        if not self.test_dir.exists():
            self.print_error(f"Test directory not found: {self.test_dir}")
            return False
        self.print_success("Test directory found")
        
        # Check for .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            self.print_success(".env file found")
        else:
            self.print_warning(".env file not found - some integration tests may fail")
            
        # Check API keys
        api_keys = ["GEMINI_API_KEY", "COINGECKO_API_KEY", "DEXSCREENER_API_KEY"]
        missing_keys = []
        for key in api_keys:
            if os.getenv(key):
                self.print_success(f"{key} is configured")
            else:
                missing_keys.append(key)
                self.print_warning(f"{key} is not configured")
                
        if missing_keys:
            self.print_info("Missing API keys will cause some integration tests to be skipped")
            
        return True
        
    def run_pytest(self, args: List[str], description: str) -> bool:
        """Run pytest with given arguments"""
        self.print_info(f"Running: {description}")
        print(f"{Colors.OKCYAN}Command: pytest {' '.join(args)}{Colors.ENDC}")
        
        start_time = time.time()
        try:
            result = subprocess.run(["pytest"] + args, cwd=self.project_root)
            end_time = time.time()
            
            duration = end_time - start_time
            if result.returncode == 0:
                self.print_success(f"{description} completed successfully in {duration:.2f}s")
                return True
            else:
                self.print_error(f"{description} failed in {duration:.2f}s")
                return False
        except KeyboardInterrupt:
            self.print_warning("Tests interrupted by user")
            return False
        except Exception as e:
            self.print_error(f"Error running tests: {e}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests only"""
        self.print_header("Running Unit Tests")
        return self.run_pytest([
            "-v",
            "-m", "not integration",
            "--tb=short",
            "tests/"
        ], "Unit tests")
    
    def run_integration_tests(self) -> bool:
        """Run integration tests only"""
        self.print_header("Running Integration Tests")
        self.print_warning("Integration tests require API keys and internet connection")
        return self.run_pytest([
            "-v", 
            "-m", "integration",
            "--tb=short",
            "tests/"
        ], "Integration tests")
    
    def run_api_tests(self) -> bool:
        """Run API endpoint tests"""
        self.print_header("Running API Tests")
        return self.run_pytest([
            "-v",
            "-m", "api",
            "--tb=short",
            "tests/"
        ], "API tests")
    
    def run_agent_tests(self) -> bool:
        """Run agent tests"""
        self.print_header("Running Agent Tests")
        return self.run_pytest([
            "-v",
            "-m", "agents",
            "--tb=short", 
            "tests/"
        ], "Agent tests")
    
    def run_specific_test(self, test_path: str) -> bool:
        """Run a specific test file or test"""
        self.print_header(f"Running Specific Test: {test_path}")
        return self.run_pytest([
            "-v",
            "--tb=short",
            test_path
        ], f"Test: {test_path}")
    
    def run_coverage_tests(self) -> bool:
        """Run tests with coverage report"""
        self.print_header("Running Tests with Coverage")
        return self.run_pytest([
            "-v",
            "--cov=app",
            "--cov=agents", 
            "--cov=config",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--tb=short",
            "-m", "not integration",
            "tests/"
        ], "Coverage tests")
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        self.print_header("Running Performance Tests")
        self.print_info("Performance tests measure response times and concurrent request handling")
        return self.run_pytest([
            "-v",
            "-k", "performance",
            "--tb=short",
            "tests/"
        ], "Performance tests")
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        self.print_header("Running Complete Test Suite")
        return self.run_pytest([
            "-v",
            "--tb=short",
            "tests/"
        ], "Complete test suite")
    
    def run_fast_tests(self) -> bool:
        """Run fast tests only (exclude integration and performance)"""
        self.print_header("Running Fast Tests")
        return self.run_pytest([
            "-v",
            "-m", "not integration",
            "-k", "not performance",
            "--tb=short",
            "tests/"
        ], "Fast tests")
    
    def show_test_info(self):
        """Show information about available tests"""
        self.print_header("Test Suite Information")
        
        if not self.test_dir.exists():
            self.print_error("Test directory not found")
            return
            
        test_files = list(self.test_dir.glob("test_*.py"))
        
        print(f"{Colors.OKBLUE}Available test files:{Colors.ENDC}")
        for test_file in test_files:
            print(f"  • {test_file.name}")
            
        print(f"\n{Colors.OKBLUE}Test categories:{Colors.ENDC}")
        print("  • Unit tests: Basic functionality tests (fast)")
        print("  • Integration tests: Tests with external APIs (require keys)")
        print("  • API tests: REST endpoint tests")
        print("  • Agent tests: AI agent functionality tests")
        print("  • Performance tests: Response time and load tests")
        
        print(f"\n{Colors.OKBLUE}Test markers:{Colors.ENDC}")
        print("  • @pytest.mark.api - API endpoint tests")
        print("  • @pytest.mark.agents - Agent functionality tests") 
        print("  • @pytest.mark.integration - Integration tests")
        
    def run_health_check(self) -> bool:
        """Run a quick health check"""
        self.print_header("Running Health Check")
        
        # Check if we can import main modules
        try:
            sys.path.insert(0, str(self.project_root))
            
            self.print_info("Testing imports...")
            
            # Test core imports
            from app.main import app
            self.print_success("FastAPI app import successful")
            
            from agents.crypto_advisor import CryptoAdvisorAgent
            self.print_success("Crypto Advisor Agent import successful")
            
            from app.services.unified_crypto_api import UnifiedCryptoAPI
            self.print_success("Unified Crypto API import successful")
            
            # Run a simple test
            return self.run_pytest([
                "-v",
                "--tb=short",
                "-k", "test_health",
                "tests/"
            ], "Health check tests")
            
        except ImportError as e:
            self.print_error(f"Import error: {e}")
            return False
        except Exception as e:
            self.print_error(f"Health check failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test runner for Salt Wallet Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py unit                    # Run unit tests only
  python test_runner.py integration             # Run integration tests
  python test_runner.py api                     # Run API tests
  python test_runner.py agents                  # Run agent tests
  python test_runner.py all                     # Run all tests
  python test_runner.py fast                    # Run fast tests only
  python test_runner.py coverage                # Run with coverage
  python test_runner.py performance             # Run performance tests
  python test_runner.py health                  # Run health check
  python test_runner.py info                    # Show test information
  python test_runner.py specific tests/test_api.py  # Run specific test
        """
    )
    
    parser.add_argument(
        "mode",
        choices=[
            "unit", "integration", "api", "agents", "all", "fast", 
            "coverage", "performance", "health", "info", "specific"
        ],
        help="Test mode to run"
    )
    
    parser.add_argument(
        "test_path",
        nargs="?",
        help="Specific test file or test to run (for 'specific' mode)"
    )
    
    parser.add_argument(
        "--no-env-check",
        action="store_true",
        help="Skip environment check"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Environment check
    if not args.no_env_check and args.mode != "info":
        if not runner.check_environment():
            print(f"\n{Colors.FAIL}Environment check failed. Fix the issues above and try again.{Colors.ENDC}")
            return 1
    
    # Run the requested test mode
    success = False
    
    if args.mode == "unit":
        success = runner.run_unit_tests()
    elif args.mode == "integration":
        success = runner.run_integration_tests()
    elif args.mode == "api":
        success = runner.run_api_tests()
    elif args.mode == "agents":
        success = runner.run_agent_tests()
    elif args.mode == "all":
        success = runner.run_all_tests()
    elif args.mode == "fast":
        success = runner.run_fast_tests()
    elif args.mode == "coverage":
        success = runner.run_coverage_tests()
    elif args.mode == "performance":
        success = runner.run_performance_tests()
    elif args.mode == "health":
        success = runner.run_health_check()
    elif args.mode == "info":
        runner.show_test_info()
        return 0
    elif args.mode == "specific":
        if not args.test_path:
            runner.print_error("Test path is required for 'specific' mode")
            return 1
        success = runner.run_specific_test(args.test_path)
    
    # Print final result
    if success:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All tests completed successfully!{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Some tests failed. Check the output above for details.{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())