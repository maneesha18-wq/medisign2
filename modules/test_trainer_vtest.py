"""modules/test_trainer_vtest.py

Smoke test for the trainer module. Generates a synthetic dataset from a single
base (60,1280) feature array, creates labels, runs 1 epoch of training, and
prints final loss/accuracy and a PASS line on success.
"""

from __future__ import annotations

import numpy as np
import traceback

import sys
from pathlib import Path

# Ensure project root on path when running the script directly
proj_root = str(Path(__file__).resolve().parents[1])
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from modules import trainer


def main():
    try:
        # Create a base (60,1280) feature vector and generate N samples by adding noise
        base = np.random.RandomState(0).randn(60, 1280).astype(np.float32)
        N = 32
        X = np.stack(
            [
                base + 0.01 * np.random.randn(60, 1280).astype(np.float32)
                for _ in range(N)
            ],
            axis=0,
        )
        # 3 classes
        y = np.random.randint(0, 3, size=(N,))

        # Train for one epoch
        model, history = trainer.train_from_arrays(
            X, y, num_classes=3, epochs=1, batch_size=8, device="cpu", out=None
        )

        # Print final loss/acc
        last = history.history
        loss = last.get("loss")[-1] if "loss" in last else None
        acc = last.get("accuracy")[-1] if "accuracy" in last else None
        print(loss)
        print(acc)
        print("PASS: trainer smoke test completed")
    except Exception:
        print("FAIL: trainer smoke test raised an exception")
        traceback.print_exc()


if __name__ == "__main__":
    main()
