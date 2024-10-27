import pytest
from pathlib import Path
import tempfile
import shutil
import os
from open_video_transcriber.core.audio import AudioExtractor
from open_video_transcriber.config import Config
from open_video_transcriber.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_video(temp_dir):
    """Create a sample video file for testing."""
    try:
        from moviepy.editor import ColorClip, AudioFileClip
        import numpy as np

        # Create a simple video with audio
        duration = 2  # seconds
        fps = 24
        video_clip = ColorClip(size=(320, 240), color=(0, 0, 0), duration=duration)
        
        # Generate a simple audio tone
        rate = 44100
        t = np.linspace(0, duration, int(rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
        
        # Save audio temporarily
        audio_path = temp_dir / "temp_audio.wav"
        with open(audio_path, 'wb') as f:
            from scipy.io import wavfile
            wavfile.write(f.name, rate, audio_data.astype(np.float32))
        
        # Combine video and audio
        video_clip = video_clip.set_audio(AudioFileClip(str(audio_path)))
        video_path = temp_dir / "test_video.mp4"
        video_clip.write_videofile(str(video_path), fps=fps, audio=True)
        
        # Clean up temporary audio file
        audio_path.unlink()
        
        return video_path
    except ImportError as e:
        pytest.skip(f"Required package not available: {e}")

class TestAudioExtractor:
    """Test suite for AudioExtractor class."""

    def test_initialization(self):
        """Test AudioExtractor initialization."""
        extractor = AudioExtractor()
        assert isinstance(extractor, AudioExtractor)

    def test_extract_audio_from_video(self, temp_dir, sample_video):
        """Test extracting audio from a video file."""
        extractor = AudioExtractor()
        output_path = temp_dir / "output_audio.wav"
        
        # Extract audio
        result_path = extractor.extract_audio(sample_video, output_path)
        
        # Verify results
        assert result_path.exists()
        assert result_path.suffix == ".wav"
        assert os.path.getsize(result_path) > 0

    def test_extract_audio_invalid_video(self, temp_dir):
        """Test handling of invalid video file."""
        extractor = AudioExtractor()
        invalid_video = temp_dir / "invalid.mp4"
        output_path = temp_dir / "output_audio.wav"
        
        # Create an invalid video file
        with open(invalid_video, 'wb') as f:
            f.write(b'invalid data')
        
        # Test error handling
        with pytest.raises(Exception):
            extractor.extract_audio(invalid_video, output_path)

    def test_extract_audio_missing_file(self, temp_dir):
        """Test handling of missing video file."""
        extractor = AudioExtractor()
        missing_video = temp_dir / "missing.mp4"
        output_path = temp_dir / "output_audio.wav"
        
        with pytest.raises(Exception):
            extractor.extract_audio(missing_video, output_path)

    def test_extract_audio_no_output_path(self, sample_video):
        """Test extraction without specifying output path."""
        extractor = AudioExtractor()
        
        # Extract audio without specifying output path
        result_path = extractor.extract_audio(sample_video)
        
        # Verify results
        assert result_path.exists()
        assert result_path.suffix == ".wav"
        assert result_path.parent == Config.TEMP_DIR
        
        # Clean up
        result_path.unlink()

    @pytest.mark.parametrize("video_format", [".mp4", ".avi", ".mov", ".mkv"])
    def test_extract_audio_different_formats(self, temp_dir, video_format):
        """Test audio extraction from different video formats."""
        try:
            from moviepy.editor import ColorClip
            
            # Create a test video in the specified format
            video_clip = ColorClip(size=(320, 240), color=(0, 0, 0), duration=1)
            video_path = temp_dir / f"test_video{video_format}"
            video_clip.write_videofile(str(video_path), fps=24, audio=False)
            
            extractor = AudioExtractor()
            output_path = temp_dir / "output_audio.wav"
            
            # Test extraction
            result_path = extractor.extract_audio(video_path, output_path)
            assert result_path.exists()
            
        except ImportError as e:
            pytest.skip(f"Required package not available: {e}")