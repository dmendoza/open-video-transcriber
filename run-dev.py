#!/usr/bin/env python3
"""
Development script for the Open Video Transcriber application.
This script includes additional development tools and debugging.
"""

import sys
import logging
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def setup_debug_logging():
    """Setup debug logging for development."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Development entry point with additional debugging."""
    setup_debug_logging()
    
    # Import after setting up logging
    from open_video_transcriber.main import main as app_main
    
    logging.info("Starting application in development mode")
    try:
        return app_main()
    except Exception as e:
        logging.exception("Application error:")
        return 1

if __name__ == "__main__":
    sys.exit(main())