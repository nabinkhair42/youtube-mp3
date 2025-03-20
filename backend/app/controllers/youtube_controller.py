import os
from fastapi import HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import requests
from app.utils.youtube_extractor import YouTubeExtractor
from app.utils.logger import get_logger

logger = get_logger("youtube_controller")

class YouTubeController:
    @staticmethod
    async def get_video_info(url: str):
        """Get information about a YouTube video."""
        request_id = str(id(url))[-6:]  # Simple request identifier
        
        logger.info(f"[{request_id}] Getting video info for URL: {url}")
        
        if not YouTubeExtractor.validate_url(url):
            logger.warning(f"[{request_id}] Invalid YouTube URL: {url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        video_info = YouTubeExtractor.get_video_info(url)
        if not video_info:
            logger.error(f"[{request_id}] Failed to fetch video information for URL: {url}")
            raise HTTPException(status_code=404, detail="Failed to fetch video information")
        
        logger.info(f"[{request_id}] Successfully retrieved info for: {video_info.get('title')}")
        return video_info
    
    @staticmethod
    async def extract_audio(url: str, max_duration: int = 600):
        """Extract audio from a YouTube video and return it as MP3."""
        request_id = str(id(url))[-6:]  # Simple request identifier
        
        logger.info(f"[{request_id}] Processing audio extraction request for URL: {url}")
        
        if not YouTubeExtractor.validate_url(url):
            logger.warning(f"[{request_id}] Invalid YouTube URL: {url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Check video length first
        logger.debug(f"[{request_id}] Checking video duration...")
        video_info = YouTubeExtractor.get_video_info(url)
        
        if not video_info:
            logger.error(f"[{request_id}] Failed to fetch video information for URL: {url}")
            raise HTTPException(status_code=404, detail="Failed to fetch video information")
            
        video_duration = video_info.get('length_seconds', 0)
        
        if video_duration > max_duration:
            logger.warning(f"[{request_id}] Video exceeds maximum duration: {video_duration}s > {max_duration}s")
            raise HTTPException(
                status_code=400,
                detail=f"Video is too long. Maximum allowed duration is {max_duration} seconds."
            )
        
        logger.info(f"[{request_id}] Duration check passed: {video_duration}s")
        logger.info(f"[{request_id}] Extracting audio for: {video_info.get('title', 'Unknown video')}")
        
        file_path, file_name, content_type = await YouTubeExtractor.extract_audio(url)
        
        if not file_path or not os.path.exists(file_path):
            logger.error(f"[{request_id}] Failed to extract audio from URL: {url}")
            
            # Try getting stream URL as fallback
            stream_data = YouTubeExtractor.get_stream_url(url)
            if not stream_data:
                raise HTTPException(status_code=500, detail="Failed to extract audio")
                
            # Return more structured stream URL information
            return JSONResponse(content={
                "title": stream_data.get("title", ""),
                "stream_url": stream_data.get("url", ""),
                "thumbnail": stream_data.get("thumbnail", ""),
                "duration": stream_data.get("duration", 0),
                "type": "stream",
                "format": stream_data.get("ext", "mp3"),
                "youtube_url": url,
                "note": "This is a temporary streaming URL that may expire. For long-term storage, download the audio."
            })
        
        # Get file size for logging
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logger.info(f"[{request_id}] Successfully extracted audio: {file_name} (Size: {file_size:.2f} MB)")
        
        # Return the audio file
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    
    @staticmethod
    async def get_stream_url(url: str, max_duration: int = 600):
        """Get a streamable URL for the audio of a YouTube video."""
        request_id = str(id(url))[-6:]
        
        logger.info(f"[{request_id}] Processing stream URL request for URL: {url}")
        
        # Add validation for empty URL
        if not url or url.strip() == "":
            logger.warning(f"[{request_id}] Empty URL provided")
            raise HTTPException(status_code=400, detail="YouTube URL cannot be empty")
        
        if not YouTubeExtractor.validate_url(url):
            logger.warning(f"[{request_id}] Invalid YouTube URL: {url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Check video length first
        video_info = YouTubeExtractor.get_video_info(url)
        if not video_info:
            logger.error(f"[{request_id}] Failed to fetch video information for URL: {url}")
            raise HTTPException(status_code=404, detail="Failed to fetch video information")
            
        video_duration = video_info.get('length_seconds', 0)
        if video_duration > max_duration:
            logger.warning(f"[{request_id}] Video exceeds maximum duration: {video_duration}s > {max_duration}s")
            raise HTTPException(
                status_code=400,
                detail=f"Video is too long. Maximum allowed duration is {max_duration} seconds."
            )
        
        # Get the stream URL directly
        stream_data = YouTubeExtractor.get_stream_url(url)
        if not stream_data:
            logger.error(f"[{request_id}] Failed to get stream URL for: {url}")
            raise HTTPException(status_code=500, detail="Failed to get streaming URL")
        
        logger.info(f"[{request_id}] Successfully retrieved stream URL for: {stream_data.get('title')}")
        
        # Return more structured information
        return {
            "title": stream_data.get("title", ""),
            "stream_url": stream_data.get("url", ""),
            "thumbnail": stream_data.get("thumbnail", ""),
            "duration": stream_data.get("duration", 0),
            "format": stream_data.get("ext", "webm"),
            "youtube_url": url,
            "type": "stream",
            "note": "This is a temporary streaming URL that may expire soon. For long-term storage, download the audio."
        }
    
    @staticmethod
    async def proxy_audio(url: str):
        """Proxy the audio content from YouTube to avoid CORS and URL expiration issues."""
        request_id = str(id(url))[-6:]
        
        logger.info(f"[{request_id}] Processing audio proxy request for URL: {url}")
        
        if not YouTubeExtractor.validate_url(url):
            logger.warning(f"[{request_id}] Invalid YouTube URL: {url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Get fresh stream URL
        stream_data = YouTubeExtractor.get_stream_url(url)
        if not stream_data or not stream_data.get('url'):
            logger.error(f"[{request_id}] Failed to get stream URL for: {url}")
            raise HTTPException(status_code=500, detail="Failed to get streaming URL")
            
        audio_url = stream_data.get('url')
        content_type = f"audio/{stream_data.get('audio_ext', 'mp4')}"
        
        # Create a streaming response that proxies the YouTube audio
        async def stream_audio():
            try:
                with requests.get(audio_url, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
            except Exception as e:
                logger.error(f"[{request_id}] Error streaming audio: {str(e)}")
                yield b""
        
        logger.info(f"[{request_id}] Streaming audio content for: {stream_data.get('title')}")
        
        return StreamingResponse(
            stream_audio(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=\"{stream_data.get('title', 'audio')}.{stream_data.get('audio_ext', 'mp4')}\"",
                "Accept-Ranges": "bytes"
            }
        )
