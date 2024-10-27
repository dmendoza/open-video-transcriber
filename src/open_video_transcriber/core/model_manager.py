# src/open_video_transcriber/core/model_manager.py
import whisper
import torch
from pathlib import Path
import os
import shutil
from typing import Optional, List
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ModelManager:
    def __init__(self):
        self.models_dir = Config.MODELS_DIR
        self.downloaded_models: List[str] = []
        self._check_downloaded_models()

    def _check_downloaded_models(self):
        """Check which models are already downloaded."""
        self.downloaded_models = []
        for model_name in Config.AVAILABLE_MODELS:
            model_path = Config.get_model_path(model_name)
            if model_path.exists():
                self.downloaded_models.append(model_name)
        logger.info(f"Found downloaded models: {self.downloaded_models}")

    def download_model(self, model_name: str) -> bool:
        """
        Download a specific Whisper model.
        
        Args:
            model_name: Name of the model to download
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if model_name not in Config.AVAILABLE_MODELS:
                raise ValueError(f"Invalid model name: {model_name}")

            model_path = Config.get_model_path(model_name)
            logger.info(f"Whisper's model path {model_path}")
            if model_path.exists():
                logger.info(f"Model {model_name} already downloaded")
                return True

            # Download model using whisper's download function
            logger.info(f"Downloading model {model_name}")
            whisper.load_model(model_name)
            
            # Move the model from whisper's cache to our app directory
            # cache_dir = Path(torch.hub.get_dir()) / "whisper"
            cache_dir = Path(os.path.join(os.path.expanduser("~"), ".cache")) / "whisper"
            logger.info(f"Whisper's model cache dir {cache_dir}")

            src_path = next(cache_dir.glob(f"*{model_name}*.pt"))
            shutil.copy2(src_path, model_path)
            
            self.downloaded_models.append(model_name)
            logger.info(f"Successfully downloaded model {model_name}")
            return True

        except Exception as e:
            logger.exception(f"Error downloading model {model_name}: {e}")
            return False

    def get_model_size(self, model_name: str) -> int:
        """Get the size of a model in MB."""
        return Config.MODEL_SIZES.get(model_name, 0)

    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if a specific model is downloaded."""
        return model_name in self.downloaded_models

    def get_available_space(self) -> int:
        """Get available disk space in MB."""
        if os.name == 'nt':  # Windows
            free_bytes = shutil.disk_usage(self.models_dir).free
        else:  # Unix-like
            st = os.statvfs(self.models_dir)
            free_bytes = st.f_frsize * st.f_bavail
        return free_bytes // (1024 * 1024)  # Convert to MB