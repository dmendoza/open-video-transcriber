"""
Graphical User Interface components for the Open Video Transcriber application.

This package contains all GUI-related components including the main window,
widgets, and dialog boxes.
"""

from .app import MainWindow
from .widgets import TranscriptionWidget, ModelDownloadDialog

__all__ = [
    'MainWindow',
    'TranscriptionWidget',
    'ModelDownloadDialog',
]