"""
Configuration settings for the Open Video Transcriber application.

Attributes:
    APP_DIR (Path): The application directory.
    RESOURCES_DIR (Path): The directory for resource files.
    MODELS_DIR (Path): The directory for model files.
    TEMP_DIR (Path): The temporary directory for the application.
    DEFAULT_MODEL (str): The default model name.
    AVAILABLE_MODELS (List[str]): A list of available model names.
    MODEL_SIZES (Dict[str, int]): A dictionary mapping model names to their approximate file sizes in MB.
    WINDOW_TITLE (str): The title of the application window.
    WINDOW_WIDTH (int): The width of the application window.
    WINDOW_HEIGHT (int): The height of the application window.
"""
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
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large", "turbo"]
    
    # Model file sizes in MB (approximate)
    MODEL_SIZES: Dict[str, int] = {
        "tiny": 150,
        "base": 300,
        "small": 500,
        "medium": 1500,
        "large": 3000,
        "turbo": 3000
    }
    
    # GUI configuration
    WINDOW_TITLE = "Open Video Transcriber"
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    @classmethod
    def initialize(cls):
        """
        Initializes the necessary directories for the application.

        This method creates the following directories if they do not already exist:
        - TEMP_DIR: Temporary directory for intermediate files.
        - RESOURCES_DIR: Directory for resource files.
        - MODELS_DIR: Directory for model files.

        Directories are created with the `exist_ok=True` flag, meaning no error is raised if the directory already exists.
        """
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.RESOURCES_DIR, exist_ok=True)
        os.makedirs(cls.MODELS_DIR, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str) -> Path:
        """
        Get the full path to a model file.

        Args:
            model_name (str): The name of the model file.

        Returns:
            Path: The full path to the model file within the models directory.
        """
        return cls.MODELS_DIR / model_name