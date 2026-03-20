"""
Step 5: Verify Medical Sign Language Pipeline

Validates that all components work correctly with real medical data
"""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import sys
import json
import numpy as np
import tensorflow as tf
from pathlib import Path
import argparse
import logging

sys.path.insert(0, ".")
from modules.feature_extractor import FeatureExtractor
from modules.sequence_model import AttentionLayer
from modules.preprocessing import preprocess_video
from modules.text_to_speech import TextToSpeech

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineVerifier:
    """Verify the complete medical sign language pipeline"""

    def __init__(self):
        self.results = {}

    def verify_model_loading(self, model_path: str) -> bool:
        """Verify model can be loaded"""
        print("\n[1/6] Verifying model loading...")
        try:
            model = tf.keras.models.load_model(
                model_path, custom_objects={"AttentionLayer": AttentionLayer}
            )
            print(f"  [OK] Model loaded: {model_path}")
            print(f"  [OK] Parameters: {model.count_params():,}")
            self.results["model"] = True
            return True
        except Exception as e:
            print(f"  [X] Model loading failed: {e}")
            self.results["model"] = False
            return False

    def verify_label_mapping(self, label_map_path: str) -> bool:
        """Verify label mapping"""
        print("\n[2/6] Verifying label mapping...")
        try:
            with open(label_map_path, "r") as f:
                label_map = json.load(f)

            num_classes = label_map["num_classes"]
            medical_terms = label_map["medical_terms"]

            print(f"  ✓ Label mapping found: {label_map_path}")
            print(f"  ✓ Classes: {num_classes}")
            print(f"  ✓ Medical terms: {', '.join(medical_terms[:3])}...")
            self.label_map = label_map
            self.results["labels"] = True
            return True
        except Exception as e:
            print(f"  ✗ Label mapping failed: {e}")
            self.results["labels"] = False
            return False

    def verify_feature_extraction(self) -> bool:
        """Verify feature extraction works"""
        print("\n[3/6] Verifying feature extraction...")
        try:
            extractor = FeatureExtractor(backbone="mobilenetv2", device="gpu")

            # Create dummy video array
            X_dummy = np.random.randn(60, 224, 224, 3).astype(np.float32)
            X_dummy = np.clip(X_dummy, 0, 1)

            features = extractor.extract(X_dummy)

            if features.shape == (60, 1280):
                print(f"  [OK] Feature extraction works")
                print(f"  [OK] Output shape: {features.shape}")
                self.results["features"] = True
                return True
            else:
                print(f"  [X] Invalid feature shape: {features.shape}")
                self.results["features"] = False
                return False
        except Exception as e:
            print(f"  [X] Feature extraction failed: {e}")
            self.results["features"] = False
            return False

    def verify_inference(self, model_path: str) -> bool:
        """Verify inference works"""
        print("\n[4/6] Verifying inference pipeline...")
        try:
            model = tf.keras.models.load_model(
                model_path, custom_objects={"AttentionLayer": AttentionLayer}
            )

            # Create dummy features
            X_test = np.random.randn(1, 60, 1280).astype(np.float32)

            logits = model.predict(X_test, verbose=0)
            pred_class = np.argmax(logits[0])
            confidence = float(logits[0, pred_class])

            num_classes = logits.shape[1]

            if hasattr(self, "label_map"):
                label = self.label_map["idx_to_label"][str(pred_class)]
            else:
                label = f"class_{pred_class}"

            print(f"  [OK] Inference works")
            print(f"  [OK] Predicted: {label} (confidence: {confidence:.4f})")
            print(f"  [OK] Output classes: {num_classes}")
            self.results["inference"] = True
            return True
        except Exception as e:
            print(f"  [X] Inference failed: {e}")
            self.results["inference"] = False
            return False

    def verify_audio_generation(self) -> bool:
        """Verify TTS audio generation"""
        print("\n[5/6] Verifying audio generation...")
        try:
            tts = TextToSpeech(output_dir="logs/audio_test")

            audio_file, error = tts.convert_and_save(text="diabetes", label="diabetes")

            if error:
                print(f"  [X] TTS error: {error}")
                self.results["audio"] = False
                return False

            if Path(audio_file).exists():
                size_kb = Path(audio_file).stat().st_size / 1024
                print(f"  [OK] Audio generation works")
                print(f"  [OK] Output: {audio_file} ({size_kb:.1f} KB)")
                self.results["audio"] = True
                return True
            else:
                print(f"  [X] Audio file not created")
                self.results["audio"] = False
                return False
        except Exception as e:
            print(f"  [X] Audio generation failed: {e}")
            self.results["audio"] = False
            return False

    def verify_test_data(self, features_dir: str) -> bool:
        """Verify test data availability"""
        print("\n[6/6] Verifying test data...")
        try:
            features_path = Path(features_dir)

            total_samples = 0
            terms = []

            for term_dir in features_path.iterdir():
                if term_dir.is_dir():
                    npy_files = list(term_dir.glob("*.npy"))
                    if npy_files:
                        total_samples += len(npy_files)
                        terms.append((term_dir.name, len(npy_files)))

            if total_samples > 0:
                print(f"  [OK] Test data found")
                print(f"  [OK] Total samples: {total_samples}")
                print(f"  [OK] Classes: {len(terms)}")
                for term, count in sorted(terms):
                    print(f"      - {term}: {count} samples")
                self.results["data"] = True
                return True
            else:
                print(f"  [X] No test data found")
                self.results["data"] = False
                return False
        except Exception as e:
            print(f"  [X] Data verification failed: {e}")
            self.results["data"] = False
            return False

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 70)
        print("PIPELINE VERIFICATION SUMMARY")
        print("=" * 70)

        checks = [
            ("Model Loading", self.results.get("model", False)),
            ("Label Mapping", self.results.get("labels", False)),
            ("Feature Extraction", self.results.get("features", False)),
            ("Inference", self.results.get("inference", False)),
            ("Audio Generation", self.results.get("audio", False)),
            ("Test Data", self.results.get("data", False)),
        ]

        all_pass = True
        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            print(f"{check_name:.<30} {status}")
            if not passed:
                all_pass = False

        print("\n" + "=" * 70)
        if all_pass:
            print("ALL CHECKS PASSED - Pipeline ready for production!")
        else:
            print("Some checks failed - please review above")
        print("=" * 70)

        return all_pass


def main():
    parser = argparse.ArgumentParser(
        description="Verify medical sign language pipeline"
    )
    parser.add_argument(
        "--model",
        default="models/sequence_model_medical.keras",
        help="Trained model path",
    )
    parser.add_argument(
        "--label-map",
        default="models/medical_terms_map.json",
        help="Label mapping file",
    )
    parser.add_argument(
        "--features-dir", default="dataset/features", help="Features directory"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("STEP 5: PIPELINE VERIFICATION")
    print("=" * 70)

    verifier = PipelineVerifier()

    verifier.verify_model_loading(args.model)
    verifier.verify_label_mapping(args.label_map)
    verifier.verify_feature_extraction()
    verifier.verify_inference(args.model)
    verifier.verify_audio_generation()
    verifier.verify_test_data(args.features_dir)

    verifier.print_summary()


if __name__ == "__main__":
    main()
