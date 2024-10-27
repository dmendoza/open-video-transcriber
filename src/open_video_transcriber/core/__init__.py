"""
Core functionality for the Open Video Transcriber application.

This package contains the main business logic for audio extraction,
transcription, and model management.
"""

from .audio import AudioExtractor
from .transcription import Transcriber
from .model_manager import ModelManager

__all__ = [
    'AudioExtractor',
    'Transcriber',
    'ModelManager',
]