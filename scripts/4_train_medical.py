"""
Step 4: Train Medical Sign Language Model

Retrains BiLSTM+Attention model on real medical sign language features
with proper medical term labels.
"""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import sys
import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Tuple, List, Dict
import argparse
import logging
from datetime import datetime
import yaml

sys.path.insert(0, ".")
from modules.sequence_model import build_sequence_model, AttentionLayer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MedicalSignLanguageTrainer:
    """Train BiLSTM+Attention model on medical sign language data"""

    def __init__(self, config_path: str = "config/training_config.yaml"):
        """Load training configuration"""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.device = self.config["training"]["device"]
        logger.info(f"Using device: {self.device}")

    def load_features_and_labels(
        self, features_dir: str, medical_terms: List[str]
    ) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Load features and labels from organized directories

        Expected structure:
        features_dir/
        ├── heart_attack/
        │   ├── sample_01.npy
        │   ├── sample_02.npy
        │   └── ...
        ├── diabetes/
        └── ...
        """
        print("\nLoading features and labels...")

        features_list = []
        labels_list = []
        label_to_idx = {term: idx for idx, term in enumerate(medical_terms)}
        idx_to_label = {idx: term for term, idx in label_to_idx.items()}

        features_path = Path(features_dir)
        if not features_path.exists():
            raise FileNotFoundError(f"Features directory not found: {features_dir}")

        for term in medical_terms:
            term_dir = features_path / term
            if not term_dir.exists():
                logger.warning(f"No data for term: {term}")
                continue

            npy_files = sorted(term_dir.glob("*.npy"))
            logger.info(f"  {term}: {len(npy_files)} samples")

            for npy_file in npy_files:
                features = np.load(npy_file)

                # Validate shape
                if features.shape != (60, 1280):
                    logger.warning(f"Invalid shape {features.shape} for {npy_file}")
                    continue

                features_list.append(features)
                labels_list.append(label_to_idx[term])

        # Stack into arrays
        X = np.stack(features_list, axis=0)  # (N, 60, 1280)
        y = np.array(labels_list, dtype=np.int32)  # (N,)

        # Convert labels to one-hot
        y_onehot = tf.keras.utils.to_categorical(y, num_classes=len(medical_terms))

        logger.info(
            f"Loaded {X.shape[0]} samples, {X.shape[1]} timesteps, {X.shape[2]} features"
        )

        return X, y_onehot, idx_to_label

    def create_train_val_split(
        self, X: np.ndarray, y: np.ndarray, train_split: float = 0.7
    ):
        """Create train/validation split"""
        indices = np.arange(len(X))
        np.random.shuffle(indices)

        train_size = int(len(X) * train_split)

        train_idx = indices[:train_size]
        val_idx = indices[train_size:]

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        return (X_train, y_train), (X_val, y_val)

    def train_model(
        self,
        features_dir: str,
        medical_terms: List[str],
        output_model: str = "models/sequence_model_medical.keras",
    ):
        """
        Train the complete model
        """
        print("\n" + "=" * 70)
        print("STEP 4: TRAINING MEDICAL SIGN LANGUAGE MODEL")
        print("=" * 70)

        # Load data
        X, y, idx_to_label = self.load_features_and_labels(features_dir, medical_terms)

        # Split data
        (X_train, y_train), (X_val, y_val) = self.create_train_val_split(X, y)
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Val set: {X_val.shape[0]} samples")

        num_classes = len(medical_terms)
        time_steps = X_train.shape[1]
        feat_dim = X_train.shape[2]

        # Build model
        logger.info(f"Building model for {num_classes} medical terms...")
        model = build_sequence_model(
            time_steps=time_steps,
            feat_dim=feat_dim,
            num_classes=num_classes,
            lstm_units=self.config["training"]["lstm_units"],
            dropout=self.config["training"].get("dropout_rate", 0.2),
        )

        model.summary()

        # Compile
        model.compile(
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=self.config["training"]["learning_rate"]
            ),
            loss=self.config["training"]["loss"],
            metrics=self.config["training"]["metrics"],
        )

        # Callbacks
        callbacks = []

        if self.config["training"]["early_stopping"]["enabled"]:
            callbacks.append(
                tf.keras.callbacks.EarlyStopping(
                    monitor=self.config["training"]["early_stopping"]["monitor"],
                    patience=self.config["training"]["early_stopping"]["patience"],
                    restore_best_weights=True,
                )
            )

        if self.config["training"]["lr_schedule"]["enabled"]:
            callbacks.append(
                tf.keras.callbacks.ReduceLROnPlateau(
                    factor=self.config["training"]["lr_schedule"]["factor"],
                    patience=self.config["training"]["lr_schedule"]["patience"],
                    verbose=1,
                )
            )

        # Train
        logger.info("Starting training...")
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=self.config["training"]["epochs"],
            batch_size=self.config["training"]["batch_size"],
            callbacks=callbacks,
            verbose=1,
        )

        # Save model
        Path(output_model).parent.mkdir(parents=True, exist_ok=True)
        model.save(output_model)
        logger.info(f"Model saved: {output_model}")

        # Save label mapping
        label_map_path = "models/medical_terms_map.json"
        with open(label_map_path, "w") as f:
            json.dump(
                {
                    "idx_to_label": idx_to_label,
                    "label_to_idx": {v: k for k, v in idx_to_label.items()},
                    "num_classes": num_classes,
                    "medical_terms": medical_terms,
                },
                f,
                indent=2,
            )
        logger.info(f"Label mapping saved: {label_map_path}")

        # Print summary
        self._print_summary(model, history, X_train, X_val, medical_terms)

        return model, history, idx_to_label

    def _print_summary(self, model, history, X_train, X_val, medical_terms):
        """Print training summary"""
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        print(f"Model parameters: {model.count_params():,}")
        print(f"Training samples: {X_train.shape[0]}")
        print(f"Validation samples: {X_val.shape[0]}")
        print(f"Medical terms: {len(medical_terms)}")
        print(f"Final train loss: {history.history['loss'][-1]:.4f}")
        print(f"Final val loss: {history.history['val_loss'][-1]:.4f}")
        if "accuracy" in history.history:
            print(f"Final train accuracy: {history.history['accuracy'][-1]:.4f}")
            print(f"Final val accuracy: {history.history['val_accuracy'][-1]:.4f}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Train medical sign language model")
    parser.add_argument(
        "--features-dir",
        default="dataset/features",
        help="Directory with extracted features",
    )
    parser.add_argument(
        "--output-model",
        default="models/sequence_model_medical.keras",
        help="Output model path",
    )
    parser.add_argument(
        "--config",
        default="config/training_config.yaml",
        help="Training configuration file",
    )
    parser.add_argument(
        "--medical-config",
        default="config/medical_terms.json",
        help="Medical terms configuration",
    )

    args = parser.parse_args()

    # Load medical terms
    with open(args.medical_config, "r") as f:
        config = json.load(f)
        medical_terms = [term["term"] for term in config["medical_terms"]]

    trainer = MedicalSignLanguageTrainer(config_path=args.config)
    trainer.train_model(args.features_dir, medical_terms, args.output_model)


if __name__ == "__main__":
    main()
