#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Salt Wallet Backend Setup${NC}"

# Check if uv is installed
if ! command -v uv &>/dev/null; then
    echo -e "${RED}uv is not installed.${NC}"
    echo -e "${YELLOW}Installing uv...${NC}"
    curl -sSf https://install.python-poetry.org | python3 -
    pip install uv
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file${NC}"
    cat >.env <<EOF
# Environment Variables
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=salt_wallet
JWT_SECRET=change-this-in-production
APP_NAME=Salt Wallet
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_NETWORK=mainnet
EOF
    echo -e "${GREEN}.env file created${NC}"
else
    echo -e "${GREEN}.env file exists${NC}"
fi

# Create and activate virtual environment using uv
echo -e "${YELLOW}Setting up virtual environment...${NC}"
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies with uv
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -r requirements.txt

# Note: Solana functionality is disabled for now
# To enable it later, install: solders, httpx, pycryptodome, base58

# Run the application
echo -e "${GREEN}Starting server...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
