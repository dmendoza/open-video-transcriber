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

class AudioVisualizationWidget(QWidget):
    seek_position = pyqtSignal(float)  # Signal to emit seek position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.transcription = None
        self.current_time = 0
        self.segment_lines = []
        self.current_segment_highlight = None
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
        self.slider.valueChanged.connect(self.seek)
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
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None)
        self.plot_audio()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(audio_path))))

    def set_transcription(self, transcription):
        self.transcription = transcription
        self.plot_audio()  # Replot to include transcription

    def plot_audio(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self.audio_data is not None:
            times = np.linspace(0, len(self.audio_data) / self.sample_rate, num=len(self.audio_data))
            ax.plot(times, self.audio_data)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            
            if self.transcription:
                self.segment_lines = []
                for segment in self.transcription['segments']:
                    line = ax.axvline(x=segment['start'], color='r', linestyle='--', alpha=0.5)
                    self.segment_lines.append(line)
                    ax.text(segment['start'], ax.get_ylim()[1], segment['text'], rotation=90, verticalalignment='bottom')
                
                self.current_segment_highlight = ax.axvspan(0, 0, color='yellow', alpha=0.3)
        
        self.canvas.draw()

    def seek(self, value):
        if self.audio_data is not None:
            position = value / 100 * (len(self.audio_data) / self.sample_rate)
            self.media_player.setPosition(int(position * 1000))
            self.seek_position.emit(position)

    def update_position(self, position):
        self.current_time = position / 1000  # Convert to seconds
        if self.audio_data is not None:
            value = int(self.current_time / (len(self.audio_data) / self.sample_rate) * 100)
            self.slider.setValue(value)

    def update_highlight(self):
        if self.transcription:
            current_segment = self.find_current_segment()
            if current_segment:
                start = current_segment['start']
                end = current_segment['end']
                # xy = [(start, 0), (start, 1), (end, 1), (end, 0)]
                # self.current_segment_highlight.set_xy(xy)
                self.current_segment_highlight.set_xy([[start, 0], [start, 1], [end, 1], [end, 0]])
                self.canvas.draw()

    def find_current_segment(self):
        for segment in self.transcription['segments']:
            if segment['start'] <= self.current_time < segment['end']:
                return segment
        return None

    def toggle_play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("Play")
            self.timer.stop()
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
            self.timer.start()