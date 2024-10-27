#!/usr/bin/env python3
"""
Entry point script for the Open Video Transcriber application.
This script should be placed in the root directory of the project.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from open_video_transcriber.main import main

if __name__ == "__main__":
    sys.exit(main())