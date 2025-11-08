"""
FastAPI main application
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

try:
    from fastapi_mcp import FastApiMCP
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

from app.database import SessionLocal, engine

# Import routers
from app.api import auth, ovelser, historikk, utstyr, muskler, admin, statistikk


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title=os.getenv("APP_NAME", "Treningsassistent"),
    description="AI-powered workout recommendation system with muscle balance tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# Configure CORS - adjust origins based on your deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative frontend port
        "https://silverha.hopto.org",  # Production domain
        "http://silverha.hopto.org",  # Production domain (HTTP)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Create and mount MCP server for Claude Code integration (optional, dev only)
if HAS_MCP:
    mcp = FastApiMCP(app)
    mcp.mount_sse(mount_path="/mcp")  # Explicitly use SSE transport with /mcp path


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unhandled errors
    """
    # In production, you might want to log this to a file or service
    print(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "debug": str(exc) if os.getenv("DEBUG", "False") == "True" else None
        }
    )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print("=" * 70)
    print("🚀 TRENINGSASSISTENT API STARTING UP")
    print("=" * 70)

    # Test database connection
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

    print("✅ API ready to accept requests")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print("👋 Shutting down Treningsassistent API")


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Treningsassistent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    # Test database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1")).scalar()
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status
    }


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ovelser.router, prefix="/api/ovelser", tags=["Exercises"])
app.include_router(historikk.router, prefix="/api/historikk", tags=["History"])
app.include_router(statistikk.router, prefix="/api/statistikk", tags=["Statistics"])
app.include_router(utstyr.router, prefix="/api/utstyr", tags=["Equipment"])
app.include_router(muskler.router, prefix="/api/muskler", tags=["Muscles"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# ============================================================================
# DEV MODE ENDPOINTS (only available when DEBUG=True)
# ============================================================================

if os.getenv("DEBUG", "False") == "True":
    @app.get("/debug/db-info", tags=["Debug"])
    async def debug_db_info():
        """
        Debug endpoint to check database table counts
        """
        from app.models import Bruker, Muskel, Utstyr, Ovelse, AntagonistiskPar

        db = SessionLocal()
        try:
            info = {
                "brukere": db.query(Bruker).count(),
                "muskler": db.query(Muskel).count(),
                "utstyr": db.query(Utstyr).count(),
                "ovelser": db.query(Ovelse).count(),
                "antagonistiske_par": db.query(AntagonistiskPar).count(),
            }
            return info
        finally:
            db.close()
