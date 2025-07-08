#!/bin/bash

# Setup script for Salt Wallet Backend

set -e # Exit on any error

echo "💻 Setting up Salt Wallet Backend environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔰 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "💧 Activating virtual environment..."
source .venv/bin/activate

# Install uv if not already installed
echo "🛠️ Checking for uv installation..."
if ! command -v uv &>/dev/null; then
    echo "📥 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies with uv
echo "📚 Installing dependencies..."
uv pip install --upgrade -r requirements.txt
uv pip install pytest pytest-cov black flake8 isort # Development dependencies

# Check if .env file exists, create template if not
if [ ! -f ".env" ]; then
    echo "📍 Creating .env template file..."
    cat >.env <<EOL
# API Configuration
PORT=8000
HOST=0.0.0.0

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/salt_wallet
EOL
    echo "⚠️ Please update the .env file with your actual credentials."
fi

# Create necessary directories if they don't exist
if [ ! -d "data" ]; then
    echo "📂 Creating data directory..."
    mkdir -p data
fi

# Run code formatting
echo "📋 Running code formatting..."
python -m black . --exclude=.venv
python -m isort . --skip=.venv

echo "✅ Setup completed successfully!"
echo "📃 Next steps:"
echo "  1. Update your .env file with actual credentials"
echo "  2. Run 'python -m uvicorn app.main:app --reload' to start the development server"
echo "  3. Visit http://localhost:8000/docs to see the API documentation"
