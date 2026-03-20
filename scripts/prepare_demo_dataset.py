"""Prepare a demo dataset of per-video feature .npy files.

This script will:
 - Load `out_feats.npy` (if present) which should be shape (T, D) or (1,T,D)
 - Or, if absent, load `dataset/samples/preprocessed_vtest.npy` and run the feature extractor
 - Write N copies into `dataset/demo_label/` as `demo_{i:03d}.npy` with shape (T,D)

Usage: python scripts/prepare_demo_dataset.py --n 30 --label demo
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=30)
    parser.add_argument("--label", type=str, default="demo")
    args = parser.parse_args()

    out_feats = Path("out_feats.npy")
    preproc = Path("dataset/samples/preprocessed_vtest.npy")
    feats = None

    if out_feats.exists():
        arr = np.load(out_feats)
        # allow (T,D) or (1,T,D)
        if arr.ndim == 2:
            feats = arr
        elif arr.ndim == 3 and arr.shape[0] == 1:
            feats = arr[0]
        else:
            raise RuntimeError(f"Unsupported shape in {out_feats}: {arr.shape}")
    elif preproc.exists():
        # lazy import to avoid heavy deps when not needed
        from modules.feature_extractor import FeatureExtractor

        pre = np.load(preproc)
        if pre.ndim == 3:
            # expect (T,H,W,C)
            fe = FeatureExtractor(backbone="mobilenetv2", device="cpu")
            feats = fe.extract(pre)
        else:
            raise RuntimeError(f"Unsupported preprocessed shape: {pre.shape}")
    else:
        raise RuntimeError(
            "No out_feats.npy or preprocessed_vtest.npy found to create demo dataset."
        )

    out_dir = Path("dataset") / args.label
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.n):
        p = out_dir / f"{args.label}_{i:03d}.npy"
        np.save(p, feats)
    print(f"Wrote {args.n} feature files to {out_dir}")


if __name__ == "__main__":
    main()
