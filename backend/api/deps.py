"""Dependencies for FastAPI routes."""
from fastapi import Header, HTTPException, status
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# API Key for authentication (can be set via environment variable)
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from request header.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(api_key: str = Depends(verify_api_key)):
            ...
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header."
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )
    
    return x_api_key

