import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as agent_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.crypto_data import router as crypto_data_router

# Try to import Solana router but don't fail if not available
SOLANA_AVAILABLE = False
try:
    from app.api.solana import router as solana_router
    SOLANA_AVAILABLE = True
except ImportError:
    logging.warning("Solana dependencies are not available. Solana functionality will be disabled.")

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    logging.info(f"Loaded environment from {dotenv_path}")
else:
    logging.warning(f".env file not found at {dotenv_path}")
    # Create a sample .env file if it doesn't exist
    with open(dotenv_path, 'w') as f:
        f.write("# Environment Variables\n")
        f.write("GEMINI_API_KEY=your_api_key_here\n")
        f.write("MONGODB_URI=mongodb://localhost:27017\n")
        f.write("DATABASE_NAME=salt_wallet\n")
        f.write("JWT_SECRET=change-this-in-production\n")
        f.write("APP_NAME=Salt Wallet\n")
        f.write("SOLANA_RPC_URL=https://api.mainnet-beta.solana.com\n")
        f.write("SOLANA_NETWORK=mainnet\n")
    logging.info(f"Created sample .env file at {dotenv_path}")

# Check if required environment variables are set
if not os.getenv("GEMINI_API_KEY"):
    logging.warning("GEMINI_API_KEY environment variable is not set! API calls to Gemini will fail.")
if not os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET") == "change-this-in-production":
    logging.warning("JWT_SECRET is not properly set! Authentication will not be secure in production.")
if SOLANA_AVAILABLE and not os.getenv("SOLANA_RPC_URL"):
    logging.warning("SOLANA_RPC_URL is not set. Using default public endpoint which may have rate limits.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Create FastAPI app
app = FastAPI(
    title="Salt Wallet API",
    description="API for AI Crypto Agents in Salt Wallet",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development frontend
        "https://saltwallet.xyz",  # Production frontend
        "https://app.saltwallet.xyz",  # Production app
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(crypto_data_router, prefix="/api/v1")

# Only include Solana router if available
if SOLANA_AVAILABLE:
    app.include_router(solana_router, prefix="/api/v1")
    logging.info("Solana functionality enabled")
else:
    logging.warning("Solana functionality disabled due to missing dependencies")


@app.get("/")
async def root():
    return {"message": "Welcome to the Salt Wallet API"}


@app.get("/health")
async def health_check():
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    jwt_secret = os.getenv("JWT_SECRET", "")
    mongodb_uri = os.getenv("MONGODB_URI", "")
    solana_rpc_url = os.getenv("SOLANA_RPC_URL", "")
    
    api_key_status = "configured" if gemini_api_key else "missing"
    jwt_status = "configured" if jwt_secret and jwt_secret != "change-this-in-production" else "insecure"
    db_status = "configured" if mongodb_uri else "missing"
    solana_status = "disabled (dependencies missing)"
    
    if SOLANA_AVAILABLE:
        solana_status = "configured" if solana_rpc_url else "using public endpoint"
    
    return {
        "status": "healthy",
        "gemini_api": api_key_status,
        "auth": jwt_status,
        "database": db_status,
        "solana": solana_status
    }


# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    logging.info(f"Request: {method} {path}")
    
    response = await call_next(request)
    
    logging.info(f"Response: {method} {path} - Status: {response.status_code}")
    
    return response

# Placeholder for other feature routers (to be implemented)
# from .api import notifications, assets, security, assistant
# app.include_router(notifications.router)
# app.include_router(assets.router)
# app.include_router(security.router)
# app.include_router(assistant.router)
