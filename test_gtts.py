import sys
import traceback
sys.stdout.reconfigure(encoding='utf-8')
from gtts import gTTS

try:
    print("Generating audio...")
    tts = gTTS(text='नमस्ते', lang='hi')
    tts.save('test_hi.mp3')
    print("Saved test_hi.mp3")
except Exception as e:
    print(traceback.format_exc())
