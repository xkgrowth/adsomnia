"""Health check and status endpoints."""
from fastapi import APIRouter
from datetime import datetime
from backend.api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Adsomnia Workflow API",
        "version": "1.0.0",
        "description": "API endpoints for Everflow workflows (WF1-WF6)",
        "endpoints": {
            "health": "/health",
            "workflows": "/api/workflows",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

