"""
Simple TTS test - no TensorFlow import to avoid h5py hang.
"""

from pathlib import Path
from modules.text_to_speech import TextToSpeech

print("\n" + "=" * 80)
print("Simple TTS Integration Test")
print("=" * 80)

print(f"\n1. Initializing TTS...")
tts = TextToSpeech(output_dir="logs/audio", language="en")
print(f"✓ TTS initialized")

print(f"\n2. Generating audio for test labels...")
test_labels = ["hello", "medical_sign_0", "patient", "diagnosis"]

for label in test_labels:
    print(f"\n  Testing label: '{label}'")
    audio_file, error = tts.convert_and_save(text=label, label=label)

    if error:
        print(f"    ⚠ Warning: {error}")
    elif audio_file:
        audio_path = Path(audio_file)
        if audio_path.exists():
            file_size_kb = audio_path.stat().st_size / 1024
            print(f"    ✓ Audio generated: {audio_path.name} ({file_size_kb:.2f} KB)")
        else:
            print(f"    ❌ File not found: {audio_file}")
    else:
        print(f"    ❌ No audio file returned")

print(f"\n3. Listing audio files...")
audio_dir = Path("logs/audio")
if audio_dir.exists():
    audio_files = sorted(audio_dir.glob("*.mp3"))
    print(f"✓ Total audio files: {len(audio_files)}")
    print(f"\n  Recent files:")
    for f in audio_files[-5:]:
        size_kb = f.stat().st_size / 1024
        print(f"    - {f.name} ({size_kb:.2f} KB)")
else:
    print(f"❌ Audio directory not found")

print(f"\n" + "=" * 80)
print("✓ TTS Test Complete!")
print("=" * 80 + "\n")
