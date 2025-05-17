"""
Runner script to start the FastAPI server with Uvicorn.
"""

import os
import argparse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISDBI Agent API Server")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to run the server on"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes"
    )
    
    args = parser.parse_args()
    
    # Set number of workers based on environment variable if available
    workers = int(os.environ.get("API_WORKERS", args.workers))
    
    # Start Uvicorn server
    uvicorn.run(
        "api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=workers,
    )
