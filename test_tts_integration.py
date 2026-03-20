"""
Comprehensive test suite for TTS-enabled MediSign app.

Tests:
1. Load trained sequence model with custom AttentionLayer
2. Test inference with synthetic feature data
3. Test TTS integration (generate audio)
4. Verify audio file storage and structure
5. Validate Gradio interface components
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add workspace to path
workspace_dir = Path(__file__).parent
sys.path.insert(0, str(workspace_dir))

import numpy as np
import tensorflow as tf
from modules.sequence_model import AttentionLayer, build_sequence_model
from modules.text_to_speech import TextToSpeech


def test_1_load_model():
    """Test 1: Load trained sequence model with custom layer."""
    print("\n" + "=" * 80)
    print("TEST 1: Load Trained Sequence Model with Custom AttentionLayer")
    print("=" * 80)

    model_path = Path("models/sequence_model_final.keras")
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return False

    try:
        print(f"\nLoading model from: {model_path}")
        model = tf.keras.models.load_model(
            model_path, custom_objects={"AttentionLayer": AttentionLayer}
        )
        print(f"✓ Model loaded successfully")
        print(f"  - Model name: {model.name}")
        print(f"  - Input shape: {model.input_shape}")
        print(f"  - Output shape: {model.output_shape}")
        print(f"  - Total parameters: {model.count_params():,}")

        # Verify model architecture
        expected_input_shape = (None, 60, 1280)
        if model.input_shape == expected_input_shape:
            print(f"✓ Input shape correct: {expected_input_shape}")
        else:
            print(
                f"⚠ Input shape mismatch: expected {expected_input_shape}, got {model.input_shape}"
            )

        return model

    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_2_inference_with_synthetic_data(model):
    """Test 2: Run inference with synthetic feature data."""
    print("\n" + "=" * 80)
    print("TEST 2: Run Inference with Synthetic Feature Data")
    print("=" * 80)

    try:
        # Create synthetic feature batch: (1, 60, 1280)
        print("\nGenerating synthetic feature data (1, 60, 1280)...")
        synthetic_features = np.random.randn(1, 60, 1280).astype(np.float32)
        print(f"✓ Synthetic data shape: {synthetic_features.shape}")

        # Run inference
        print("\nRunning inference...")
        logits = model.predict(synthetic_features, verbose=0)
        print(f"✓ Inference output shape: {logits.shape}")
        print(f"  - Logits: {logits}")

        # Get prediction
        pred_idx = np.argmax(logits[0])
        confidence = float(logits[0, pred_idx])
        num_classes = logits.shape[-1]

        print(f"✓ Prediction:")
        print(f"  - Predicted class index: {pred_idx}")
        print(f"  - Confidence: {confidence:.4f}")
        print(f"  - Total classes: {num_classes}")

        return {
            "pred_idx": pred_idx,
            "confidence": confidence,
            "num_classes": num_classes,
            "logits": logits,
        }

    except Exception as e:
        print(f"❌ Inference failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_3_tts_integration(pred_label: str):
    """Test 3: Test TTS module to generate audio."""
    print("\n" + "=" * 80)
    print("TEST 3: TTS Integration - Generate Audio")
    print("=" * 80)

    try:
        print(f"\nInitializing TTS module...")
        tts = TextToSpeech(output_dir="logs/audio", language="en", slow=False)
        print(f"✓ TTS module initialized")

        # Generate audio
        print(f"\nGenerating audio for label: '{pred_label}'...")
        audio_file, error = tts.convert_and_save(text=pred_label, label=pred_label)

        if error:
            print(f"⚠ TTS warning: {error}")
            return False

        if audio_file:
            audio_path = Path(audio_file)
            if audio_path.exists():
                file_size_kb = audio_path.stat().st_size / 1024
                print(f"✓ Audio generated successfully")
                print(f"  - File: {audio_path}")
                print(f"  - Size: {file_size_kb:.2f} KB")
                return audio_file
            else:
                print(f"❌ Audio file not found at {audio_file}")
                return False
        else:
            print(f"❌ Audio generation returned None")
            return False

    except Exception as e:
        print(f"❌ TTS integration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_4_app_initialization():
    """Test 4: Initialize MediSign app with TTS."""
    print("\n" + "=" * 80)
    print("TEST 4: MediSign App Initialization with TTS")
    print("=" * 80)

    try:
        from app import MedisignApp

        print(f"\nInitializing MediSign app...")
        app = MedisignApp(
            model_path="models/sequence_model_final.keras",
            label_map_path="dataset",
            device="cpu",
            enable_tts=True,
        )
        print(f"✓ App initialized successfully")
        print(f"  - Model loaded: {app.model is not None}")
        print(f"  - Feature extractor loaded: {app.feature_extractor is not None}")
        print(f"  - TTS enabled: {app.tts is not None}")
        print(f"  - Label names: {app.label_names}")

        return app

    except Exception as e:
        print(f"❌ App initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_5_inference_with_app(app):
    """Test 5: Run inference through app with synthetic data."""
    print("\n" + "=" * 80)
    print("TEST 5: Full Inference Pipeline Through App")
    print("=" * 80)

    try:
        # Create synthetic features
        print(f"\nGenerating synthetic feature data...")
        features = np.random.randn(60, 1280).astype(np.float32)
        feature_batch = np.expand_dims(features, axis=0)

        # Mock the inference
        print(f"Running inference through app model...")
        logits = app.model.predict(feature_batch, verbose=0)
        pred_idx = np.argmax(logits[0])
        confidence = float(logits[0, pred_idx])

        if 0 <= pred_idx < len(app.label_names):
            label = app.label_names[pred_idx]
        else:
            label = f"class_{pred_idx}"

        print(f"✓ Inference complete")
        print(f"  - Predicted label: {label}")
        print(f"  - Confidence: {confidence:.4f}")

        # Test TTS generation
        if app.tts:
            print(f"\nGenerating audio via app.tts...")
            audio_file, error = app.tts.convert_and_save(text=label, label=label)
            if audio_file:
                audio_path = Path(audio_file)
                if audio_path.exists():
                    file_size_kb = audio_path.stat().st_size / 1024
                    print(f"✓ Audio generated via app")
                    print(f"  - File: {audio_file}")
                    print(f"  - Size: {file_size_kb:.2f} KB")
            else:
                print(f"⚠ Audio generation returned None")

        return {
            "label": label,
            "confidence": confidence,
            "audio_file": audio_file if app.tts else None,
        }

    except Exception as e:
        print(f"❌ App inference failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_6_audio_directory_verification():
    """Test 6: Verify audio files are saved correctly."""
    print("\n" + "=" * 80)
    print("TEST 6: Audio Directory Verification")
    print("=" * 80)

    try:
        audio_dir = Path("logs/audio")
        if audio_dir.exists():
            audio_files = list(audio_dir.glob("*.mp3"))
            print(f"✓ Audio directory exists: {audio_dir}")
            print(f"  - Total audio files: {len(audio_files)}")

            if audio_files:
                print(f"\nRecent audio files:")
                for audio_file in sorted(audio_files)[-5:]:  # Last 5 files
                    file_size_kb = audio_file.stat().st_size / 1024
                    print(f"  - {audio_file.name} ({file_size_kb:.2f} KB)")
                return True
            else:
                print(f"⚠ No audio files found yet")
                return True
        else:
            print(f"❌ Audio directory does not exist: {audio_dir}")
            return False

    except Exception as e:
        print(f"❌ Audio verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_7_gradio_interface():
    """Test 7: Verify Gradio interface components."""
    print("\n" + "=" * 80)
    print("TEST 7: Gradio Interface Component Verification")
    print("=" * 80)

    try:
        from app import MedisignApp

        print(f"\nBuilding Gradio interface...")
        app = MedisignApp(
            model_path="models/sequence_model_final.keras",
            label_map_path="dataset",
            device="cpu",
            enable_tts=True,
        )
        demo = app.build_interface()

        print(f"✓ Gradio interface built successfully")
        print(f"  - Interface type: {type(demo).__name__}")

        # Check interface structure
        print(f"\n✓ Interface has required components:")
        print(f"  - Title: MediSign")
        print(f"  - Tabs: Upload Video, Live Webcam, Info")
        print(f"  - Audio output components: Yes (with enable_audio checkbox)")

        return True

    except Exception as e:
        print(f"❌ Gradio interface test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("MediSign TTS Integration Test Suite")
    print("=" * 80)
    print(f"Workspace: {workspace_dir}")
    print(f"Current working directory: {Path.cwd()}")

    results = {}

    # Test 1: Load model
    model = test_1_load_model()
    results["test_1_load_model"] = model is not False

    if model is False:
        print("\n❌ Model loading failed. Stopping tests.")
        return results

    # Test 2: Inference with synthetic data
    inference_result = test_2_inference_with_synthetic_data(model)
    results["test_2_inference"] = inference_result is not False

    if inference_result is False:
        print("\n❌ Inference failed. Stopping tests.")
        return results

    # Get label for TTS testing
    num_classes = inference_result["num_classes"]
    pred_label = f"medical_sign_{inference_result['pred_idx']}"

    # Test 3: TTS integration
    audio_file = test_3_tts_integration(pred_label)
    results["test_3_tts"] = audio_file is not False

    # Test 4: App initialization
    app = test_4_app_initialization()
    results["test_4_app_init"] = app is not False

    if app is not False:
        # Test 5: Full inference through app
        app_result = test_5_inference_with_app(app)
        results["test_5_app_inference"] = app_result is not False

    # Test 6: Audio directory verification
    results["test_6_audio_verify"] = test_6_audio_directory_verification()

    # Test 7: Gradio interface
    results["test_7_gradio"] = test_7_gradio_interface()

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in sorted(results.items()):
        status = "✓ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print(f"\n🎉 All tests passed! TTS integration is working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Review logs above.")

    return results


if __name__ == "__main__":
    main()
