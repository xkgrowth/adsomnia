"""FastAPI application main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import workflows, health, chat

# Create FastAPI app
app = FastAPI(
    title="Adsomnia Workflow API",
    description="API endpoints for Everflow workflows (WF1-WF6)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("=" * 60)
    print("Adsomnia Workflow API")
    print("=" * 60)
    print("✅ API server starting...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔑 API Key required for all workflow endpoints")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

