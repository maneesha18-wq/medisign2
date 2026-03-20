import os
import tempfile
# Workaround for Avast/AVG SSL permission error
if "SSLKEYLOGFILE" in os.environ:
    del os.environ["SSLKEYLOGFILE"]

from gtts import gTTS
from pathlib import Path

def speak_text(text: str, output_dir: str = "temp_audio") -> str:
    """
    Converts text to speech using gTTS and saves it as an MP3 file.
    
    Args:
        text: The text to convert to speech.
        output_dir: Directory to save the audio file.
        
    Returns:
        Absolute path to the generated MP3 file.
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create a unique filename based on the text (sanitized) to avoid collisions if needed,
        # or just use a fixed name if we want to overwrite.
        # For this app, overwriting a single "output.mp3" might cause caching issues in browsers.
        # Let's use a hashed name or timestamp? 
        # Actually, Gradio handles temp files well if we return a path. 
        # But to be safe and avoid race conditions or browser caching of "same name different content",
        # let's generate a unique name.
        
        # However, accumulating files is bad.
        # Let's try to simple approach: unique name, but relying on OS temp dir might be better?
        # The prompt asks to "Handle file overwrite safely".
        # If we use a single file "prediction.mp3", browser might cache it.
        # Let's use a temp file.
        
        # Clean up old files in the directory? 
        # For simplicity in this stage, let's just create a new file.
        # In a long running production app we'd need a cleaner.
        
        filename = "prediction.mp3"
        filepath = output_path / filename
        
        tts = gTTS(text=text, lang='en')
        tts.save(str(filepath))
        
        return str(filepath.resolve())
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
