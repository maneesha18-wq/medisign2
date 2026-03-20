"""Sequence model: stacked BiLSTM + attention for per-frame feature sequences.

Provides a helper to build a Keras Model for sequence classification.
"""

from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers
from keras.saving import register_keras_serializable


@register_keras_serializable(package="medisign")
class AttentionLayer(layers.Layer):
    """Simple attention mechanism over time steps.

    Given inputs of shape (batch, time, hidden), computes attention weights
    over the time axis and returns the context vector of shape (batch, hidden).
    """

    def __init__(self, units: int = 128, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        # let Keras know this layer can handle masks
        self.supports_masking = True

    def build(self, input_shape):
        hidden = int(input_shape[-1])
        # trainable projection for attention
        self.W = self.add_weight(
            name="W", shape=(hidden, self.units), initializer="glorot_uniform"
        )
        self.v = self.add_weight(
            name="v", shape=(self.units,), initializer="glorot_uniform"
        )
        super().build(input_shape)

    def call(self, inputs, mask=None, training=None):
        # inputs: (batch, time, hidden)
        # score = v^T tanh(inputs @ W)
        # shape => (batch, time, units) -> (batch, time)
        proj = tf.tensordot(inputs, self.W, axes=[[2], [0]])  # (batch, time, units)
        score = tf.tensordot(tf.tanh(proj), self.v, axes=[[2], [0]])  # (batch, time)

        if mask is not None:
            # mask: (batch, time)
            score += (1.0 - tf.cast(mask, tf.float32)) * -1e9

        weights = tf.nn.softmax(score, axis=1)  # (batch, time)
        weights_expanded = tf.expand_dims(weights, axis=-1)  # (batch, time, 1)
        context = tf.reduce_sum(inputs * weights_expanded, axis=1)  # (batch, hidden)
        return context

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"units": self.units})
        return cfg


def build_sequence_model(
    time_steps: int = 60,
    feat_dim: int = 1280,
    num_classes: int = 30,
    lstm_units: int = 256,
    dropout: float = 0.2,
) -> tf.keras.Model:
    """Builds and returns a Keras Model with stacked BiLSTM + attention.

    Args:
        time_steps: Number of frames/time steps per sample.
        feat_dim: Dimensionality of per-frame features.
        num_classes: Number of output classes.
        lstm_units: Number of units in each LSTM (per direction).
        dropout: Dropout rate applied inside LSTM layers.

    Returns:
        Compiled Keras Model (not compiled here; caller may compile).
    """

    inputs = layers.Input(shape=(time_steps, feat_dim), name="features")

    x = layers.Bidirectional(
        layers.LSTM(lstm_units, return_sequences=True, dropout=dropout), name="bilstm_1"
    )(inputs)

    x = layers.Bidirectional(
        layers.LSTM(lstm_units, return_sequences=True, dropout=dropout), name="bilstm_2"
    )(x)

    # Attention over time
    context = AttentionLayer(units=256, name="attention")(x)

    x = layers.Dense(128, activation="relu", name="fc1")(context)
    x = layers.Dropout(0.3, name="dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="bilstm_attention")
    return model


if __name__ == "__main__":
    # quick sanity: build and print summary
    m = build_sequence_model()
    m.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )
    m.summary()
