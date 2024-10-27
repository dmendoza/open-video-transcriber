# src/open_video_transcriber/core/transcription.py
import whisper
import torch
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..config import Config
from .model_manager import ModelManager

logger = get_logger(__name__)

class Transcriber:
    def __init__(self, model_name: str = Config.DEFAULT_MODEL):
        """
        Initialize the transcriber with a specific model.
        
        Args:
            model_name (str): Name of the Whisper model to use
        """
        self.model_name = model_name
        self.model: Optional[whisper.Whisper] = None
        self.model_manager = ModelManager()
    
    def ensure_model(self) -> bool:
        """
        Ensure the model is downloaded and available.
        
        Returns:
            bool: True if model is ready, False otherwise
        """
        if not self.model_manager.is_model_downloaded(self.model_name):
            return self.model_manager.download_model(self.model_name)
        return True
    
    def load_model(self):
        """Load the Whisper model if not already loaded."""
        if self.model is None:
            if not self.ensure_model():
                raise RuntimeError(f"Failed to ensure model {self.model_name}")
                
            logger.info(f"Loading Whisper model: {self.model_name}")
            model_path = Config.get_model_path(self.model_name)
            self.model = whisper.load_model(self.model_name)
    
    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path (Path): Path to the audio file
            
        Returns:
            Dict[str, Any]: Transcription results
        """
        try:
            self.load_model()
            logger.info(f"Transcribing audio file: {audio_path}")
            result = self.model.transcribe(str(audio_path))
            return result
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise