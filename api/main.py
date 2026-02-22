"""
BA&QA Intelligence Platform — FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from api.config import get_settings
from api.routers import (
    projects,
    documents,
    documents_export,
    evaluation,
    pipeline,
    search,
    upload,
    matching,
    jira,
    design,
    reports,
    settings as settings_router
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()

# Global state for embedding model
embedding_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup/shutdown logic.
    Preloads embedding model to prevent cold start.
    """
    global embedding_model

    # Startup
    logger.info("Starting BA&QA Intelligence Platform API...")

    try:
        # Preload embedding model (prevents 5-10s delay on first search)
        logger.info(f"Preloading embedding model: {settings.embedding_model}")
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload embedding model: {e}")

    logger.info("API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix=f"{settings.api_prefix}/projects", tags=["Projects"])
app.include_router(documents.router, prefix=f"{settings.api_prefix}/documents", tags=["Documents"])
app.include_router(documents_export.router, prefix=f"{settings.api_prefix}/documents-export", tags=["Document Export"])
app.include_router(evaluation.router, prefix=f"{settings.api_prefix}/evaluate", tags=["Evaluation"])
app.include_router(pipeline.router, prefix=f"{settings.api_prefix}/pipeline", tags=["Pipeline"])
app.include_router(search.router, prefix=f"{settings.api_prefix}/search", tags=["Search"])
app.include_router(upload.router, prefix=f"{settings.api_prefix}/upload", tags=["Upload"])
app.include_router(matching.router, prefix=f"{settings.api_prefix}/match", tags=["Matching"])
app.include_router(design.router, prefix=f"{settings.api_prefix}", tags=["Design"])
app.include_router(reports.router, prefix=f"{settings.api_prefix}", tags=["Reports"])
app.include_router(jira.router, prefix=f"{settings.api_prefix}", tags=["JIRA"])
app.include_router(settings_router.router, prefix=f"{settings.api_prefix}/settings", tags=["Settings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "embedding_model_loaded": embedding_model is not None
    }


# ============================================================================
# Static Files (Production React App)
# ============================================================================

# Serve React build in production
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="static")

    # Serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes"""
        # Skip API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return {"error": "Not found"}

        # Serve static files
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Default to index.html for SPA routing
        return FileResponse(frontend_dist / "index.html")
else:
    logger.warning(f"Frontend dist directory not found: {frontend_dist}")
    logger.warning("Run 'cd frontend && npm run build' to build the React app")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
