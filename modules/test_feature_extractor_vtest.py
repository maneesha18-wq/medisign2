"""Smoke test for modules.feature_extractor.FeatureExtractor using vtest.avi preprocessed tensor.

Prints and asserts the following:
- feature tensor shape
- dtype
- per-frame feature dimensionality
- total frames processed

Asserts:
- number of feature rows == 60
- no NaNs or infs

Exits non-zero on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure project root is importable
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules import preprocessing
from modules.feature_extractor import FeatureExtractor


def main(video_path: str) -> int:
    # Preprocess video to (60,224,224,3)
    arr = preprocessing.preprocess_video(
        video_path, num_frames=60, target_size=(224, 224)
    )

    if arr.shape != (60, 224, 224, 3):
        print(f"Unexpected preprocessed shape: {arr.shape}")
        return 2

    # Instantiate extractor (device auto: GPU if available else CPU)
    ext = FeatureExtractor(backbone="mobilenetv2", device=None)

    feats = ext.extract(arr, batch_size=16)

    # Print diagnostics
    print(feats.shape)
    print(feats.dtype)
    per_frame_dim = int(feats.shape[-1])
    total_frames = int(feats.shape[0])
    print(per_frame_dim)
    print(total_frames)

    # Assertions
    if total_frames != 60:
        print("ERROR: total_frames != 60")
        return 3

    if np.isnan(feats).any() or np.isinf(feats).any():
        print("ERROR: NaN or Inf detected in features")
        return 4

    print("FEATURE EXTRACTION VALIDATION: PASS — Stage 4 complete")
    return 0


if __name__ == "__main__":
    video = Path(__file__).resolve().parents[1] / "dataset" / "samples" / "vtest.avi"
    if not video.exists():
        print(f"Video not found: {video}")
        sys.exit(2)
    rc = main(str(video))
    sys.exit(rc)
