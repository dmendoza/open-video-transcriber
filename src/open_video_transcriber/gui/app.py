
from PyQt5.QtWidgets import QMainWindow, QApplication
"""
This module contains the main application logic for the Open Video Transcriber GUI.
Classes:
    TranscriptionThread(QThread): A QThread subclass that handles the extraction of audio from a video file and its transcription.
    MainWindow(QMainWindow): The main window of the application, which initializes the UI and handles user interactions.
Signals:
    TranscriptionThread.finished(dict): Emitted when the transcription process is finished, with the transcription result as a dictionary.
    TranscriptionThread.error(str): Emitted when an error occurs during the transcription process, with the error message as a string.
"""
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
from ..config import Config
from ..core.audio import AudioExtractor
from ..core.transcription import Transcriber
from ..utils.logger import get_logger
from .widgets import TranscriptionWidget
from ..constants import MSG_TRANSCRIBING, MSG_ERROR

logger = get_logger(__name__)

class TranscriptionThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, video_path: str, model_name: str):
        """
        Initialize the application with the given video path and model name.
        Args:
            video_path (str): The path to the video file.
            model_name (str): The name of the model to be used.
        """
        super().__init__()
        self.video_path = Path(video_path)
        self.model_name = model_name
        self.audio_path = None  # Initialize audio_path attribute
        
    def run(self):
        """
        Runs the transcription process.
        This method performs the following steps:
        1. Extracts audio from the video file specified by `self.video_path`.
        2. Transcribes the extracted audio using the model specified by `self.model_name`.
        3. Emits the transcription result via the `finished` signal.
        4. Handles any exceptions that occur during the process and emits an error message via the `error` signal.
        
        Attributes:
            self.video_path (str): Path to the video file.
            self.model_name (str): Name of the transcription model to use.
            self.audio_path (str): Path to the extracted audio file.
        Emits:
            finished (str): Signal emitted with the transcription result.
            error (str): Signal emitted with the error message if an exception occurs.
        """
        try:
            # Extract audio
            audio_extractor = AudioExtractor()
            self.audio_path = audio_extractor.extract_audio(self.video_path)
            
            # Transcribe
            transcriber = Transcriber(self.model_name)
            result = transcriber.transcribe(self.audio_path)
            logger.info(f"Transcription result: {result}")
            
            # Clean up
            # self.audio_path.unlink()
            # self.finished.emit(result["text"])
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Error in transcription thread: {e}")
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the application by calling the parent class initializer and setting up the user interface.
        """
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """
        Initializes the user interface for the application.
        This method sets the window title and geometry using the configuration
        settings. It also creates an instance of the TranscriptionWidget, connects
        its transcribe_requested signal to the start_transcription method, and sets
        it as the central widget of the main window.
        """
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        self.transcription_widget = TranscriptionWidget()
        self.transcription_widget.transcribe_requested.connect(self.start_transcription)
        self.setCentralWidget(self.transcription_widget)
        
    def start_transcription(self, video_path: str, model_name: str):
        """
        Starts the transcription process for a given video file using the specified model.

        Args:
            video_path (str): The file path to the video that needs to be transcribed.
            model_name (str): The name of the transcription model to be used.
        """
        self.thread = TranscriptionThread(video_path, model_name)
        self.thread.finished.connect(self.on_transcription_finished)
        self.thread.error.connect(self.transcription_widget.show_error)
        self.thread.start()
        
    def on_transcription_finished(self, result):
        """
        Callback function that is called when the transcription process is finished.
        This function updates the transcription widget with the audio path and the transcription result.

        Args:
            result (str): The transcription result obtained from the transcription process.
        """
        self.transcription_widget.set_audio_path(self.thread.audio_path)
        self.transcription_widget.set_transcription(result)