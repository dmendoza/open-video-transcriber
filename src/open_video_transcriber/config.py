# src/open_video_transcriber/config.py
import os
from pathlib import Path
from typing import Dict

class Config:
    # Application paths
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    RESOURCES_DIR = APP_DIR / "resources"
    MODELS_DIR = RESOURCES_DIR / "models"
    TEMP_DIR = Path(os.getenv("TEMP", "/tmp")) / "open_video_transcriber"
    
    # Whisper configuration
    DEFAULT_MODEL = "base"
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]
    
    # Model file sizes in MB (approximate)
    MODEL_SIZES: Dict[str, int] = {
        "tiny": 150,
        "base": 300,
        "small": 500,
        "medium": 1500,
        "large": 3000
    }
    
    # GUI configuration
    WINDOW_TITLE = "Open Video Transcriber"
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    @classmethod
    def initialize(cls):
        """Initialize necessary directories."""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.RESOURCES_DIR, exist_ok=True)
        os.makedirs(cls.MODELS_DIR, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Path:
        """Get the path for a specific model."""
        return cls.MODELS_DIR / model_name