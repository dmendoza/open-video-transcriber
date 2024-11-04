# Open Video Transcriber

A desktop application for transcribing video files using OpenAI's Whisper model.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/open-video-transcriber
cd open-video-transcriber
```

2. Set up the development environment:
```bash
# On Windows:
python setup_dev_env.py

# On macOS/Linux:
python3 setup_dev_env.py
```

3. Activate the virtual environment:
```bash
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Development Workflow

1. Always activate the virtual environment before working on the project:
```bash
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

2. Run the application:
```bash
python -m open_video_transcriber
```

3. Run tests:
```bash
pytest tests/
```

4. Format code:
```bash
black src/
```

5. Run linter:
```bash
flake8 src/
```

### Managing Dependencies

- Add new project dependencies to `setup.py` under `install_requires`
- Add new development dependencies to `setup.py` under `extras_require["dev"]`
- After updating dependencies, reinstall the package:
```bash
pip install -e .[dev]
```

### Deactivating the Virtual Environment

When you're done working on the project:
```bash
deactivate
```

## Project Structure

```
open_video_transcriber/
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
├── setup_dev_env.py
├── src/
│   └── open_video_transcriber/
│       ├── __init__.py
│       ├── config.py
│       ├── constants.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── audio.py
│       │   └── transcription.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── widgets.py
│       │   └── audio_visualization.py
│       ├── utils/
│       │   ├── __init__.py
│       │   └── logger.py
│       └── main.py
└── tests/
    ├── __init__.py
    ├── test_audio.py
    └── test_transcription.py
```

## Common Issues and Solutions

### Installation Issues

1. **PyTorch Installation Fails**
   - Try installing PyTorch separately first:
   ```bash
   pip install torch
   ```
   - Then install the rest of the dependencies:
   ```bash
   pip install -e .[dev]
   ```

2. **FFmpeg Not Found**
   - Install FFmpeg using your system's package manager
   - On Windows: Download from FFmpeg website and add to PATH
   - On macOS: `brew install ffmpeg`
   - On Linux: `sudo apt-get install ffmpeg`

### Development Issues

1. **Import Errors**
   - Make sure the virtual environment is activated
   - Verify the package is installed in editable mode
   - Check your PYTHONPATH if needed

2. **GUI Issues**
   - On Linux, ensure Qt dependencies are installed:
   ```bash
   sudo apt-get install python3-pyqt5
   ```

## License

[MIT License](LICENSE)