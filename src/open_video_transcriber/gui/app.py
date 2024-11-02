# src/open_video_transcriber/gui/app.py
from PyQt5.QtWidgets import QMainWindow, QApplication
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
        super().__init__()
        self.video_path = Path(video_path)
        self.model_name = model_name
        self.audio_path = None  # Initialize audio_path attribute
        
    def run(self):
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
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        self.transcription_widget = TranscriptionWidget()
        self.transcription_widget.transcribe_requested.connect(self.start_transcription)
        self.setCentralWidget(self.transcription_widget)
        
    def start_transcription(self, video_path: str, model_name: str):
        self.thread = TranscriptionThread(video_path, model_name)
        self.thread.finished.connect(self.on_transcription_finished)
        self.thread.error.connect(self.transcription_widget.show_error)
        self.thread.start()
        
    def on_transcription_finished(self, result):
        self.transcription_widget.set_audio_path(self.thread.audio_path)
        self.transcription_widget.set_transcription(result)