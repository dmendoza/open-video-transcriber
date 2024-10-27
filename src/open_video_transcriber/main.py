"""
Main entry point for the Open Video Transcriber application.
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
    """Initialize the application configuration and logging."""
    try:
        # Initialize configuration
        Config.initialize()
        
        # Log application start
        logger.info("Initializing Whisper Transcriber")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

def main():
    """Main entry point for the application."""
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