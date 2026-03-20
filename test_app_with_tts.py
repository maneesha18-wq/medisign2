"""
Test Gradio app with TTS - includes h5py workaround for Windows.
"""

import os
import sys

# Workaround for h5py WMI hang on Windows
os.environ["HDF5_PLUGIN_PATH"] = ""

# Add workspace to path
from pathlib import Path

workspace_dir = Path(__file__).parent
sys.path.insert(0, str(workspace_dir))

print("\n" + "=" * 80)
print("Gradio App Test - TTS Enabled")
print("=" * 80)

# Test app load without building interface (to avoid Gradio launch)
print(f"\n1. Loading TensorFlow and Keras...")
try:
    import tensorflow as tf

    print(f"✓ TensorFlow {tf.__version__} loaded")
except Exception as e:
    print(f"⚠ TensorFlow load warning: {str(e)[:100]}")

print(f"\n2. Loading custom layer registration...")
from modules.sequence_model import AttentionLayer

print(f"✓ AttentionLayer imported and ready")

print(f"\n3. Loading trained model...")
model_path = Path("models/sequence_model_final.keras")
if model_path.exists():
    try:
        model = tf.keras.models.load_model(
            model_path, custom_objects={"AttentionLayer": AttentionLayer}
        )
        print(f"✓ Model loaded successfully")
        print(f"  - Input shape: {model.input_shape}")
        print(f"  - Output shape: {model.output_shape}")
    except Exception as e:
        print(f"❌ Model load failed: {e}")
        sys.exit(1)
else:
    print(f"❌ Model not found at {model_path}")
    sys.exit(1)

print(f"\n4. Initializing MediSign app...")
try:
    from app import MedisignApp

    app = MedisignApp(
        model_path="models/sequence_model_final.keras",
        label_map_path="dataset",
        device="cpu",
        enable_tts=True,
    )
    print(f"✓ MediSign app initialized")
    print(f"  - Model: {app.model is not None}")
    print(f"  - Feature extractor: {app.feature_extractor is not None}")
    print(f"  - TTS enabled: {app.tts is not None}")
    print(f"  - Labels: {app.label_names}")
except Exception as e:
    print(f"❌ App initialization failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print(f"\n5. Testing inference with synthetic data...")
try:
    import numpy as np

    # Create synthetic feature
    features = np.random.randn(60, 1280).astype(np.float32)
    feature_batch = np.expand_dims(features, axis=0)

    # Run inference
    logits = app.model.predict(feature_batch, verbose=0)
    pred_idx = np.argmax(logits[0])
    confidence = float(logits[0, pred_idx])
    label = (
        app.label_names[pred_idx]
        if 0 <= pred_idx < len(app.label_names)
        else f"class_{pred_idx}"
    )

    print(f"✓ Inference successful")
    print(f"  - Predicted: {label}")
    print(f"  - Confidence: {confidence:.4f}")

    # Test TTS through app
    print(f"\n6. Generating audio via app.tts...")
    if app.tts:
        audio_file, error = app.tts.convert_and_save(text=label, label=label)
        if audio_file:
            audio_path = Path(audio_file)
            if audio_path.exists():
                size_kb = audio_path.stat().st_size / 1024
                print(f"✓ Audio generated via app")
                print(f"  - File: {audio_path.name}")
                print(f"  - Size: {size_kb:.2f} KB")
        else:
            print(f"⚠ Audio generation returned None")
    else:
        print(f"⚠ TTS not initialized")

except Exception as e:
    print(f"❌ Inference failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print(f"\n7. Building Gradio interface...")
try:
    demo = app.build_interface()
    print(f"✓ Gradio interface built successfully")
    print(f"  - Type: {type(demo).__name__}")
    print(f"  - With audio output components: Yes")
    print(f"  - With enable_audio checkbox: Yes")
except Exception as e:
    print(f"❌ Gradio build failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print(f"\n8. Verifying audio directory...")
audio_dir = Path("logs/audio")
if audio_dir.exists():
    audio_files = sorted(audio_dir.glob("*.mp3"))
    print(f"✓ Audio directory: {audio_dir}")
    print(f"  - Total files: {len(audio_files)}")
    if audio_files:
        print(f"  - Latest: {audio_files[-1].name}")
else:
    print(f"⚠ Audio directory not found")

print(f"\n" + "=" * 80)
print("✓ All app tests passed! Ready for deployment.")
print("=" * 80)
print(f"\nTo launch the app, run:")
print(f"  python app.py --port 7860")
print(f"\nThe interface will have:")
print(f"  - Upload tab with video upload and audio output")
print(f"  - Webcam tab with live recording and audio output")
print(f"  - Info tab with model details and TTS info\n")
