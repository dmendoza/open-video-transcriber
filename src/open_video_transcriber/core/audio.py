"""
This module provides functionality to extract audio from video files.

Classes:
    AudioExtractor: A class with a static method to extract audio from a video file.
"""
from moviepy.editor import VideoFileClip
from pathlib import Path
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)

class AudioExtractor:
    @staticmethod
    def extract_audio(video_path: Path, output_path: Path = None) -> Path:
        """
        Extracts the audio from a given video file and saves it as a .wav file.

        Args:
            video_path (Path): The path to the video file from which to extract audio.
            output_path (Path, optional): The path where the extracted audio file will be saved. 
                                          If not provided, the audio will be saved in the TEMP_DIR 
                                          with the same name as the video file but with a .wav extension.
        Returns:
            Path: The path to the extracted audio file.
        Raises:
            Exception: If there is an error during the audio extraction process.
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