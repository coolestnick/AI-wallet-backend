# Deployment Guide - Vercel

This guide explains how to deploy the AI Wallet Backend to Vercel.

## 🚀 Deployment Options

### Option 1: Deploy Both Frontend and Backend (Recommended)

1. **Clone your repository**:
   ```bash
   git clone https://github.com/coolestnick/AI-wallet-backend.git
   cd AI-wallet-backend
   ```

2. **Deploy to Vercel using CLI**:
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

### Option 2: Deploy Frontend and Backend Separately

#### Deploy Backend API First:

1. **Deploy backend**:
   ```bash
   vercel --prod --config vercel-backend.json
   ```

2. **Set environment variables**:
   ```bash
   vercel env add GEMINI_API_KEY
   vercel env add FIRECRAWL_API_KEY
   vercel env add JWT_SECRET
   vercel env add MONGODB_URI
   ```

#### Deploy Frontend:

1. **Update API URL** in `vercel-frontend.json` with your backend URL

2. **Deploy frontend**:
   ```bash
   vercel --prod --config vercel-frontend.json
   ```

## 🔑 Required Environment Variables

Set these in your Vercel dashboard or via CLI:

### Backend Variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `FIRECRAWL_API_KEY`: Your Firecrawl API key  
- `JWT_SECRET`: Secret key for JWT tokens
- `MONGODB_URI`: MongoDB connection string

### Frontend Variables:
- `NEXT_PUBLIC_API_URL`: Your deployed backend URL

## 📂 Project Structure for Vercel

```
AI-wallet-backend/
├── api/
│   └── index.py              # Vercel serverless entry point
├── agno_ui/crypto-research-ui/  # Next.js frontend
├── vercel.json               # Main Vercel config
├── vercel-backend.json       # Backend-only config
├── vercel-frontend.json      # Frontend-only config
└── requirements.txt          # Python dependencies
```

## 🛠️ Configuration Files

### vercel.json (Main Config)
Deploys both frontend and backend in a single project.

### vercel-backend.json
Backend-only deployment for API endpoints.

### vercel-frontend.json  
Frontend-only deployment for the UI.

## 🔧 API Endpoints

After deployment, your API will be available at:
- `https://your-project.vercel.app/api/v1/agents`
- `https://your-project.vercel.app/api/v1/agents/{agent_id}/chat`
- `https://your-project.vercel.app/api/v1/agents/{agent_id}/chat/stream`

## 🎯 Testing Deployment

1. **Check API health**:
   ```bash
   curl https://your-project.vercel.app/health
   ```

2. **Test agent list**:
   ```bash
   curl https://your-project.vercel.app/api/v1/agents
   ```

3. **Access frontend**:
   Visit `https://your-project.vercel.app` in your browser

## 🚨 Important Notes

1. **Serverless Limitations**: 
   - Function timeout: 30 seconds max
   - Memory: 1024MB max
   - No persistent storage

2. **Database**: 
   - Use MongoDB Atlas (cloud) instead of local MongoDB
   - Update connection string in environment variables

3. **File Storage**:
   - Vercel functions are stateless
   - Use external storage for files if needed

## 🔍 Troubleshooting

### Common Issues:

1. **Module not found errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check import paths in `api/index.py`

2. **Environment variables not working**:
   - Verify variables are set in Vercel dashboard
   - Restart deployment after adding variables

3. **API timeout errors**:
   - Optimize agent response times
   - Consider using async operations

4. **CORS errors**:
   - Check CORS configuration in `api/index.py`
   - Ensure frontend URL is allowed

## 📊 Monitoring

Monitor your deployment:
- Vercel Dashboard: Function logs and analytics
- Error tracking: Check function execution logs
- Performance: Monitor response times

## 🔄 Continuous Deployment

Connect your GitHub repository to Vercel for automatic deployments:
1. Import project in Vercel dashboard
2. Connect to GitHub repository
3. Set environment variables
4. Deploy automatically on git push

## 🎉 Success\!

Your AI Wallet Backend should now be live on Vercel with:
- ✅ FastAPI backend as serverless functions
- ✅ Next.js frontend with modern UI
- ✅ Real-time AI agent interactions
- ✅ Web scraping capabilities
- ✅ Automatic HTTPS and CDN
EOF < /dev/null