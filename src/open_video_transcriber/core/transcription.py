
"""
This module provides the Transcriber class for transcribing audio files using the Whisper model.

Classes:
    Transcriber: A class to handle the transcription of audio files using a specified Whisper model.
"""
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
        Initializes the Transcription class with a specified model name.

        Args:
            model_name (str): The name of the model to be used for transcription. Defaults to Config.DEFAULT_MODEL.

        Attributes:
            model_name (str): The name of the model to be used for transcription.
            model (Optional[whisper.Whisper]): The Whisper model instance, initialized as None.
            model_manager (ModelManager): An instance of the ModelManager class to manage model-related operations.
        """
        self.model_name = model_name
        self.model: Optional[whisper.Whisper] = None
        self.model_manager = ModelManager()
    
    def ensure_model(self) -> bool:
        """
        Ensures that the required model is downloaded.

        This method checks if the model specified by `self.model_name` is already
        downloaded using the `is_model_downloaded` method of `self.model_manager`.
        If the model is not downloaded, it attempts to download the model using
        the `download_model` method of `self.model_manager`.

        Returns:
            bool: True if the model is already downloaded or successfully downloaded,
                  False otherwise.
        """
        if not self.model_manager.is_model_downloaded(self.model_name):
            return self.model_manager.download_model(self.model_name)
        return True
    
    def load_model(self):
        """
        Loads the Whisper model if it is not already loaded.
        This method checks if the model is already loaded. If not, it ensures the model is available
        by calling `ensure_model()`. If the model cannot be ensured, it raises a RuntimeError.
        Once the model is ensured, it loads the Whisper model using the model name and updates
        the `self.model` attribute.

        Raises:
            RuntimeError: If the model cannot be ensured.
        """
        if self.model is None:
            if not self.ensure_model():
                raise RuntimeError(f"Failed to ensure model {self.model_name}")
                
            logger.info(f"Loading Whisper model: {self.model_name}")
            model_path = Config.get_model_path(self.model_name)
            self.model = whisper.load_model(self.model_name)
    
    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribes the given audio file using the loaded model.

        Args:
            audio_path (Path): The path to the audio file to be transcribed.

        Returns:
            Dict[str, Any]: The transcription result.

        Raises:
            Exception: If an error occurs during transcription.
        """
        try:
            self.load_model()
            logger.info(f"Transcribing audio file: {audio_path}")
            result = self.model.transcribe(str(audio_path))
            return result
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise