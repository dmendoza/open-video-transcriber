# src/open_video_transcriber/config.py
import os
from pathlib import Path

class Config:
    # Application paths
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    RESOURCES_DIR = APP_DIR / "resources"
    TEMP_DIR = Path(os.getenv("TEMP", "/tmp")) / "open_video_transcriber"
    
    # Whisper configuration
    DEFAULT_MODEL = "base"
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]
    
    # GUI configuration
    WINDOW_TITLE = "Open Video Transcriber"
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    # Initialize necessary directories
    @classmethod
    def initialize(cls):
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.RESOURCES_DIR, exist_ok=True)
