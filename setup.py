"""
Setup script for the open_video_transcriber package.

This script uses setuptools to package the open_video_transcriber application, 
which is a desktop application for transcribing video files using OpenAI's Whisper.
"""
from setuptools import setup, find_packages
import os
from pathlib import Path

def get_model_files():
    """
    Retrieves the model files from the specified directory.

    This function checks if the directory 'src/open_video_transcriber/resources/models' exists.
    If it does, it returns a list containing a tuple. The tuple consists of the relative path 
    to the model directory and a list of all files within that directory.

    Returns:
        list: A list containing a single tuple. The tuple contains:
            - str: The relative path to the model directory.
            - list: A list of strings representing the file paths of all files in the model directory.
        If the directory does not exist, an empty list is returned.
    """
    model_dir = Path("src/open_video_transcriber/resources/models")
    if model_dir.exists():
        return [
            (str(model_dir.relative_to("src/open_video_transcriber")), 
             [str(f) for f in model_dir.glob("*") if f.is_file()])
        ]
    return []

setup(
    name="open_video_transcriber",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    data_files=get_model_files(),
    install_requires=[
        "openai-whisper>=0.5.0",
        "moviepy>=1.0.3",
        "PyQt5>=5.15.0",
        "torch>=2.0.0",
        "numpy>=1.20.0",
        "matplotlib>=3.9.2",
        "librosa>=0.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "py2app>=0.28.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "open-video-transcriber=open_video_transcriber.main:main",
        ],
    },
    author="Diego E. Mendoza",
    author_email="diego.e.mendoza@gmail.com",
    description="A desktop application for transcribing video files using OpenAI's Whisper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="whisper, transcription, video, audio, speech-to-text",
    url="https://github.com/yourusername/open-video-transcriber",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
)