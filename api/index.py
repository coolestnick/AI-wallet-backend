from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app

# Configure CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the Mangum handler for Vercel
handler = Mangum(app)
EOF < /dev/null