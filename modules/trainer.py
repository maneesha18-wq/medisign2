"""modules/trainer.py

Simple training utilities that consume pre-extracted per-frame features and
train a small classifier on top.

API highlights:
- train_from_arrays(features, labels, ...)
- CLI that accepts feature files / label files and saves a model to disk

Design:
- Accept feature tensors shaped (N, 60, 1280) or (60, 1280) for a single sample
- Collapse temporal dimension with GlobalAveragePooling1D -> (N, 1280)
- Small Dense head -> softmax
"""

from __future__ import annotations

import argparse
import os
from typing import Optional, Tuple

import numpy as np
import tensorflow as tf


def _ensure_batch_dim(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr)
    if arr.ndim == 4:
        # already (N,60,H,W,C) unexpected
        raise ValueError("Unexpected 4D array for features")
    if arr.ndim == 3:
        return arr
    if arr.ndim == 2:
        # single sample (60, feat_dim)
        return arr[np.newaxis, ...]
    raise ValueError(f"Unsupported feature array shape: {arr.shape}")


def build_classifier(input_shape: Tuple[int, int], num_classes: int) -> tf.keras.Model:
    # input_shape: (time, feat_dim) e.g. (60,1280)
    inputs = tf.keras.Input(shape=input_shape, name="features")
    # Collapse time dimension
    x = tf.keras.layers.GlobalAveragePooling1D()(inputs)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="feat_classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_from_arrays(
    features: np.ndarray,
    labels: np.ndarray,
    num_classes: int = 3,
    epochs: int = 10,
    batch_size: int = 8,
    device: Optional[str] = None,
    out: Optional[str] = None,
) -> Tuple[tf.keras.Model, tf.keras.callbacks.History]:
    """Train a small classifier from feature arrays.

    features: np.ndarray, shape (N, 60, feat_dim) or (60, feat_dim)
    labels: np.ndarray, shape (N,) or (1,)
    """
    arr = _ensure_batch_dim(features)
    if arr.ndim != 3:
        raise ValueError("features must be (N, time, feat_dim)")

    N = arr.shape[0]
    if labels is None:
        labels = np.zeros((N,), dtype=np.int32)
    labels = np.asarray(labels).reshape((-1,))

    # Device selection
    if device is None:
        device = "gpu" if tf.config.list_physical_devices("GPU") else "cpu"
    device_ctx = (
        "/GPU:0"
        if device == "gpu" and tf.config.list_physical_devices("GPU")
        else "/CPU:0"
    )

    with tf.device(device_ctx):
        model = build_classifier(
            input_shape=(arr.shape[1], arr.shape[2]), num_classes=num_classes
        )

        history = model.fit(
            arr, labels, epochs=epochs, batch_size=batch_size, verbose=2
        )

        if out:
            os.makedirs(os.path.dirname(out) or "models", exist_ok=True)
            model.save(out)

    return model, history


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Train classifier on pre-extracted features"
    )
    parser.add_argument(
        "--features",
        required=True,
        help="Path to .npy features file (N,60,feat) or (60,feat)",
    )
    parser.add_argument(
        "--labels", help="Optional .npy labels file (N,) or omitted to use dummy labels"
    )
    parser.add_argument("--num-classes", type=int, default=3)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--device", choices=("cpu", "gpu"), default=None)
    parser.add_argument("--out", default="models/feat_classifier.h5")

    args = parser.parse_args(argv)

    feats = np.load(args.features)
    labels = None
    if args.labels:
        labels = np.load(args.labels)

    model, history = train_from_arrays(
        feats,
        labels,
        num_classes=args.num_classes,
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
        out=args.out,
    )
    print("Training finished. Model saved to", args.out)


if __name__ == "__main__":
    _cli_main()
