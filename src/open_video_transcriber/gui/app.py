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
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, video_path: str, model_name: str):
        super().__init__()
        self.video_path = Path(video_path)
        self.model_name = model_name
        
    def run(self):
        try:
            # Extract audio
            audio_extractor = AudioExtractor()
            audio_path = audio_extractor.extract_audio(self.video_path)
            
            # Transcribe
            transcriber = Transcriber(self.model_name)
            result = transcriber.transcribe(audio_path)
            
            # Clean up
            audio_path.unlink()
            
            self.finished.emit(result["text"])
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
        self.thread.finished.connect(self.transcription_widget.set_text)
        self.thread.error.connect(self.transcription_widget.show_error)
        self.thread.start()