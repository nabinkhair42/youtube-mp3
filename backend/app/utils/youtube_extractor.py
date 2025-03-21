import os
import tempfile
import uuid
import random
from typing import Optional, Tuple, Dict, Any
import re
import yt_dlp
from app.utils.logger import get_logger
import shutil

logger = get_logger("youtube_extractor")

# List of common user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
]

class YouTubeExtractor:
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if the provided URL is a valid YouTube URL."""
        try:
            # Simple YouTube URL pattern matching
            youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
            if not re.match(youtube_pattern, url):
                logger.warning(f"URL doesn't match YouTube pattern: {url}")
                return False
                
            # Use yt-dlp to validate the URL with a random user agent
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'no_warnings': True,
                'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            }
            
            logger.debug(f"Validating YouTube URL: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=False)
                logger.debug(f"URL validation successful: {url}")
                return True
                
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False
    
    @staticmethod
    def get_stream_url(url: str) -> Optional[Dict[str, Any]]:
        """
        Get a streamable audio URL instead of downloading the file.
        This is more reliable for browser playback.
        """
        info_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(f"[{info_id}] Getting stream URL for: {url}")
            
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'format': 'bestaudio/best',
                'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.error(f"[{info_id}] Failed to extract stream info")
                    return None
                
                # Get the best audio format
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                
                if not audio_formats:
                    logger.warning(f"[{info_id}] No audio-only formats found, using best format with audio")
                    audio_formats = [f for f in formats if f.get('acodec') != 'none']
                
                # Sort by quality (bitrate)
                audio_formats.sort(key=lambda f: f.get('tbr', 0), reverse=True)
                
                if not audio_formats:
                    logger.error(f"[{info_id}] No suitable audio format found")
                    return None
                
                best_audio = audio_formats[0]
                
                stream_data = {
                    'url': best_audio.get('url'),
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'ext': best_audio.get('ext', 'mp3'),
                }
                
                logger.info(f"[{info_id}] Successfully retrieved stream URL for: {info.get('title')}")
                return stream_data
                
        except Exception as e:
            logger.error(f"[{info_id}] Error getting stream URL: {str(e)}")
            return None
    
    @staticmethod
    async def extract_audio(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract audio from a YouTube video using yt-dlp.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple containing (file_path, file_name, content_type)
            Returns (None, None, None) if extraction fails
        """
        extraction_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(f"[{extraction_id}] Starting audio extraction from: {url}")
            
            # Create a unique filename with UUID
            file_id = str(uuid.uuid4())[:8]
            temp_dir = tempfile.gettempdir()
            output_template = os.path.join(temp_dir, f"audio_{file_id}.%(ext)s")
            
            # Check if FFmpeg is available
            ffmpeg_available = shutil.which('ffmpeg') is not None
            logger.info(f"[{extraction_id}] FFmpeg available: {ffmpeg_available}")
            
            # Configure yt-dlp options
            if (ffmpeg_available):
                # Use FFmpeg for conversion if available
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                    'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
                }
            else:
                # Fall back to native m4a if FFmpeg is not available
                logger.warning(f"[{extraction_id}] FFmpeg not available, using native audio format")
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': output_template,
                    'quiet': True,
                    'no_warnings': True,
                    'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
                }
            
            # Get title for better filename
            info_opts = {
                'quiet': True,
                'skip_download': True,
                'no_warnings': True,
                'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            }
            
            title = None
            try:
                with yt_dlp.YoutubeDL(info_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', None)
                    logger.info(f"[{extraction_id}] Retrieved video title: {title}")
            except Exception as e:
                logger.warning(f"[{extraction_id}] Could not get video title: {str(e)}")
            
            # Download the audio
            logger.info(f"[{extraction_id}] Starting download with yt-dlp...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info(f"[{extraction_id}] Download completed")
                
            # Find the output file
            output_file = None
            output_ext = 'mp3' if ffmpeg_available else 'm4a'
            
            for file in os.listdir(temp_dir):
                if file.startswith(f"audio_{file_id}"):
                    output_file = os.path.join(temp_dir, file)
                    output_ext = os.path.splitext(file)[1][1:]  # Get the extension without dot
                    break
            
            if not output_file:
                logger.error(f"[{extraction_id}] Output file not found after download")
                return None, None, None
                
            # Create a more user-friendly filename if we have the title
            if title:
                # Sanitize title for use as filename
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                safe_title = safe_title[:30]  # Limit length
                safe_filename = f"{safe_title.replace(' ', '_')}_{file_id}.{output_ext}"
                new_filepath = os.path.join(temp_dir, safe_filename)
                
                if not os.path.exists(new_filepath):
                    try:
                        os.rename(output_file, new_filepath)
                        logger.info(f"[{extraction_id}] Renamed output file to: {new_filepath}")
                        output_file = new_filepath
                    except Exception as e:
                        logger.warning(f"[{extraction_id}] Failed to rename file: {str(e)}")
            
            # Determine content type based on extension
            content_type_map = {
                'mp3': 'audio/mpeg',
                'm4a': 'audio/mp4',
                'ogg': 'audio/ogg',
                'wav': 'audio/wav',
                'webm': 'audio/webm',
            }
            content_type = content_type_map.get(output_ext, 'application/octet-stream')
            
            logger.info(f"[{extraction_id}] Successfully processed audio: {output_file}")
            
            return output_file, os.path.basename(output_file), content_type
                
        except Exception as e:
            logger.error(f"[{extraction_id}] Error extracting audio: {str(e)}")
            return None, None, None
    
    @staticmethod
    def get_video_info(url: str) -> Optional[Dict[str, Any]]:
        """Get basic information about a YouTube video."""
        try:
            logger.info(f"Getting video info for: {url}")
            
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'no_warnings': True,
                'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_data = ydl.extract_info(url, download=False)
                
                if not video_data:
                    return None
                
                info = {
                    "title": video_data.get("title", "Unknown title"),
                    "author": video_data.get("uploader", "Unknown uploader"),
                    "length_seconds": video_data.get("duration", 0),
                    "thumbnail_url": video_data.get("thumbnail", ""),
                    "youtube_id": video_data.get("id", ""),
                    "youtube_url": url,  # Include the original URL
                }
                
                logger.info(f"Successfully retrieved video info: {info['title']}")
                return info
                
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None
