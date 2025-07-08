#!/usr/bin/env python3
"""
Script to run the Salt Wallet API server locally with proper configuration.
This handles common import errors and ensures the environment is set up correctly.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("run_server")

def check_env_file():
    """Check if .env file exists and create if missing"""
    dotenv_path = Path(__file__).resolve().parent / '.env'
    if not dotenv_path.exists():
        logger.warning(f".env file not found at {dotenv_path}, creating sample file")
        with open(dotenv_path, 'w') as f:
            f.write("# Environment Variables\n")
            f.write("GEMINI_API_KEY=your_api_key_here\n")
            f.write("MONGODB_URI=mongodb://localhost:27017\n")
            f.write("DATABASE_NAME=salt_wallet\n")
            f.write("JWT_SECRET=change-this-in-production\n")
            f.write("APP_NAME=Salt Wallet\n")
            f.write("SOLANA_RPC_URL=https://api.mainnet-beta.solana.com\n")
            f.write("SOLANA_NETWORK=mainnet\n")
        logger.info(f"Created sample .env file at {dotenv_path}")
    else:
        logger.info(f"Found .env file at {dotenv_path}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "fastapi", "uvicorn", "motor", "pymongo", "pyjwt", 
        "eth-account", "base58", "solana"
    ]
    
    missing_packages = []
    
    logger.info("Checking installed packages...")
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            logger.error(f"❌ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing packages: {', '.join(missing_packages)}")
        install = input("Would you like to install missing packages? (y/n): ")
        if install.lower() == 'y':
            cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages"] + missing_packages
            subprocess.check_call(cmd)
            logger.info("Packages installed successfully")
        else:
            logger.warning("Missing packages not installed, server may not run correctly")

def run_server():
    """Run the server using uvicorn"""
    check_env_file()
    check_dependencies()
    
    logger.info("Starting server...")
    os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    run_server() 