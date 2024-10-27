"""
Open Video Transcriber
==================

A desktop application for transcribing video files using OpenAI's Whisper model.
"""

__version__ = "0.1.0"
__author__ = "Diego E. Mendoza"
__email__ = "diego.e.mendoza@gmail.com"

from .config import Config
from .constants import *

# Initialize configuration when the package is imported
Config.initialize()