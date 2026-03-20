#!/usr/bin/env python
"""Wait for features and then train model"""

import time
from pathlib import Path
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

features_dir = Path("dataset/features")
expected_count = 239


def count_features():
    return len(list(features_dir.rglob("*.npy")))


logger.info("Waiting for feature extraction to complete...")
logger.info(f"Expected features: {expected_count}")

prev_count = 0
while True:
    current_count = count_features()

    if current_count != prev_count:
        pct = (current_count / expected_count) * 100
        logger.info(f"Features: {current_count}/{expected_count} ({pct:.1f}%)")
        prev_count = current_count

    if current_count >= expected_count - 5:  # Allow small tolerance
        logger.info("✅ Feature extraction complete!")
        break

    time.sleep(10)

logger.info("\n" + "=" * 70)
logger.info("Starting model training...")
logger.info("=" * 70 + "\n")

# Run training
result = subprocess.run(["python", "scripts/4_train_medical.py"], cwd=".")

if result.returncode == 0:
    logger.info("✅ Model training complete!")
    logger.info("\nDeploying updated model...")
    subprocess.run(["python", "app_medical.py"])
else:
    logger.error("❌ Model training failed")
