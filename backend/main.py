"""
FastAPI application entry point.
Configures middleware, routers, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import sessions, audio, search, employees


# Lifespan Events (Startup/Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    Use for:
    - Loading ML models
    - Opening database pools
    - Initializing caches
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Environment: {'Development' if settings.debug else 'Production'}")
    print(f"🔗 Supabase: {settings.supabase_url}")
    
    # Load models here (optional)
    # global transcription_model
    # transcription_model = load_whisper_model()
    
    yield  # App runs here
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for knowledge transfer during employee offboarding",
    docs_url="/docs" if settings.debug else None,  # Disable in production
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# CORS Middleware (für Next.js Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(
    employees.router,
    prefix=f"{settings.api_v1_prefix}/employees",
    tags=["employees"]
)

app.include_router(
    sessions.router,
    prefix=f"{settings.api_v1_prefix}/sessions",
    tags=["sessions"]
)

app.include_router(
    audio.router,
    prefix=f"{settings.api_v1_prefix}/audio",
    tags=["audio"]
)

app.include_router(
    search.router,
    prefix=f"{settings.api_v1_prefix}/search",
    tags=["search"]
)


# Root Endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "docs": "/docs" if settings.debug else "disabled"
    }


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all for unhandled exceptions"""
    if settings.debug:
        # In development: Show full error
        raise exc
    else:
        # In production: Hide details
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )