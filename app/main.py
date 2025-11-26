from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import APP_NAME
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.routers import usage_limit, analyze, feedback, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown.
    - On startup: Connect to MongoDB
    - On shutdown: Close MongoDB connection
    """
    # App startup: create MongoDB client (lazy server selection)
    connect_to_mongo()
    
    yield
    
    # App shutdown
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="API for managing model usage limits",
    version="1.0.0",
    lifespan=lifespan
)

# Add routes
app.include_router(usage_limit.router)
app.include_router(analyze.router)
app.include_router(feedback.router)
app.include_router(history.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Custom exception handler for HTTPException to return consistent error format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail
        }
    )
