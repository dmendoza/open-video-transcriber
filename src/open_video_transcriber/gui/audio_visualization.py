"""
This module provides a PyQt5 widget for visualizing audio waveforms and handling audio playback.

Classes:
    AudioVisualizationWidget: A QWidget subclass that visualizes audio waveforms and provides playback controls.
Signals:
    AudioVisualizationWidget.seek_position: Signal emitted when the user seeks to a new position in the audio.
    AudioVisualizationWidget.playback_updated_position: Signal emitted when the playback position is updated.
"""
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
        """
        Initializes the AudioVisualization class.

        Args:
            parent (optional): The parent widget. Defaults to None.
        Attributes:
            audio_data (None): Placeholder for audio data.
            sample_rate (None): Placeholder for the sample rate of the audio data.
            transcription (None): Placeholder for the transcription of the audio data.
            current_time (int): The current time position in the audio data. Defaults to 0.
            segment_lines (list): List to store segment lines for visualization.
            current_segment_highlight (None): Placeholder for the current segment highlight.
            ax (None): Reference to the axes for plotting.
        """
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
        """
        Initializes the user interface for the audio visualization component.
        This method sets up the layout and widgets for the audio visualization,
        including a matplotlib figure and canvas for plotting, a play/pause button,
        and a slider for seeking through the audio. It also initializes the media
        player and a timer for updating the position and highlighting.
        Widgets and Layout:
        - QVBoxLayout: Main layout for the component.
        - QHBoxLayout: Layout for control elements (play button and slider).
        - FigureCanvasQTAgg: Canvas for displaying the matplotlib figure.
        - QPushButton: Play/pause button.
        - QSlider: Slider for seeking through the audio.
        Media Player:
        - QMediaPlayer: Media player for handling audio playback.
        - QTimer: Timer for updating the position and highlighting.
        Connections:
        - play_button.clicked: Connected to the toggle_play method.
        - slider.valueChanged: Connected to the slider_seek method.
        - media_player.positionChanged: Connected to the update_position method.
        - timer.timeout: Connected to the update_highlight method.
        """
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
        self.media_player.notifyInterval = 500  # Notify every 500 ms
        self.media_player.positionChanged.connect(self.update_position)
        
        # Setup timer for updating position
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Update every 100 ms
        self.timer.timeout.connect(self.update_highlight)

    def load_audio(self, audio_path):
        """
        Loads an audio file, extracts its data and sample rate, and updates the media player.

        Args:
            audio_path (str): The file path to the audio file to be loaded.

        Returns:
            None
        """
        self.audio_data, self.sample_rate = librosa.load(audio_path, sr=None)
        self.plot_audio()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(audio_path))))

    def set_transcription(self, transcription):
        """
        Sets the transcription text and updates the audio plot.

        Args:
            transcription (str): The transcription text to be set.
        """
        self.transcription = transcription
        self.plot_audio()

    def plot_audio(self):
        """
        Plots the audio waveform and transcription segments on the figure.
        This method clears the current figure, adds a new subplot, and plots the audio waveform
        if audio data is available. It also plots vertical lines and text labels for each segment
        in the transcription if available. Additionally, it initializes a highlight patch for the
        current segment.

        Attributes:
            self.figure (matplotlib.figure.Figure): The figure object to plot on.
            self.ax (matplotlib.axes.Axes): The axes object for the subplot.
            self.audio_data (numpy.ndarray): The audio data to plot.
            self.sample_rate (int): The sample rate of the audio data.
            self.transcription (dict): The transcription data containing segments.
            self.segment_lines (list): List of line objects representing segment boundaries.
            self.current_segment_highlight (matplotlib.patches.Polygon): The highlight patch for the current segment.
            self.canvas (matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg): The canvas object to draw on.
        Notes:
            - The method assumes that `self.audio_data` is a numpy array and `self.sample_rate` is an integer.
            - The `self.transcription` dictionary should contain a 'segments' key with a list of segment dictionaries,
              each having 'start' and 'text' keys.
            - The method uses matplotlib for plotting and assumes the figure and canvas are properly initialized.
        """

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
                    # self.ax.text(segment['start'], self.ax.get_ylim()[1], 
                            #    segment['text'][:20] + '...' if len(segment['text']) > 20 else segment['text'],
                            #    rotation=45, verticalalignment='bottom', fontsize=8)
                
                # Initialize the highlight patch
                if self.current_segment_highlight is None:
                    self.current_segment_highlight = self.ax.axvspan(0, 0, color='yellow', alpha=0.2)
            
            # Adjust layout to prevent text cutoff
            self.figure.tight_layout()
            
        self.canvas.draw()

    def update_highlight(self):
        """
        Updates the highlight on the audio visualization to reflect the current transcription segment.
        This method checks if there is a transcription and a current segment highlight. If so, it finds the current
        segment and updates the highlight on the audio visualization by removing the previous highlight and creating
        a new one. The highlight is represented as a shaded region between the start and end times of the current
        segment.
        The method uses `axvspan` to create the highlight and `draw_idle` to update the canvas efficiently.

        Attributes:
            self.transcription (list): The list of transcription segments.
            self.current_segment_highlight (matplotlib.patches.Patch): The current highlighted segment on the plot.
            self.ax (matplotlib.axes.Axes): The axes object of the plot.
            self.canvas (matplotlib.backend_bases.FigureCanvasBase): The canvas object of the plot.
        """
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
        """
        Finds the current transcription segment based on the current time.
        This method iterates through the segments in the transcription and 
        returns the segment where the current time falls between the start 
        and end times of the segment.

        Returns:
            dict or None: The current segment if found, otherwise None.
        """
        if not self.transcription:
            return None
            
        for segment in self.transcription['segments']:
            if segment['start'] <= self.current_time <= segment['end']:
                return segment
        return None

    def slider_seek(self, slider_seek_value):
        """
        Adjusts the media player's position based on the slider's seek value.

        Parameters:
        slider_seek_value (float): The value from the slider indicating the desired seek position 
                       as a percentage (0 to 100).
        """
        logger.info(f"seek > value: {slider_seek_value}")
        if self.audio_data is not None:
            duration = len(self.audio_data) / self.sample_rate
            current_time = (slider_seek_value / 100.0) * duration
            slider_seek_position = current_time * 1000  # Convert to milliseconds
            # logger.info(f"seek > slider_seek_position: {slider_seek_position}")
            self.media_player.setPosition(int(slider_seek_position))  # Convert to milliseconds
            # self.seek_position.emit(slider_seek_position)

    def update_position(self, media_player_position):
        """
        Updates the current playback position of the media player and adjusts the slider accordingly.

        Args:
            media_player_position (int): The current position of the media player in milliseconds.

        Emits:
            playback_updated_position (float): The updated playback position in seconds.
        """
        # logger.info(f"update_position > media_player_position: {media_player_position}")
        self.current_time = media_player_position / 1000.0  # Convert from milliseconds to seconds
        if self.audio_data is not None:
            duration = len(self.audio_data) / self.sample_rate
            slider_seek_value = int((self.current_time / duration) * 100)
            self.playback_updated_position.emit(self.current_time) # Convert to milliseconds
            self.slider.blockSignals(True)
            self.slider.setValue(slider_seek_value)
            self.slider.blockSignals(False)

    def toggle_play(self):
        """
        Toggles the play/pause state of the media player.

        If the media player is currently playing, this method will pause it,
        change the play button text to "Play", and stop the timer. If the media
        player is paused, this method will start playing it, change the play
        button text to "Pause", and start the timer.
        """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("Play")
            self.timer.stop()
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
            self.timer.start()

    def cleanup(self):
        """
        Cleans up the audio visualization widget by stopping the timer and media player,
        and deleting the media player instance.

        This method performs the following actions:
        - Logs an info message indicating the cleanup process.
        - Stops the timer associated with the audio visualization.
        - Stops the media player to halt any ongoing audio playback.
        - Deletes the media player instance to free up resources.
        """
        logger.info("Cleaning up audio visualization widget")
        self.timer.stop()
        self.media_player.stop()
        self.media_player.deleteLater()