
from modules.tts import speak_text
import os

try:
    path = speak_text("Testing TTS functionality", output_dir="temp_audio_test")
    if path and os.path.exists(path):
        print(f"PASS: TTS generated at {path}")
    else:
        print("FAIL: TTS failed to generate file")
except Exception as e:
    print(f"FAIL: Exception {e}")
