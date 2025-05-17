"""
FastAPI application exposing ISDBI agents as API endpoints.
This provides RESTful access to the various agent capabilities.
"""

import os
import logging
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import time

# Import routers
from .routers import use_case, transaction,  enhancement

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="ISDBI Agent API",
    description="API for accessing Islamic Finance standards agents and services",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Add middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log requests and timing."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response


# Add middleware for global exception handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )


# Include routers
app.include_router(use_case.router)
app.include_router(transaction.router)
app.include_router(enhancement.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "ISDBI Agent API",
        "version": "1.0.0",
        "description": "API for accessing Islamic Finance standards agents and services",
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
