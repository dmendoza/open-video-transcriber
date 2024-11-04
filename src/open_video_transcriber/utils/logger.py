"""
This module provides a utility function to create and configure a logger.
Functions:
    get_logger(name: str) -> logging.Logger:
        Create a logger with the given name. The logger will have both console and file handlers.
        The console handler outputs logs to stdout with INFO level, while the file handler outputs
        logs to a file with DEBUG level.
"""
import logging
import sys
from pathlib import Path
from ..config import Config

def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a logger with the specified name.
    This function sets up a logger that outputs log messages to both the console
    and a file. The console handler logs messages at the INFO level, while the 
    file handler logs messages at the DEBUG level. The log messages are formatted 
    to include the timestamp, logger name, log level, and message.
    
    Args:
        name (str): The name of the logger.
    Returns:
        logging.Logger: Configured logger instance.
    """

    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Config.TEMP_DIR / "open_video_transcriber.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger