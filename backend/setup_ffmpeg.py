"""
Setup script to download and configure FFmpeg for MP3 conversion support.
"""
import os
import platform
import subprocess
import sys
import zipfile
import tempfile
from pathlib import Path

def download_file(url, output_path):
    """Download a file from a URL to the specified output path."""
    import requests
    print(f"Downloading {url} to {output_path}...")
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        
        # Show progress during download
        downloaded = 0
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = int(100 * downloaded / total_size) if total_size > 0 else 0
                    sys.stdout.write(f"\rProgress: {percent}% ({downloaded/1024/1024:.1f} MB)")
                    sys.stdout.flush()
        
        print("\nDownload complete!")

def setup_ffmpeg():
    """Download and set up FFmpeg for the local development environment."""
    if platform.system() != "Windows":
        print("This script is intended for Windows. On Linux or Mac, install FFmpeg through your package manager.")
        print("For Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("For MacOS: brew install ffmpeg")
        return
    
    print("\n===== FFmpeg Setup Utility =====")
    print("This utility will download FFmpeg for MP3 conversion support.")
    print("\nNote: This will download approximately 30-100 MB of data.")
    
    confirm = input("\nDo you want to proceed with downloading FFmpeg? (y/n): ")
    if confirm.lower() not in ['y', 'yes']:
        print("Setup cancelled. The application will use native audio formats instead of MP3.")
        return
    
    print("\nSetting up FFmpeg...")
    bin_dir = Path(__file__).parent / "bin"
    bin_dir.mkdir(exist_ok=True)
    
    ffmpeg_exe = bin_dir / "ffmpeg.exe"
    ffprobe_exe = bin_dir / "ffprobe.exe"
    
    if ffmpeg_exe.exists() and ffprobe_exe.exists():
        print(f"FFmpeg already installed at {bin_dir}")
        return
    
    # Use the most reliable URL
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        try:
            # Download FFmpeg
            download_file(ffmpeg_url, zip_path)
            
            # Extract FFmpeg
            print(f"Extracting FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the ffmpeg.exe and ffprobe.exe
            print("Locating FFmpeg executables...")
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower() == "ffmpeg.exe":
                        src_path = os.path.join(root, file)
                        print(f"Copying {src_path} to {ffmpeg_exe}")
                        Path(src_path).replace(ffmpeg_exe)
                    elif file.lower() == "ffprobe.exe":
                        src_path = os.path.join(root, file)
                        print(f"Copying {src_path} to {ffprobe_exe}")
                        Path(src_path).replace(ffprobe_exe)
        
        except Exception as e:
            print(f"Error during FFmpeg installation: {str(e)}")
            print("Please download FFmpeg manually from https://ffmpeg.org/download.html")
            return
    
    # Verify installation
    if ffmpeg_exe.exists() and ffprobe_exe.exists():
        print("\nFFmpeg installation successful!")
        print(f"FFmpeg binaries located at: {bin_dir}")
        
        # Add to PATH for the current session
        os.environ["PATH"] = f"{bin_dir};{os.environ['PATH']}"
        print("FFmpeg added to PATH for current session")
        
        # Test FFmpeg
        try:
            result = subprocess.run([str(ffmpeg_exe), "-version"], 
                                   capture_output=True, text=True, check=True)
            print(f"FFmpeg version: {result.stdout.splitlines()[0]}")
        except Exception as e:
            print(f"Warning: FFmpeg test failed: {e}")
    else:
        print("\nFFmpeg installation failed. Please install FFmpeg manually.")

if __name__ == "__main__":
    setup_ffmpeg()
    print("\nSetup complete! You can now convert YouTube videos to MP3.")
