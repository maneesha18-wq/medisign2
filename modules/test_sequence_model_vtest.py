"""Smoke test for the BiLSTM+Attention sequence model.

Builds a small synthetic dataset, runs one training epoch, and prints
loss/accuracy and a PASS line on completion.
"""

from __future__ import annotations

import numpy as np
import tensorflow as tf

from modules.sequence_model import build_sequence_model


def run_smoke():
    # synthetic dataset: 5 samples, 60 frames, 1280 features
    N = 5
    T = 60
    F = 1280
    num_classes = 3

    np.random.seed(0)
    X = np.random.randn(N, T, F).astype(np.float32)
    y = np.random.randint(0, num_classes, size=(N,)).astype(np.int32)

    model = build_sequence_model(time_steps=T, feat_dim=F, num_classes=num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    history = model.fit(X, y, epochs=1, batch_size=2, verbose=1)

    # report final metrics
    loss = history.history.get("loss", [None])[-1]
    acc = history.history.get("accuracy", [None])[-1]
    print(f"Final loss: {loss}")
    print(f"Final accuracy: {acc}")
    print("PASS: sequence model smoke test completed")


if __name__ == "__main__":
    run_smoke()
