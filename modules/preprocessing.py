"""
modules/preprocessing.py

Preprocessing utilities for MediSign (Stage 3).

Functions:
- preprocess_video(video_path, num_frames=60, target_size=(224,224))
  -> loads video, extracts exactly num_frames frames, resizes to target_size,
     normalizes to 0-1, pads with black frames if needed, returns numpy array
     with shape (num_frames, H, W, 3) and dtype float32.

Usage (CLI):
  python -m modules.preprocessing --video path/to/video.mp4

This module has no external dependencies beyond OpenCV and NumPy.
"""

from __future__ import annotations

import cv2
import numpy as np
import os
import sys
from typing import Tuple


def _read_all_frames(video_path: str) -> list:
    """Read all frames from a video file and return list of BGR frames.

    Raises RuntimeError if the video cannot be opened.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    return frames


def _resize_frame(frame: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """Resize a frame (BGR) to size=(width, height) using INTER_AREA for shrinking."""
    width, height = size
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def preprocess_video(
    video_path: str, num_frames: int = 60, target_size: Tuple[int, int] = (224, 224)
) -> np.ndarray:
    """Load a video and return a NumPy array of shape (num_frames, H, W, 3), dtype float32.

    Steps:
    - Read all frames from video
    - If frames >= num_frames: sample evenly to get exactly num_frames frames
    - If frames < num_frames: take all frames and pad with black frames
    - Resize frames to target_size (width, height)
    - Convert BGR->RGB
    - Normalize pixel values to range [0, 1]

    Returns:
        np.ndarray with shape (num_frames, target_height, target_width, 3), dtype float32
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    frames = _read_all_frames(video_path)
    total = len(frames)

    if total == 0:
        # Return all-black frames
        h, w = target_size[1], target_size[0]
        return np.zeros((num_frames, h, w, 3), dtype=np.float32)

    # Choose indices
    if total >= num_frames:
        indices = np.linspace(0, total - 1, num_frames).astype(int)
        selected = [frames[i] for i in indices]
    else:
        # Use all frames, then pad later
        selected = frames.copy()

    processed = []
    for f in selected:
        # Resize (target_size is (width, height))
        resized = _resize_frame(f, target_size)
        # Convert BGR -> RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        # To float32 and normalize
        rgb = rgb.astype(np.float32) / 255.0
        processed.append(rgb)

    # Pad if needed
    if len(processed) < num_frames:
        h, w = target_size[1], target_size[0]
        n_missing = num_frames - len(processed)
        black = np.zeros((h, w, 3), dtype=np.float32)
        processed.extend([black] * n_missing)

    arr = np.stack(processed, axis=0)
    return arr


def save_numpy(array: np.ndarray, out_path: str):
    """Save a NumPy array to an .npy file (creates parent directories if needed)."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    np.save(out_path, array)


def _cli_main(argv: list):
    import argparse

    parser = argparse.ArgumentParser(
        description="Preprocess a video into fixed-length frame tensor."
    )
    parser.add_argument("--video", required=True, help="Path to input MP4 video")
    parser.add_argument(
        "--frames",
        type=int,
        default=60,
        help="Number of frames to extract (default: 60)",
    )
    parser.add_argument(
        "--size",
        type=int,
        nargs=2,
        default=(224, 224),
        help="Target width and height (default: 224 224)",
    )
    parser.add_argument(
        "--out", help="Optional .npy output path to save the processed array"
    )

    args = parser.parse_args(argv)

    arr = preprocess_video(
        args.video, num_frames=args.frames, target_size=(args.size[0], args.size[1])
    )
    print(
        f"Processed array shape: {arr.shape}, dtype={arr.dtype}, min={arr.min():.3f}, max={arr.max():.3f}"
    )

    if args.out:
        save_numpy(arr, args.out)
        print(f"Saved preprocessed array to {args.out}")


if __name__ == "__main__":
    _cli_main(sys.argv[1:])
