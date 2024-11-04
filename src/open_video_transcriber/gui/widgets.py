"""
This module contains the GUI widgets for the Open Video Transcriber application.
Classes:
    ModelDownloadDialog(QDialog): A dialog for downloading models required for offline use.
    TranscriptionWidget(QWidget): The main widget for handling video transcription.

Signals:
    TranscriptionWidget.transcribe_requested(str, str): Emitted when a transcription is requested, with video path and model name as arguments.
"""
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
        """
        Initializes the widget with the specified model name and size.
        Args:
            model_name (str): The name of the model.
            model_size (int): The size of the model.
            parent (optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.model_name = model_name
        self.model_size = model_size
        self.init_ui()
        
    def init_ui(self):
        """
        Initializes the user interface for the widget.
        This method sets up the layout and widgets for the UI, including:
        - Information labels displaying the model name and size.
        - A message indicating that the model needs to be downloaded for offline use.
        - Download and Cancel buttons with their respective click event handlers.
        The layout is set to a vertical box layout (QVBoxLayout) with a horizontal box layout (QHBoxLayout) for the buttons.
        The window title is set to "Download Required".
        """
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
        """
        Initializes the widget.
        This constructor sets up the widget by calling the parent constructor,
        initializing the model manager, and setting up the initial state for
        audio path and transcription. It also initializes the user interface.

        Attributes:
            model_manager (ModelManager): An instance of the ModelManager class.
            audio_path (str or None): The path to the audio file, initially set to None.
            transcription (str or None): The transcription of the audio file, initially set to None.
        """
        super().__init__()
        self.model_manager = ModelManager()
        self.audio_path = None
        self.transcription = None
        self.init_ui()
        
    def init_ui(self):
        """
        Initializes the user interface for the widget.
        This method sets up the main layout and button layout, creates and configures
        various widgets including combo boxes, buttons, text edit, and audio visualization
        widget. It also connects signals to their respective slots for handling user
        interactions.
        Widgets created:
        - QComboBox for model selection
        - QPushButton for opening video files
        - QPushButton for downloading models
        - QTextEdit for displaying text output
        - AudioVisualizationWidget for visualizing audio and handling playback
        Layouts created:
        - QVBoxLayout for the main layout
        - QHBoxLayout for the button layout
        - QSplitter for splitting text output and audio visualization
        Signals connected:
        - QPushButton.clicked to open_file_dialog and manage_models
        - AudioVisualizationWidget.seek_position to highlight_text
        - AudioVisualizationWidget.playback_updated_position to highlight_text
        """
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
        """
        Update the model combo box with the list of available models.
        This method clears the current items in the model combo box and repopulates
        it with the models listed in `Config.AVAILABLE_MODELS`. Each model is checked
        to determine if it has been downloaded using the `is_model_downloaded` method
        of `model_manager`. The combo box items are labeled accordingly to indicate
        whether each model is downloaded or not.
        Returns:
            None
        """
        self.model_combo.clear()
        for model in Config.AVAILABLE_MODELS:
            if self.model_manager.is_model_downloaded(model):
                self.model_combo.addItem(f"{model} (downloaded)", model)
            else:
                self.model_combo.addItem(f"{model} (not downloaded)", model)
    
    def manage_models(self):
        """
        Displays a message box with information about the downloaded models and available disk space.
        The message box contains:
        - A list of downloaded models with their respective sizes.
        - The available disk space in megabytes.
        This method retrieves the list of downloaded models and their sizes from the model manager,
        and also gets the available disk space from the model manager.
        """
        msg = "Downloaded Models:\n"
        for model in self.model_manager.downloaded_models:
            size = self.model_manager.get_model_size(model)
            msg += f"- {model} ({size} MB)\n"
        
        msg += "\nAvailable Space: "
        msg += f"{self.model_manager.get_available_space()} MB"
        
        QMessageBox.information(self, "Model Management", msg)
    
    def open_file_dialog(self):
        """
        Opens a file dialog for the user to select a video file. If a file is selected,
        it checks if the required model is downloaded. If the model is not downloaded,
        it prompts the user to download the model and shows a progress dialog during
        the download. Once the model is downloaded, or if it was already downloaded,
        it emits a signal to request transcription of the selected video file.

        Signals:
            transcribe_requested (str, str): Emitted when a video file is selected and
                             the required model is available, with the
                             filename and model name as arguments.
        """

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
        """
        Sets the given text to the text_output widget.

        Args:
            text (str): The text to be set in the text_output widget.
        """
        self.text_output.setText(text)
        
    def show_error(self, message):
        """
        Displays an error message in a critical message box.

        Args:
            message (str): The error message to be displayed.
        """
        QMessageBox.critical(self, "Error", message)

    def set_transcription(self, transcription):
        """
        Sets the transcription for the widget and updates the text and audio visualization.

        Args:
            transcription (dict): A dictionary containing the transcription data. 
                                  It should have a key "text" with the transcription text.
        """
        self.transcription = transcription
        self.set_text(transcription["text"])
        if self.audio_path:
            self.audio_viz.load_audio(self.audio_path)
            self.audio_viz.set_transcription(transcription)
    
    def set_audio_path(self, audio_path):
        """
        Sets the path to the audio file.

        Args:
            audio_path (str): The file path to the audio file.
        """
        self.audio_path = audio_path
    
    def highlight_text(self, position):
        """
        Highlights the text in the text_output widget based on the given position.
        This method highlights the segment of text in the text_output widget that corresponds
        to the given position within the transcription. The highlighted text is marked with
        a light yellow background.

        Args:
            position (int): The position within the transcription to highlight.
        """
        # logger.info(f"highlight_text > position: {position}")
        if not self.transcription:
            return
        
        cursor = self.text_output.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow
        
        for segment in self.transcription['segments']:
            # logger.info(f"highlight_text > segment: {segment}")
            if segment['start'] <= position < segment['end']:
                segment_text = segment['text']
                start_pos = self.text_output.document().find(segment_text).position()
                # logger.info(f"highlight_text > segment_text: {segment_text}")
                # logger.info(f"highlight_text > start_pos: {start_pos}")
                # logger.info(f"highlight_text > len(segment_text): {len(segment_text)}")
                cursor.setPosition(start_pos - len(segment_text))
                cursor.setPosition(start_pos, QTextCursor.KeepAnchor)
                cursor.setCharFormat(highlight_format)
                break