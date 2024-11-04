"""
This module provides the ModelManager class, which handles the downloading and management of Whisper models.

Classes:
    ModelManager: Manages the downloading, checking, and storage of Whisper models.
"""
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
        """
        Initializes the ModelManager instance.
        
        Attributes:
            models_dir (str): The directory where models are stored.
            downloaded_models (List[str]): A list to keep track of downloaded models.
        """
        self.models_dir = Config.MODELS_DIR
        self.downloaded_models: List[str] = []
        self._check_downloaded_models()

    def _check_downloaded_models(self):
        """
        Checks for downloaded models and updates the downloaded_models attribute.
        This method iterates over the available models defined in the Config class,
        checks if the model files exist in the specified paths, and appends the names
        of the downloaded models to the downloaded_models attribute. It also logs
        the names of the found downloaded models.

        Returns:
            None
        """
        self.downloaded_models = []
        for model_name in Config.AVAILABLE_MODELS:
            model_path = Config.get_model_path(model_name)
            if model_path.exists():
                self.downloaded_models.append(model_name)
        logger.info(f"Found downloaded models: {self.downloaded_models}")

    def download_model(self, model_name: str) -> bool:
        """
        Downloads a specified model if it is not already downloaded.
        This method checks if the given model name is valid and available in the configuration.
        If the model is already downloaded, it logs the information and returns True.
        Otherwise, it downloads the model using Whisper's download function, moves it from
        Whisper's cache to the application's directory, and logs the process.

        Args:
            model_name (str): The name of the model to be downloaded.
        Returns:
            bool: True if the model is successfully downloaded or already exists, False otherwise.
        Raises:
            ValueError: If the model name is not valid or not available in the configuration.
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
        """
        Get the size of a model in megabytes (MB).
        
        Args:
            model_name (str): The name of the model.
        Returns:
            int: The size of the model in MB. Returns 0 if the model name is not found.
        """
        return Config.MODEL_SIZES.get(model_name, 0)

    def is_model_downloaded(self, model_name: str) -> bool:
        """
        Check if a specific model is downloaded.
        
        Args:
            model_name (str): The name of the model to check.
        Returns:
            bool: True if the model is downloaded, False otherwise.
        """
        return model_name in self.downloaded_models

    def get_available_space(self) -> int:
        """
        Get the available disk space in the directory specified by `self.models_dir`.

        Returns:
            int: The available disk space in megabytes (MB).
        """
        if os.name == 'nt':  # Windows
            free_bytes = shutil.disk_usage(self.models_dir).free
        else:  # Unix-like
            st = os.statvfs(self.models_dir)
            free_bytes = st.f_frsize * st.f_bavail
        return free_bytes // (1024 * 1024)  # Convert to MB