import os
import sys
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yt_dlp
import logging
import random

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("youtube-extractor")

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
]

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

# Simple functions for YouTube operations
def validate_youtube_url(url):
    """Validate if a URL is a valid YouTube URL."""
    if not url or url.strip() == "":
        return False
        
    try:
        # Simple pattern matching first to avoid unnecessary API calls
        youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
        import re
        if not re.match(youtube_pattern, url):
            logger.warning(f"URL doesn't match YouTube pattern: {url}")
            return False
            
        # Use yt-dlp to validate
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            'cookiefile': None,  # Avoid cookie issues
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
            return True
    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        if "Sign in to confirm you're not a bot" in str(e):
            # Specific error for bot detection
            raise HTTPException(
                status_code=429, 
                detail="YouTube has detected too many requests. Please try again later or a different video."
            )
        return False

def get_video_info(url):
    """Get basic video information."""
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            'cookiefile': None,  # Avoid cookie issues
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                "title": info.get("title", "Unknown title"),
                "author": info.get("uploader", "Unknown uploader"),
                "length_seconds": info.get("duration", 0),
                "thumbnail_url": info.get("thumbnail", ""),
                "youtube_id": info.get("id", ""),
                "youtube_url": url,
            }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        if "Sign in to confirm you're not a bot" in str(e):
            # Specific error for bot detection
            raise HTTPException(
                status_code=429, 
                detail="YouTube has detected too many requests. Please try again later or a different video."
            )
        return None

def get_stream_url(url):
    """Get a streamable audio URL."""
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get the best audio format
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if not audio_formats:
                audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            # Sort by quality
            audio_formats.sort(key=lambda f: f.get('tbr', 0), reverse=True)
            
            if not audio_formats:
                return None
                
            best_audio = audio_formats[0]
            
            return {
                'url': best_audio.get('url'),
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'ext': best_audio.get('ext', 'mp3'),
            }
    except Exception as e:
        logger.error(f"Error getting stream URL: {str(e)}")
        return None

# API routes
@app.get("/")
async def root():
    return {"message": "YouTube Audio Extractor API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Vercel."""
    return {"status": "ok", "message": "API is healthy"}

@app.get("/api/youtube/info")
async def get_youtube_info(url: str = Query(..., description="YouTube video URL")):
    """Get information about a YouTube video."""
    try:
        if not validate_youtube_url(url):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            
        info = get_video_info(url)
        if not info:
            raise HTTPException(status_code=404, detail="Failed to fetch video information")
            
        return info
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="YouTube has detected too many requests. Please try again later or a different video."
            )
        raise HTTPException(status_code=500, detail=f"An error occurred: {error_msg}")

@app.get("/api/youtube/stream-url")
async def get_youtube_stream_url(url: str = Query(..., description="YouTube video URL")):
    """Get a streamable URL for a YouTube video's audio."""
    if not validate_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    info = get_video_info(url)
    if not info:
        raise HTTPException(status_code=404, detail="Failed to fetch video information")
    
    stream_data = get_stream_url(url)
    if not stream_data:
        raise HTTPException(status_code=500, detail="Failed to get streaming URL")
    
    return {
        "title": stream_data.get("title", ""),
        "stream_url": stream_data.get("url", ""),
        "thumbnail": stream_data.get("thumbnail", ""),
        "duration": stream_data.get("duration", 0),
        "format": stream_data.get("ext", "webm"),
        "youtube_url": url,
        "type": "stream",
        "note": "This is a temporary streaming URL that may expire soon."
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
