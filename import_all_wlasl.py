#!/usr/bin/env python
"""Import ALL WLASL videos for processing"""

import json
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

wlasl_videos_path = Path(r"C:\Users\vishn\Downloads\archive\videos")
output_path = Path("dataset/raw_videos")

# Create output directory
output_path.mkdir(parents=True, exist_ok=True)

logger.info("=" * 70)
logger.info("WLASL DATASET IMPORT - ALL VIDEOS")
logger.info("=" * 70)

# Find all video files
all_videos = list(wlasl_videos_path.glob("*.mp4"))
logger.info(f"\nFound {len(all_videos)} total WLASL videos")

# Import ALL videos for processing
imported_count = 0
for video_file in all_videos:
    try:
        # Copy video to output with preserved name
        output_file = output_path / video_file.name
        shutil.copy2(video_file, output_file)
        imported_count += 1

        if imported_count % 1000 == 0:
            logger.info(f"  Imported {imported_count}/{len(all_videos)} videos...")
    except Exception as e:
        logger.warning(f"Failed to import {video_file.name}: {e}")

logger.info(f"\n✅ Imported {imported_count} WLASL videos to {output_path}")

# Count videos now available for training
all_videos_now = list(output_path.glob("*.mp4"))
youtube_videos = (
    len(list((Path("dataset/raw_videos") / "heart_attack").glob("*.mp4")))
    if (Path("dataset/raw_videos") / "heart_attack").exists()
    else 0
)

logger.info(f"\nDataset summary:")
logger.info(f"  - WLASL videos imported: {imported_count}")
logger.info(f"  - YouTube videos (existing): ~2")
logger.info(f"  - Total videos available: {len(all_videos_now)}")

logger.info("\n" + "=" * 70)
logger.info("NEXT STEPS")
logger.info("=" * 70)
logger.info(
    """
To train on the full WLASL dataset:

1. Preprocess videos (extract frames):
   python scripts/2_preprocess_videos.py

2. Extract features (MobileNetV2 encoding):
   python scripts/3_extract_features.py

3. Train model:
   python scripts/4_train_medical.py

4. Deploy:
   python app_medical.py

This will train on 11,000+ diverse sign language videos!
"""
)

logger.info("=" * 70)
