"""
Utility script to ensure yt-dlp is properly installed 
and has necessary dependencies during build time.
"""
import subprocess
import sys
import platform
import os

def install_yt_dlp():
    """Install yt-dlp with appropriate dependencies."""
    try:
        # Install yt-dlp
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp==2023.11.16"])
        print("✅ yt-dlp successfully installed")
        
        # Check if FFmpeg is available
        try:
            if platform.system() == "Windows":
                # For Windows, add FFmpeg to PATH using a portable version
                ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
                if not os.path.exists(ffmpeg_path):
                    os.makedirs(ffmpeg_path, exist_ok=True)
                
                # Download portable FFmpeg if not already present
                ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
                if not os.path.exists(ffmpeg_exe):
                    print("⚙️ FFmpeg not found, attempting to download portable version...")
                    import requests
                    
                    # URL for a small portable FFmpeg (example URL, may need updating)
                    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                    
                    zip_path = os.path.join(ffmpeg_path, "ffmpeg.zip")
                    with requests.get(ffmpeg_url, stream=True) as r:
                        r.raise_for_status()
                        with open(zip_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    # Extract the zip file
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(ffmpeg_path)
                    
                    # Update PATH environment variable
                    os.environ["PATH"] += os.pathsep + ffmpeg_path
                    print(f"✅ FFmpeg downloaded and added to PATH: {ffmpeg_path}")
                else:
                    print(f"✅ FFmpeg already exists at: {ffmpeg_exe}")
                    os.environ["PATH"] += os.pathsep + ffmpeg_path
            
            elif platform.system() == "Linux":
                # For Linux, install using apt-get or similar
                subprocess.check_call(["apt-get", "update"])
                subprocess.check_call(["apt-get", "install", "-y", "ffmpeg"])
                print("✅ FFmpeg installed on Linux")
        
        except Exception as e:
            print(f"⚠️ Warning: FFmpeg may not be available: {str(e)}")
            print("⚠️ Some audio extraction features may not work correctly.")
        
        # Test yt-dlp Python API
        import yt_dlp
        print(f"✅ yt-dlp Python library is available (version: {yt_dlp.version.__version__})")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    install_yt_dlp()
