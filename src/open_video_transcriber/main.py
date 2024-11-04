"""
This module serves as the main entry point for the Open Video Transcriber application.
It initializes the application configuration and logging, creates the Qt application,
and starts the main event loop.

Usage:
    Run this module directly to start the Open Video Transcriber application.
"""
import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from .gui.app import MainWindow
from .config import Config
from .utils.logger import get_logger

logger = get_logger(__name__)

def init_application():
    """
    Initializes the application by setting up the configuration and logging the start of the Whisper Transcriber.
    This function performs the following steps:
    1. Initializes the configuration using the Config class.
    2. Logs the start of the Whisper Transcriber.
    If an exception occurs during initialization, it logs the error and raises the exception.

    Raises:
        Exception: If an error occurs during initialization.
    """
    try:
        # Initialize configuration
        Config.initialize()
        
        # Log application start
        logger.info("Initializing Whisper Transcriber")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

def main():
    """
    Main entry point for the application.
    This function initializes the application, creates the Qt application and main window,
    and starts the event loop. If an exception occurs during execution, it logs the error
    and returns a non-zero exit code.
    
    Returns:
        int: The exit code of the application. Returns 0 if the application exits normally,
             or 1 if an exception occurs.
    """
    try:
        # Initialize application
        init_application()
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Create and show main window
        logger.info("Creating main window")
        window = MainWindow()
        window.show()
        
        # Start event loop
        logger.info("Starting application event loop")
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())