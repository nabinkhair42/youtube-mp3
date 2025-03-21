import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Define log levels
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    """Set up application logging."""
    # In serverless, we shouldn't try to write to the filesystem
    is_vercel = os.environ.get("VERCEL", "0") == "1"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates when reloading in dev
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Create console handler (always needed)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # Only add file handler in non-serverless environment
    if not is_vercel:
        try:
            log_dir = Path(__file__).parents[3] / "logs"
            log_dir.mkdir(exist_ok=True)
            
            # Create a unique log file name with date
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"app_{today}.log"
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging initialized. Log file: {log_file}")
        except Exception as e:
            root_logger.warning(f"Could not set up file logging: {str(e)}")
    
    root_logger.info("Logging initialized")
    return root_logger

def get_logger(name):
    """Get a logger with the specified name."""
    return logging.getLogger(name)
