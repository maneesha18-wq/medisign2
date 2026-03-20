"""
Step 3: Extract Features using MobileNetV2

Converts preprocessed frames (60, 224, 224, 3) into (60, 1280) features
using pre-trained MobileNetV2 CNN.
"""

import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
from pathlib import Path
import logging
from typing import Optional
import argparse
from tqdm import tqdm

sys.path.insert(0, ".")
from modules.feature_extractor import FeatureExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FeatureExtractionPipeline:
    """Extract deep learning features from preprocessed videos"""

    def __init__(self, backbone: str = "mobilenetv2", device: str = "gpu"):
        """
        Initialize feature extractor

        Args:
            backbone: CNN backbone ("mobilenetv2" recommended)
            device: "gpu" or "cpu"
        """
        self.backbone = backbone
        self.device = device

        logger.info(f"Initializing feature extractor: {backbone}")
        self.extractor = FeatureExtractor(backbone=backbone, device=device)

    def extract_features_from_video(
        self, video_array: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Extract features from preprocessed video array

        Args:
            video_array: Shape (60, 224, 224, 3) with values in [0, 1]

        Returns:
            Shape (60, 1280) feature array or None if error
        """
        try:
            features = self.extractor.extract(video_array)
            return features
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return None

    def extract_features_dataset(
        self, input_dir: str, output_dir: str, skip_existing: bool = True
    ):
        """
        Extract features for entire dataset

        Args:
            input_dir: Directory with preprocessed videos (60, 224, 224, 3)
            output_dir: Where to save features (60, 1280)
            skip_existing: Skip files that already exist
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return

        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "total_size_mb": 0,
        }

        # Process each medical term folder
        for term_dir in sorted(input_path.iterdir()):
            if not term_dir.is_dir():
                continue

            term = term_dir.name
            output_term_dir = output_path / term
            output_term_dir.mkdir(exist_ok=True)

            logger.info(f"\nExtracting features for: {term}")

            npy_files = sorted(term_dir.glob("*.npy"))

            for npy_file in tqdm(npy_files, desc=f"  {term}"):
                output_file = output_term_dir / npy_file.name

                stats["total"] += 1

                # Skip if exists
                if output_file.exists() and skip_existing:
                    stats["skipped"] += 1
                    continue

                try:
                    # Load preprocessed video
                    video_array = np.load(npy_file)

                    # Extract features
                    features = self.extract_features_from_video(video_array)

                    if features is not None and features.shape == (60, 1280):
                        np.save(output_file, features)
                        stats["success"] += 1
                        stats["total_size_mb"] += output_file.stat().st_size / (
                            1024 * 1024
                        )
                    else:
                        logger.error(f"Invalid features shape from {npy_file}")
                        stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Error processing {npy_file}: {e}")
                    stats["failed"] += 1

        # Print summary
        self._print_summary(stats, output_path)

    def _print_summary(self, stats, output_dir):
        """Print feature extraction summary"""
        print("\n" + "=" * 70)
        print("FEATURE EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"Total videos processed: {stats['total']}")
        print(f"Successfully extracted: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Total output size: {stats['total_size_mb']:.2f} MB")
        print(f"\nOutput directory: {output_dir}")
        print(f"Feature format: (60, 1280) float32 arrays")
        print(f"Backbone: {self.backbone}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Extract features using MobileNetV2")
    parser.add_argument(
        "--input-dir",
        default="dataset/preprocessed",
        help="Directory with preprocessed videos (60, 224, 224, 3)",
    )
    parser.add_argument(
        "--output-dir",
        default="dataset/features",
        help="Output directory for features (60, 1280)",
    )
    parser.add_argument(
        "--backbone",
        default="mobilenetv2",
        choices=["mobilenetv2"],
        help="CNN backbone for features",
    )
    parser.add_argument(
        "--device", default="gpu", choices=["gpu", "cpu"], help="Device to use"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip files that already exist",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("STEP 3: FEATURE EXTRACTION")
    print("=" * 70)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Backbone: {args.backbone}")
    print(f"Device: {args.device}")
    print("=" * 70 + "\n")

    pipeline = FeatureExtractionPipeline(backbone=args.backbone, device=args.device)

    pipeline.extract_features_dataset(
        args.input_dir, args.output_dir, skip_existing=args.skip_existing
    )


if __name__ == "__main__":
    main()
