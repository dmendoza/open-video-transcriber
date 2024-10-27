# src/open_video_transcriber/gui/widgets.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QComboBox, QLabel, QFileDialog, 
    QProgressDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ..config import Config
from ..constants import VIDEO_FILTER

class TranscriptionWidget(QWidget):
    transcribe_requested = pyqtSignal(str, str)  # video_path, model_name
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Create layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        # Create widgets
        self.model_combo = QComboBox()
        self.model_combo.addItems(Config.AVAILABLE_MODELS)
        self.model_combo.setCurrentText(Config.DEFAULT_MODEL)
        
        self.file_button = QPushButton("Open Video File")
        self.file_button.clicked.connect(self.open_file_dialog)
        
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        
        # Add widgets to layouts
        button_layout.addWidget(QLabel("Model:"))
        button_layout.addWidget(self.model_combo)
        button_layout.addWidget(self.file_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.text_output)
        
        self.setLayout(main_layout)
        
    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", VIDEO_FILTER
        )
        if filename:
            self.transcribe_requested.emit(filename, self.model_combo.currentText())
            
    def set_text(self, text):
        self.text_output.setText(text)
        
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)