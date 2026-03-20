"""
modules/feature_extractor.py

Feature extraction utilities for MediSign (Stage 4).

This module provides a production-ready interface to extract per-frame
feature embeddings from preprocessed video tensors.

Primary API:
- FeatureExtractor(backbone='mobilenetv2', device='gpu')
  - extract(video_array, batch_size=16) -> np.ndarray

Notes:
- Input expected: np.ndarray with shape (60, 224, 224, 3) for a single video
  or (N, 60, 224, 224, 3) for N videos.
- Output: features with shape (60, feature_dim) or (N, 60, feature_dim)
  where feature_dim depends on backbone (1280 for MobileNetV2/EfficientNetB0).
"""

from __future__ import annotations

import os
from typing import Optional, Tuple

import numpy as np

import tensorflow as tf


def _build_backbone(
    name: str = "mobilenetv2", input_shape: Tuple[int, int, int] = (224, 224, 3)
) -> tf.keras.Model:
    """Build and return a backbone model that maps images -> feature vectors.

    Supported names: 'mobilenetv2', 'efficientnetb0'
    The returned model has output shape (feature_dim,) per input image.
    """
    name = name.lower()
    if name == "mobilenetv2":
        base = tf.keras.applications.MobileNetV2(
            weights="imagenet",
            include_top=False,
            input_shape=input_shape,
            pooling="avg",
        )
        feature_dim = 1280
    elif name == "efficientnetb0":
        base = tf.keras.applications.EfficientNetB0(
            weights="imagenet",
            include_top=False,
            input_shape=input_shape,
            pooling="avg",
        )
        # EfficientNetB0 final feature dim is 1280 as well
        feature_dim = 1280
    else:
        raise ValueError(f"Unsupported backbone: {name}")

    # Freeze weights
    base.trainable = False

    # Ensure output is a 1D feature vector per image
    inputs = base.input
    outputs = base.output
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name=f"fe_{name}")
    model._feature_dim = feature_dim  # attach attribute for convenience
    return model


class FeatureExtractor:
    """Feature extractor wrapper.

    Example:
        ext = FeatureExtractor(backbone='mobilenetv2', device='gpu')
        feats = ext.extract(video_array, batch_size=16)
    """

    def __init__(
        self, backbone: str = "mobilenetv2", device: Optional[str] = "gpu"
    ) -> None:
        self.backbone_name = backbone.lower()
        # Device selection: 'cpu' or 'gpu' (default: gpu if available)
        if device is None:
            device = "gpu"
        device = device.lower()
        if device not in ("cpu", "gpu"):
            raise ValueError("device must be 'cpu' or 'gpu'")

        # Resolve actual device name
        if device == "gpu" and tf.config.list_physical_devices("GPU"):
            self._device = "/GPU:0"
        else:
            self._device = "/CPU:0"

        # Build model under selected device
        with tf.device(self._device):
            self.model = _build_backbone(self.backbone_name, input_shape=(224, 224, 3))

        # feature dimension
        self.feature_dim = getattr(
            self.model, "_feature_dim", int(self.model.output_shape[-1])
        )

    def extract(self, video_array: np.ndarray, batch_size: int = 16) -> np.ndarray:
        """Extract per-frame features from a preprocessed video tensor.

        Args:
            video_array: np.ndarray, shape (60,224,224,3) for single video or (N,60,224,224,3)
            batch_size: int, number of frames to process per batch.

        Returns:
            np.ndarray of shape (60, feature_dim) or (N, 60, feature_dim)
        """
        arr = np.asarray(video_array)
        if arr.ndim == 4:
            # single video: (60, H, W, C)
            single = True
            if arr.shape[0] != 60:
                raise AssertionError(f"Expected 60 frames, got {arr.shape[0]}")
            frames = arr
        elif arr.ndim == 5:
            # batch of videos: (N,60,H,W,C)
            single = False
            if arr.shape[1] != 60:
                raise AssertionError(
                    f"Expected 60 frames per video, got {arr.shape[1]}"
                )
            # reshape to list of frames with video grouping later
            N = arr.shape[0]
            frames = arr.reshape((-1,) + arr.shape[2:])  # (N*60, H, W, C)
        else:
            raise AssertionError(
                "Input must have shape (60,224,224,3) or (N,60,224,224,3)"
            )

        # Assert spatial size
        if frames.shape[1:3] != (224, 224):
            raise AssertionError(
                f"Expected spatial size 224x224, got {frames.shape[1:3]}"
            )
        if frames.shape[3] != 3:
            raise AssertionError(f"Expected 3 channels, got {frames.shape[3]}")

        # Prepare batches
        num_frames = frames.shape[0]
        features = []

        # Use device context for inference
        with tf.device(self._device):
            for start in range(0, num_frames, batch_size):
                end = min(start + batch_size, num_frames)
                batch = frames[start:end].astype(np.float32)
                # Model expects inputs in range [0,255] with preprocessing or scaled as imagenet preprocessing
                # Our preprocessing scaled to [0,1], so rescale back to [0,255] and apply model-specific preprocess
                batch_255 = batch * 255.0

                if self.backbone_name == "mobilenetv2":
                    batch_pre = tf.keras.applications.mobilenet_v2.preprocess_input(
                        batch_255
                    )
                elif self.backbone_name == "efficientnetb0":
                    batch_pre = tf.keras.applications.efficientnet.preprocess_input(
                        batch_255
                    )
                else:
                    batch_pre = batch_255

                # Run inference
                preds = self.model(batch_pre, training=False)
                preds_np = preds.numpy()
                features.append(preds_np)

        features = np.concatenate(features, axis=0)  # (num_frames, feature_dim)

        if single:
            assert features.shape[0] == 60
            return features  # (60, feature_dim)
        else:
            # reshape back to (N,60,feature_dim)
            N = arr.shape[0]
            return features.reshape((N, 60, self.feature_dim))


def _cli_main(argv):
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract per-frame features from preprocessed video (.npy) using a CNN backbone."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to preprocessed .npy file or .npz containing 'arr'",
    )
    parser.add_argument(
        "--backbone", default="mobilenetv2", choices=("mobilenetv2", "efficientnetb0")
    )
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--device", default="gpu", choices=("gpu", "cpu"))
    parser.add_argument("--out", help="Optional output .npy file to save features")

    args = parser.parse_args(argv)

    # Load input
    data = None
    if args.input.endswith(".npy"):
        data = np.load(args.input)
    elif args.input.endswith(".npz"):
        loaded = np.load(args.input)
        # prefer key 'arr' or first array
        if "arr" in loaded:
            data = loaded["arr"]
        else:
            # pick first
            data = loaded[list(loaded.files)[0]]
    else:
        raise RuntimeError(
            "Input must be .npy or .npz file containing preprocessed video tensor"
        )

    ext = FeatureExtractor(backbone=args.backbone, device=args.device)
    feats = ext.extract(data, batch_size=args.batch_size)
    print(f"Extracted features shape: {feats.shape}, dtype={feats.dtype}")

    if args.out:
        np.save(args.out, feats)
        print(f"Saved features to {args.out}")


if __name__ == "__main__":
    import sys

    _cli_main(sys.argv[1:])
