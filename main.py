from fastapi import FastAPI
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

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="QC Panel API",
    description="Quality Control Panel Backend API",
    version="1.0.0"
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event - don't check database here"""
    import logging
    logging.info("QC Panel API is starting...")
    logging.info("Database connection will be tested on first request")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    import logging
    logging.info("QC Panel API is shutting down...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(reviews.router)
app.include_router(comparison.router)
app.include_router(dashboard.router)
app.include_router(leaderboard.router)
app.include_router(settings_routes.router)
app.include_router(agents.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QC Panel API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unknown"
    try:
        from database import get_db_connection
        # Run sync database call in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(None, get_db_connection)
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)[:50]}"

    return {
        "status": "healthy",
        "database": db_status
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host=settings.API_HOST,
#         port=settings.API_PORT,
#         reload=True
#     )
