"""modules/smoke_vtest.py

Quick smoke test for dataset/samples/vtest.avi using OpenCV.

Prints:
 - total frame count
 - FPS
 - width x height
 - first frame read success (True/False)

Exits non-zero if any hard-gate check fails.
"""

from __future__ import annotations

import sys
import os

import cv2


def main(path: str) -> int:
    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}")
        return 2

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"ERROR: cannot open video: {path}")
        return 3

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    ret, frame = cap.read()
    first_ok = bool(ret)

    print(frame_count)
    print(fps)
    print(f"{width}x{height}")
    print(first_ok)

    # Hard-gate validations
    errors = []
    if frame_count <= 0:
        errors.append("frame_count<=0")
    if not (fps and fps > 0):
        errors.append("fps<=0 or invalid")
    if width <= 0 or height <= 0:
        errors.append("invalid dimensions")
    if not first_ok:
        errors.append("first frame read failed")

    cap.release()

    if errors:
        print("VALIDATION: FAIL")
        print("REASONS:", ", ".join(errors))
        return 4

    print("VALIDATION: PASS - video looks good and ready for preprocessing")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smoke_vtest.py <path/to/vtest.avi>")
        sys.exit(1)

    path = sys.argv[1]
    rc = main(path)
    sys.exit(rc)
