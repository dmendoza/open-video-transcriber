# src/open_video_transcriber/constants.py
# File extensions
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"]
AUDIO_EXTENSIONS = [".wav", ".mp3", ".m4a"]

# Messages
MSG_TRANSCRIBING = "Transcribing... Please wait"
MSG_EXTRACTING_AUDIO = "Extracting audio from video..."
MSG_DONE = "Transcription completed!"
MSG_ERROR = "An error occurred: {}"

# File filters for dialog
VIDEO_FILTER = "Video Files (*.mp4 *.avi *.mov *.mkv)"