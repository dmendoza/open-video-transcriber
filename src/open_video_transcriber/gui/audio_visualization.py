import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt, pyqtSignal
import librosa

class AudioVisualizationWidget(QWidget):
    seek_position = pyqtSignal(float)  # Signal to emit seek position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.transcription = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Create matplotlib Figure and Canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        
        # Add slider for seeking
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.seek)
        layout.addWidget(self.slider)
        
        self.setLayout(layout)

    def load_audio(self, audio_path):
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None)
        self.plot_audio()

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
                for segment in self.transcription['segments']:
                    ax.axvline(x=segment['start'], color='r', linestyle='--', alpha=0.5)
                    ax.text(segment['start'], ax.get_ylim()[1], segment['text'], rotation=90, verticalalignment='bottom')
        
        self.canvas.draw()

    def seek(self, value):
        if self.audio_data is not None:
            position = value / 100 * (len(self.audio_data) / self.sample_rate)
            self.seek_position.emit(position)

    def update_position(self, position):
        if self.audio_data is not None:
            value = int(position / (len(self.audio_data) / self.sample_rate) * 100)
            self.slider.setValue(value)