# src/open_video_transcriber/main.py
import sys
from PyQt5.QtWidgets import QApplication
from .gui.app import MainWindow
from .config import Config
from .utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main entry point for the application."""
    try:
        # Initialize configuration
        Config.initialize()
        
        # Create and start the application
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()