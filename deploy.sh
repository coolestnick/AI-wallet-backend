#\!/bin/bash

echo "🚀 Deploying AI Wallet Backend to Vercel..."

# Check if Vercel CLI is installed
if \! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "Please login to Vercel if prompted..."
vercel login

# Deploy to production
echo "Deploying to production..."
vercel --prod

echo "✅ Deployment complete\!"
echo "🌐 Your app should be available at the URL shown above"
echo ""
echo "🔧 To test your deployment:"
echo "1. Check API health: curl https://your-app.vercel.app/health"
echo "2. List agents: curl https://your-app.vercel.app/api/v1/agents"
echo "3. Open frontend: https://your-app.vercel.app"
