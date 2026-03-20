"""Full training script (separate from train.py to avoid previous corruption).

Behaves like the requested final training orchestration and fails fast if
insufficient real feature files are found.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
import tensorflow as tf

from modules.sequence_model import build_sequence_model

try:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, classification_report
except Exception:
    train_test_split = None
    confusion_matrix = None
    classification_report = None


def discover_feature_files(dataset_dir: str) -> List[Path]:
    p = Path(dataset_dir)
    return list(p.rglob("*.npy"))


def infer_label_from_path(p: Path) -> str:
    parent = p.parent.name
    if parent and parent.lower() not in {"dataset", "samples", ""}:
        return parent
    return p.stem.split("_")[0]


def load_dataset(
    files: List[Path], time_steps: int = 60, feat_dim: int = 1280
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    X = []
    y = []
    labels = []
    for p in files:
        try:
            arr = np.load(p)
        except Exception as e:
            print(f"Skipping {p}: load error: {e}")
            continue
        if arr.ndim != 2:
            print(f"Skipping {p}: unexpected array shape {arr.shape}")
            continue
        if arr.shape[0] == time_steps and arr.shape[1] == feat_dim:
            seq = arr
        elif arr.shape[1] == time_steps and arr.shape[0] == feat_dim:
            seq = arr.T
        else:
            print(
                f"Skipping {p}: shape {arr.shape} doesn't match expected ({time_steps},{feat_dim})"
            )
            continue
        lbl = infer_label_from_path(p)
        X.append(seq.astype(np.float32))
        y.append(lbl)
        labels.append(lbl)
    if not X:
        raise RuntimeError("No valid feature arrays found in dataset directory.")
    X = np.stack(X, axis=0)
    unique = sorted(set(labels))
    label2int = {l: i for i, l in enumerate(unique)}
    y_int = np.array([label2int[val] for val in y], dtype=np.int32)
    return X, y_int, unique


def make_datasets(
    X: np.ndarray, y: np.ndarray, batch_size: int, val_fraction: float = 0.2
):
    if train_test_split is None:
        raise RuntimeError(
            "scikit-learn is required for train/test split. Please install scikit-learn."
        )
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=val_fraction, stratify=y, random_state=42
    )
    train_ds = (
        tf.data.Dataset.from_tensor_slices((X_train, y_train))
        .shuffle(1024)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )
    val_ds = (
        tf.data.Dataset.from_tensor_slices((X_val, y_val))
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )
    return train_ds, val_ds


def save_history(history: tf.keras.callbacks.History, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    hist = {k: [float(x) for x in v] for k, v in history.history.items()}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    p = out_dir / f"history_{ts}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)
    print(f"Saved training history to {p}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default="dataset",
        help="Dataset root containing .npy feature files",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--device", type=str, default="cpu", help="Device to run on: 'cpu' or 'gpu'"
    )
    parser.add_argument(
        "--model-out", type=str, default="models/sequence_model_final.keras"
    )
    parser.add_argument("--log-dir", type=str, default="logs")
    parser.add_argument("--time-steps", type=int, default=60)
    parser.add_argument("--feat-dim", type=int, default=1280)
    args = parser.parse_args(argv)

    files = discover_feature_files(args.dataset)
    root_feat = Path("out_feats.npy")
    if root_feat.exists() and not files:
        files.append(root_feat)
    files = sorted(set(files))
    print(f"Found {len(files)} .npy feature files: {files}")

    X, y, label_names = load_dataset(
        files, time_steps=args.time_steps, feat_dim=args.feat_dim
    )
    num_classes = len(label_names)
    print(f"Loaded data: X={X.shape}, y={y.shape}, classes={num_classes}")

    MIN_SAMPLES = 30
    if X.shape[0] < MIN_SAMPLES:
        raise RuntimeError(
            f"Insufficient data: found {X.shape[0]} samples but require at least {MIN_SAMPLES} real samples to train.\n"
            "Please extract per-video features into dataset/<label>/*.npy and retry."
        )

    train_ds, val_ds = make_datasets(X, y, batch_size=args.batch_size)

    model = build_sequence_model(
        time_steps=args.time_steps, feat_dim=args.feat_dim, num_classes=num_classes
    )

    device_map = {"cpu": "/CPU:0", "gpu": "/GPU:0"}
    device = device_map.get(args.device.lower(), args.device)

    ckpt_dir = Path(args.model_out).parent
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = ckpt_dir / "best_sequence_model.keras"
    csv_log_dir = Path(args.log_dir)
    csv_log_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_log_dir / "training_log.csv"

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            str(checkpoint_path), save_best_only=True, monitor="val_loss"
        ),
        tf.keras.callbacks.CSVLogger(str(csv_path)),
    ]

    with tf.device(device):
        model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary()
        history = model.fit(
            train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks
        )

    out_path = Path(args.model_out).with_suffix(".keras")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(out_path)
    print(f"Saved model to {out_path}")

    save_history(history, Path(args.log_dir))

    try:
        from sklearn.metrics import confusion_matrix, classification_report
    except Exception:
        confusion_matrix = None
        classification_report = None

    if confusion_matrix is None:
        print(
            "sklearn required for confusion matrix; install scikit-learn to enable evaluation reports."
        )
    else:
        X_val = []
        y_val = []
        for xb, yb in val_ds.unbatch().batch(1):
            X_val.append(xb.numpy())
            y_val.append(int(yb.numpy()))
        if X_val:
            X_val = np.concatenate(X_val, axis=0)
            y_val = np.array(y_val, dtype=np.int32)
            preds = model.predict(X_val)
            y_pred = preds.argmax(axis=1)
            cm = confusion_matrix(y_val, y_pred)
            print("Confusion matrix (validation):")
            print(cm)
            print("Classification report:")
            print(classification_report(y_val, y_pred, target_names=label_names))

    print("PASS: full sequence model training completed")


if __name__ == "__main__":
    main()
