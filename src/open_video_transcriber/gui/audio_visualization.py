import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import librosa

from ..utils.logger import get_logger
logger = get_logger(__name__)

class AudioVisualizationWidget(QWidget):
    seek_position = pyqtSignal(float)  # Signal to emit seek position
    playback_updated_position = pyqtSignal(float)  # Signal to emit current position during playback

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.transcription = None
        self.current_time = 0
        self.segment_lines = []
        self.current_segment_highlight = None
        self.ax = None  # Store reference to the axes
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Create matplotlib Figure and Canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        
        # Control layout
        control_layout = QHBoxLayout()
        
        # Add play/pause button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_button)
        
        # Add slider for seeking
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.slider_seek)
        control_layout.addWidget(self.slider)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
        # Setup media player
        self.media_player = QMediaPlayer()
        self.media_player.positionChanged.connect(self.update_position)
        
        # Setup timer for updating position
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Update every 100 ms
        self.timer.timeout.connect(self.update_highlight)

    def load_audio(self, audio_path):
        """Load audio file and initialize the visualization."""
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None)
        self.plot_audio()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(audio_path))))

    def set_transcription(self, transcription):
        """Set transcription data and update the visualization."""
        self.transcription = transcription
        self.plot_audio()

    def plot_audio(self):
        """Plot the audio waveform and initialize visualization elements."""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        if self.audio_data is not None:
            # Plot waveform
            times = np.linspace(0, len(self.audio_data) / self.sample_rate, num=len(self.audio_data))
            self.ax.plot(times, self.audio_data, color='blue', alpha=0.5)
            
            # Set labels and title
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Amplitude')
            
            if self.transcription:
                # Plot segment markers
                self.segment_lines = []
                for segment in self.transcription['segments']:
                    # Add vertical lines at segment boundaries
                    line = self.ax.axvline(x=segment['start'], color='r', linestyle='--', alpha=0.3)
                    self.segment_lines.append(line)
                    
                    # Add text labels
                    self.ax.text(segment['start'], self.ax.get_ylim()[1], 
                               segment['text'][:20] + '...' if len(segment['text']) > 20 else segment['text'],
                               rotation=45, verticalalignment='bottom', fontsize=8)
                
                # Initialize the highlight patch
                if self.current_segment_highlight is None:
                    self.current_segment_highlight = self.ax.axvspan(0, 0, color='yellow', alpha=0.2)
            
            # Adjust layout to prevent text cutoff
            self.figure.tight_layout()
            
        self.canvas.draw()

    def update_highlight(self):
        """Update the position of the highlight based on current time."""
        if self.transcription and self.current_segment_highlight:
            current_segment = self.find_current_segment()
            if current_segment:
                start = current_segment['start']
                end = current_segment['end']
                # Remove previous highlight
                if self.current_segment_highlight in self.ax.patches:
                    self.current_segment_highlight.remove()
                # Create new highlight
                self.current_segment_highlight = self.ax.axvspan(start, end, 
                                                               color='yellow', 
                                                               alpha=0.2)
                self.canvas.draw_idle()  # More efficient than full draw()

    def find_current_segment(self):
        """Find the segment corresponding to the current playback time."""
        if not self.transcription:
            return None
            
        for segment in self.transcription['segments']:
            if segment['start'] <= self.current_time <= segment['end']:
                return segment
        return None

    def slider_seek(self, value):
        """Handle seeking in the audio file when user use the slider."""
        logger.info(f"seek > value: {value}")
        if self.audio_data is not None:
            duration = len(self.audio_data) / self.sample_rate
            slider_seek_position = (value / 100.0) * duration
            logger.info(f"seek > slider_seek_position: {slider_seek_position}")
            self.media_player.setPosition(int(slider_seek_position))  # Convert to milliseconds
            self.seek_position.emit(slider_seek_position)

    def update_position(self, position):
        """Update the current position during playback."""
        logger.info(f"update_position > Position: {position}")
        self.current_time = position / 1000.0  # Convert from milliseconds to seconds
        if self.audio_data is not None:
            duration = len(self.audio_data) / self.sample_rate
            value = int((self.current_time / duration) * 100)
            self.playback_updated_position.emit(self.current_time) # Convert to milliseconds
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def toggle_play(self):
        """Toggle between play and pause states."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("Play")
            self.timer.stop()
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
            self.timer.start()

    def cleanup(self):
        """Clean up resources when widget is closed."""
        self.timer.stop()
        self.media_player.stop()
        self.media_player.deleteLater()