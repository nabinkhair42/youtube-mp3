from fastapi import APIRouter, Query
from app.controllers.youtube_controller import YouTubeController

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
    responses={404: {"description": "Not found"}},
)

@router.get("/info")
async def get_video_info(url: str = Query(..., description="YouTube video URL")):
    """Get information about a YouTube video."""
    return await YouTubeController.get_video_info(url)

@router.get("/extract-audio")
async def extract_audio(
    url: str = Query(..., description="YouTube video URL"),
    max_duration: int = Query(600, description="Maximum video duration in seconds (default: 600)")
):
    """Extract audio from a YouTube video and return it as MP3.
    Falls back to streaming URL if direct download fails."""
    return await YouTubeController.extract_audio(url, max_duration)

@router.get("/stream-url")
async def get_stream_url(
    url: str = Query(..., description="YouTube video URL")
):
    """Get a streamable URL for the audio."""
    return await YouTubeController.get_stream_url(url)

@router.get("/proxy-audio")
async def proxy_audio(
    url: str = Query(..., description="YouTube video URL")
):
    """Proxy the audio content from YouTube to avoid CORS and URL expiration issues."""
    return await YouTubeController.proxy_audio(url)
