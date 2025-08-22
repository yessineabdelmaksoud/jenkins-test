"""FastAPI application for AI Agents deployment."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
import sys 
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from ai_agents.deployment.api_agent.api.routes import agents
from ai_agents.deployment.api_agent.core.config import get_settings
from ai_agents.deployment.api_agent.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="AI Agents API",
        description="API for managing and executing AI agents",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(agents.router, prefix="/api", tags=["agents"])
    
    # Mount static files for dashboard
    dashboard_path = Path(__file__).parent / "dashboard"
    if dashboard_path.exists():
        app.mount("/static", StaticFiles(directory=str(dashboard_path)), name="static")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "AI Agents API", "version": "1.0.0", "dashboard": "/dashboard"}

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Jenkins Agent Dashboard."""
        dashboard_file = Path(__file__).parent / "dashboard" / "index.html"
        if dashboard_file.exists():
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="Dashboard not found")

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
