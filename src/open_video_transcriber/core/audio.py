# src/open_video_transcriber/core/audio.py
from moviepy.editor import VideoFileClip
from pathlib import Path
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)

class AudioExtractor:
    @staticmethod
    def extract_audio(video_path: Path, output_path: Path = None) -> Path:
        """
        Extract audio from a video file.
        
        Args:
            video_path (Path): Path to the video file
            output_path (Path, optional): Path for the output audio file
            
        Returns:
            Path: Path to the extracted audio file
        """
        try:
            if output_path is None:
                output_path = Config.TEMP_DIR / f"{video_path.stem}.wav"
                
            logger.info(f"Extracting audio from {video_path} to {output_path}")
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(str(output_path))
            video.close()
            
            return output_path
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise