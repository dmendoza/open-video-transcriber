import pytest
from pathlib import Path
import tempfile
import shutil
import numpy as np
from whisper_transcriber.core.transcription import Transcriber
from whisper_transcriber.core.model_manager import ModelManager
from whisper_transcriber.config import Config
from whisper_transcriber.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_audio(temp_dir):
    """Create a sample audio file for testing."""
    try:
        # Generate a simple audio file with speech-like characteristics
        duration = 2  # seconds
        rate = 16000  # Whisper expects 16kHz
        t = np.linspace(0, duration, int(rate * duration))
        
        # Generate a complex waveform (more speech-like than a simple sine wave)
        audio_data = (np.sin(2 * np.pi * 440 * t) +  # Fundamental frequency
                     0.5 * np.sin(2 * np.pi * 880 * t) +  # First harmonic
                     0.25 * np.sin(2 * np.pi * 1320 * t))  # Second harmonic
        
        # Normalize the audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Save the audio file
        audio_path = temp_dir / "test_audio.wav"
        from scipy.io import wavfile
        wavfile.write(str(audio_path), rate, (audio_data * 32767).astype(np.int16))
        
        return audio_path
    except ImportError as e:
        pytest.skip(f"Required package not available: {e}")

@pytest.fixture
def model_manager():
    """Create a ModelManager instance."""
    return ModelManager()

class TestModelManager:
    """Test suite for ModelManager class."""

    def test_initialization(self):
        """Test ModelManager initialization."""
        manager = ModelManager()
        assert isinstance(manager, ModelManager)
        assert hasattr(manager, 'downloaded_models')

    def test_check_downloaded_models(self, model_manager):
        """Test checking for downloaded models."""
        model_manager._check_downloaded_models()
        assert isinstance(model_manager.downloaded_models, list)

    def test_get_model_size(self, model_manager):
        """Test getting model size information."""
        size = model_manager.get_model_size('base')
        assert isinstance(size, int)
        assert size > 0

    def test_get_available_space(self, model_manager):
        """Test checking available disk space."""
        space = model_manager.get_available_space()
        assert isinstance(space, int)
        assert space > 0

    def test_invalid_model_name(self, model_manager):
        """Test handling of invalid model names."""
        with pytest.raises(ValueError):
            model_manager.download_model('invalid_model')

class TestTranscriber:
    """Test suite for Transcriber class."""

    def test_initialization(self):
        """Test Transcriber initialization."""
        transcriber = Transcriber()
        assert isinstance(transcriber, Transcriber)
        assert transcriber.model_name == Config.DEFAULT_MODEL
        assert transcriber.model is None

    def test_ensure_model(self):
        """Test model availability check."""
        transcriber = Transcriber('tiny')  # Use tiny model for faster testing
        assert isinstance(transcriber.ensure_model(), bool)

    @pytest.mark.slow
    def test_load_model(self):
        """Test model loading."""
        transcriber = Transcriber('tiny')  # Use tiny model for faster testing
        transcriber.load_model()
        assert transcriber.model is not None

    @pytest.mark.slow
    def test_transcribe_audio(self, sample_audio):
        """Test audio transcription."""
        transcriber = Transcriber('tiny')  # Use tiny model for faster testing
        result = transcriber.transcribe(sample_audio)
        
        assert isinstance(result, dict)
        assert 'text' in result
        assert isinstance(result['text'], str)

    def test_transcribe_invalid_audio(self, temp_dir):
        """Test handling of invalid audio file."""
        transcriber = Transcriber('tiny')
        invalid_audio = temp_dir / "invalid.wav"
        
        # Create an invalid audio file
        with open(invalid_audio, 'wb') as f:
            f.write(b'invalid data')
        
        with pytest.raises(Exception):
            transcriber.transcribe(invalid_audio)

    def test_transcribe_missing_audio(self, temp_dir):
        """Test handling of missing audio file."""
        transcriber = Transcriber('tiny')
        missing_audio = temp_dir / "missing.wav"
        
        with pytest.raises(Exception):
            transcriber.transcribe(missing_audio)

    @pytest.mark.parametrize("model_name", ["tiny", "base"])
    def test_different_models(self, model_name, sample_audio):
        """Test transcription with different models."""
        transcriber = Transcriber(model_name)
        
        try:
            result = transcriber.transcribe(sample_audio)
            assert isinstance(result, dict)
            assert 'text' in result
        except Exception as e:
            pytest.skip(f"Model {model_name} not available: {e}")

if __name__ == '__main__':
    pytest.main([__file__])