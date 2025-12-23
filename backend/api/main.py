"""FastAPI application main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import workflows, health, entities
import logging

logger = logging.getLogger(__name__)

# Import chat route conditionally (may fail if LangChain dependencies are missing)
try:
    from backend.api.routes import chat
    CHAT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Chat route not available: {e}")
    CHAT_AVAILABLE = False
    chat = None

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
if CHAT_AVAILABLE and chat:
    app.include_router(chat.router)
app.include_router(entities.router)


@app.on_event("startup")
async def startup_event():
    """Initialize API and validate Everflow endpoints."""
    print("=" * 60)
    print("🚀 Adsomnia Workflow API Starting...")
    print("=" * 60)
    
    # Initialize and validate Everflow API
    print("\n📋 Validating Everflow API endpoints...")
    try:
        from backend.sql_agent.everflow_api_validator import get_validator
        
        validator = get_validator()
        validator.initialize(force_refresh=False)
        
        # Validate all endpoints
        validation_results = validator.validate_all_endpoints()
        
        # Report results
        valid_count = sum(1 for r in validation_results.values() if r.valid)
        total_count = len(validation_results)
        
        print(f"   ✅ {valid_count}/{total_count} endpoints validated")
        
        # Show warnings
        for endpoint, result in validation_results.items():
            if result.warnings:
                for warning in result.warnings:
                    print(f"   ⚠️  {endpoint}: {warning}")
            if not result.valid:
                for error in result.errors:
                    print(f"   ❌ {endpoint}: {error}")
        
        print("   ✅ Everflow API validation complete")
    except Exception as e:
        logger.error(f"Error validating Everflow API: {e}")
        print(f"   ⚠️  Warning: Could not validate Everflow API endpoints: {e}")
    
    print("\n🔑 API Key required for all workflow endpoints")
    print("📚 Interactive docs available at: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

