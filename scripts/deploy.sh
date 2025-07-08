#!/bin/bash

# Deployment script for Salt Wallet API

set -e # Exit on any error

echo "🚀 Starting deployment for Salt Wallet API..."

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set."
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable is not set."
    exit 1
fi

echo "🔍 Running tests..."
python -m pytest tests/

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Aborting deployment."
    exit 1
fi

# Create a Dockerfile.deploy with uv for faster dependency installation
echo "📝 Creating optimized Dockerfile..."
cat >Dockerfile.deploy <<EOL
FROM python:3.11-slim

WORKDIR /app

# Install uv for faster package installation
RUN pip install uv

# Copy requirements first for better layer caching
COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOL

echo "🏗️ Building Docker image..."
docker build -t salt-wallet:beta -f Dockerfile.deploy .

echo "🔄 Stopping old container (if exists)..."
docker stop salt-wallet || true
docker rm salt-wallet || true

echo "🚢 Starting new container..."
docker run -d \
    --name salt-wallet \
    -p 8000:8000 \
    -e DATABASE_URL="$DATABASE_URL" \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e PORT="8000" \
    -e HOST="0.0.0.0" \
    salt-wallet:beta

# Clean up temporary Dockerfile
rm Dockerfile.deploy

echo "✅ Deployment completed successfully!"
echo "📝 API documentation available at: http://localhost:8000/docs"
