# src/open_video_transcriber/gui/widgets.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QComboBox, QLabel, QFileDialog, 
    QProgressDialog, QMessageBox, QDialog, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from ..config import Config
from ..constants import VIDEO_FILTER
from ..core.model_manager import ModelManager
from .audio_visualization import AudioVisualizationWidget

from ..utils.logger import get_logger
logger = get_logger(__name__)

class ModelDownloadDialog(QDialog):
    def __init__(self, model_name: str, model_size: int, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.model_size = model_size
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Add information labels
        layout.addWidget(QLabel(f"Model: {self.model_name}"))
        layout.addWidget(QLabel(f"Size: {self.model_size} MB"))
        layout.addWidget(QLabel("This model needs to be downloaded for offline use."))
        
        # Add buttons
        button_layout = QHBoxLayout()
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(download_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setWindowTitle("Download Required")

class TranscriptionWidget(QWidget):
    transcribe_requested = pyqtSignal(str, str)  # video_path, model_name
    
    def __init__(self):
        super().__init__()
        self.model_manager = ModelManager()
        self.audio_path = None
        self.transcription = None
        self.init_ui()
        
    def init_ui(self):
        # Create layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        # Create widgets
        self.model_combo = QComboBox()
        self.update_model_combo()
        
        self.file_button = QPushButton("Open Video File")
        self.file_button.clicked.connect(self.open_file_dialog)
        
        self.download_button = QPushButton("Download Models")
        self.download_button.clicked.connect(self.manage_models)
        
        # Create a splitter for text output and audio visualization
        splitter = QSplitter(Qt.Vertical)
        
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        splitter.addWidget(self.text_output)
        
        self.audio_viz = AudioVisualizationWidget()
        self.audio_viz.seek_position.connect(self.highlight_text)
        self.audio_viz.playback_updated_position.connect(self.highlight_text)
        
        splitter.addWidget(self.audio_viz)
        
        # Add widgets to layouts
        button_layout.addWidget(QLabel("Model:"))
        button_layout.addWidget(self.model_combo)
        button_layout.addWidget(self.file_button)
        button_layout.addWidget(self.download_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
    
    def update_model_combo(self):
        """Update the model combo box with downloaded models."""
        self.model_combo.clear()
        for model in Config.AVAILABLE_MODELS:
            if self.model_manager.is_model_downloaded(model):
                self.model_combo.addItem(f"{model} (downloaded)", model)
            else:
                self.model_combo.addItem(f"{model} (not downloaded)", model)
    
    def manage_models(self):
        """Open dialog to manage model downloads."""
        msg = "Downloaded Models:\n"
        for model in self.model_manager.downloaded_models:
            size = self.model_manager.get_model_size(model)
            msg += f"- {model} ({size} MB)\n"
        
        msg += "\nAvailable Space: "
        msg += f"{self.model_manager.get_available_space()} MB"
        
        QMessageBox.information(self, "Model Management", msg)
    
    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", VIDEO_FILTER
        )
        if filename:
            model_name = self.model_combo.currentData()
            
            # Check if model is downloaded
            if not self.model_manager.is_model_downloaded(model_name):
                size = self.model_manager.get_model_size(model_name)
                dialog = ModelDownloadDialog(model_name, size, self)
                
                if dialog.exec_() == QDialog.Accepted:
                    progress = QProgressDialog("Downloading model...", "Cancel", 0, 0, self)
                    progress.setWindowModality(Qt.WindowModal)
                    progress.show()
                    
                    # Download model
                    if self.model_manager.download_model(model_name):
                        progress.close()
                        self.update_model_combo()
                        self.transcribe_requested.emit(filename, model_name)
                    else:
                        progress.close()
                        QMessageBox.critical(self, "Error", "Failed to download model")
            else:
                self.transcribe_requested.emit(filename, model_name)

    def set_text(self, text):
        self.text_output.setText(text)
        
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def set_transcription(self, transcription):
        self.transcription = transcription
        self.set_text(transcription["text"])
        if self.audio_path:
            self.audio_viz.load_audio(self.audio_path)
            self.audio_viz.set_transcription(transcription)
    
    def set_audio_path(self, audio_path):
        self.audio_path = audio_path
    
    def highlight_text(self, position):
        logger.info(f"highlight_text > position: {position}")
        if not self.transcription:
            return
        
        cursor = self.text_output.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow
        
        for segment in self.transcription['segments']:
            if segment['start'] <= position < segment['end']:
                start_pos = self.text_output.document().find(segment['text']).position()
                cursor.setPosition(start_pos)
                cursor.setPosition(start_pos + len(segment['text']), QTextCursor.KeepAnchor)
                cursor.setCharFormat(highlight_format)
                break