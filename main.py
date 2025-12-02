import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routes import (
    auth,
    users,
    conversations,
    reviews,
    comparison,
    dashboard,
    leaderboard,
    agents
)
from routes import settings as settings_routes
import time
from contextlib import asynccontextmanager

# Initialize settings first
settings = get_settings()

# Configure logging with level from settings
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log the configured log level
logger.info(f"Logging configured with level: {settings.LOG_LEVEL.upper()}")

# Initialize settings
logger.info("Loading application settings...")
logger.info(f"Settings loaded - API will run on {settings.API_HOST}:{settings.API_PORT}")


# Lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("=" * 50)
        logger.info("LIFESPAN: Starting application startup sequence...")
        logger.info("=" * 50)
        logger.info("QC Panel API is starting...")
        logger.info(f"Version: 1.0.0")
        logger.info(f"Host: {settings.API_HOST}:{settings.API_PORT}")
        logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
        logger.info(f"Database Host: {settings.POSTGRES_HOST}")
        logger.info(f"Database: {settings.POSTGRES_DATABASE}")
        logger.info(f"Schema: {settings.POSTGRES_SCHEMA}")
        logger.info("Database connection will be tested on first request")
        logger.info("=" * 50)
        logger.info("LIFESPAN: Startup complete, application ready!")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"LIFESPAN: Startup failed with error: {e}")
        logger.exception("Full traceback:")
        raise

    yield

    # Shutdown
    try:
        logger.info("=" * 50)
        logger.info("LIFESPAN: Starting shutdown sequence...")
        logger.info("QC Panel API is shutting down...")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"LIFESPAN: Shutdown error: {e}")


# Create FastAPI app with lifespan
logger.info("Creating FastAPI application...")
app = FastAPI(
    title="QC Panel API",
    description="Quality Control Panel Backend API",
    version="1.0.0",
    lifespan=lifespan
)
logger.info("FastAPI application created")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.3f}s"
        )
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
        logger.exception("Request exception traceback:")
        raise

logger.info("Request logging middleware registered")

# Configure CORS
logger.info("Configuring CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured for origins: {settings.CORS_ORIGINS}")

# Include routers
logger.info("Registering API routes...")
app.include_router(auth.router)
logger.info("  - Auth routes registered")
app.include_router(users.router)
logger.info("  - Users routes registered")
app.include_router(conversations.router)
logger.info("  - Conversations routes registered")
app.include_router(reviews.router)
logger.info("  - Reviews routes registered")
app.include_router(comparison.router)
logger.info("  - Comparison routes registered")
app.include_router(dashboard.router)
logger.info("  - Dashboard routes registered")
app.include_router(leaderboard.router)
logger.info("  - Leaderboard routes registered")
app.include_router(settings_routes.router)
logger.info("  - Settings routes registered")
app.include_router(agents.router)
logger.info("  - Agents routes registered")
logger.info("All routes registered successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    logger.debug("Root endpoint called")
    return {
        "message": "QC Panel API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint - no database check"""
    logger.debug("Health check endpoint called")
    return {
        "status": "healthy",
        "service": "qc-panel-api",
        "version": "1.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database status"""
    logger.info("Detailed health check started")
    db_status = "unknown"
    db_error = None

    try:
        logger.debug("Attempting database connection...")
        from database import get_db_connection
        # Run sync database call in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(None, get_db_connection)
        conn.close()
        db_status = "connected"
        logger.info("Database connection successful")
    except Exception as e:
        db_status = "disconnected"
        db_error = str(e)[:100]
        logger.error(f"Database connection failed: {db_error}")

    result = {
        "status": "healthy",
        "database": db_status,
        "service": "qc-panel-api",
        "version": "1.0.0"
    }

    if db_error:
        result["database_error"] = db_error

    return result


# Final initialization logs
logger.info("=" * 50)
logger.info("MODULE LOADED: main.py initialization complete")
logger.info("Application is ready to receive requests")
logger.info("Waiting for Uvicorn to start the server...")
logger.info("=" * 50)

# Signal handler for debugging
import signal
import sys as system

def signal_handler(sig, frame):
    sig_name = signal.Signals(sig).name
    logger.warning(f"SIGNAL RECEIVED: {sig_name} (signal {sig})")
    logger.warning("Application is terminating...")
    system.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
logger.info("Signal handlers registered (SIGTERM, SIGINT)")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host=settings.API_HOST,
#         port=settings.API_PORT,
#         reload=True
#     )
