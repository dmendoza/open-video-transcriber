"""
Test suite for the Open Video Transcriber application.

This package contains all test cases and fixtures for testing
the application's functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path for testing
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))