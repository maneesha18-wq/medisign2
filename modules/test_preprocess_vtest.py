"""Test runner for modules.preprocessing.preprocess_video on vtest.avi.

This script prints:
 - output shape
 - dtype
 - min / max pixel values
 - number of non-zero frames

And asserts the hard gates specified by the user.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import sys
from pathlib import Path

# Ensure project root is on sys.path so we can import the 'modules' package when
# running this script directly.
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules import preprocessing


def main(video_path: str) -> int:
    arr = preprocessing.preprocess_video(
        video_path, num_frames=60, target_size=(224, 224)
    )

    shape = arr.shape
    dtype = arr.dtype
    vmin = float(np.min(arr))
    vmax = float(np.max(arr))
    # count frames that are not entirely zero
    nonzero_frames = int(np.sum(np.any(arr != 0.0, axis=(1, 2, 3))))

    print(shape)
    print(dtype)
    print(vmin, vmax)
    print(nonzero_frames)

    # Assertions (hard gates)
    assert shape == (60, 224, 224, 3), f"Unexpected shape: {shape}"
    assert dtype == np.float32, f"Unexpected dtype: {dtype}"
    assert (
        0.0 <= vmin <= 1.0 and 0.0 <= vmax <= 1.0
    ), f"Pixel values out of [0,1]: min={vmin}, max={vmax}"

    print("PREPROCESSING VALIDATION: PASS — Stage 3 complete")
    return 0


if __name__ == "__main__":
    video = Path(__file__).resolve().parents[1] / "dataset" / "samples" / "vtest.avi"
    if not video.exists():
        print(f"Video not found: {video}")
        sys.exit(2)
    try:
        rc = main(str(video))
    except AssertionError as e:
        print("PREPROCESSING VALIDATION: FAIL")
        print("REASON:", e)
        sys.exit(3)
    except Exception as e:
        print("PREPROCESSING VALIDATION: ERROR")
        print(e)
        sys.exit(4)
    sys.exit(rc)
