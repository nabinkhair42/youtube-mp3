import os
import sys
import time
from pathlib import Path

# Configure Python path to find app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
from app.utils.logger import setup_logging, get_logger
logger = setup_logging()

# Check for dependencies
def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import yt_dlp
        logger.info(f"yt-dlp version: {yt_dlp.version.__version__}")
        
        # Check if FFmpeg is in PATH or in the bin directory
        bin_dir = Path(__file__).parent / "bin"
        if bin_dir.exists():
            os.environ["PATH"] = f"{bin_dir};{os.environ['PATH']}"
            logger.info(f"Added {bin_dir} to PATH")
        
        # Check if FFmpeg is available
        import shutil
        if shutil.which('ffmpeg') is None:
            logger.warning("FFmpeg not found. Audio extraction will use native formats instead of MP3.")
            logger.info("To install FFmpeg manually, run: python setup_ffmpeg.py")
        else:
            logger.info(f"FFmpeg found: {shutil.which('ffmpeg')}")
    
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)

# Check dependencies before starting the app
check_dependencies()

# Import FastAPI components
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routes
from app.routes.youtube_routes import router as youtube_router

# Create FastAPI app
app = FastAPI(
    title="YouTube Audio Extractor API",
    description="API for extracting audio from YouTube videos",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")
    return response

# Include routers
app.include_router(youtube_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "YouTube Audio Extractor API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Vercel."""
    return {"status": "ok", "message": "API is healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
