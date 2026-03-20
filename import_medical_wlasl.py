#!/usr/bin/env python
"""Import WLASL medical-related videos - smart selection"""

import json
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

wlasl_path = Path(r"C:\Users\vishn\Downloads\archive\videos")
metadata_path = Path(r"C:\Users\vishn\Downloads\archive\WLASL_v0.3.json")
output_base = Path("dataset/raw_videos")

output_base.mkdir(parents=True, exist_ok=True)

logger.info("=" * 70)
logger.info("WLASL DATASET IMPORT - MEDICAL VIDEOS")
logger.info("=" * 70)

# Medical keywords mapping
medical_categories = {
    "heart_attack": ["heart", "attack", "cardiac"],
    "diabetes": ["diabetes", "blood", "sugar"],
    "broken_arm": ["arm", "break", "fracture", "injury"],
    "fever": ["fever", "temperature", "sick"],
    "medication": ["medicine", "drug", "pill", "treatment"],
    "headache": ["headache", "head", "pain", "ache"],
    "hospital": ["hospital", "clinic", "medical", "health"],
    "surgeon": ["doctor", "surgeon", "physician", "nurse"],
    "emergency": ["emergency", "urgent", "crisis"],
    "pain": ["pain", "hurt", "ache", "suffer"],
}

# Load WLASL metadata
logger.info(f"Loading WLASL metadata from {metadata_path}...")
with open(metadata_path) as f:
    wlasl_data = json.load(f)

logger.info(f"Loaded {len(wlasl_data)} entries\n")

# Find and import medical videos
category_stats = {
    cat: {"found": 0, "imported": 0, "failed": 0} for cat in medical_categories
}

for entry in wlasl_data:
    gloss = entry["gloss"].lower()

    # Find matching medical category
    matched_category = None
    for category, keywords in medical_categories.items():
        if any(kw in gloss for kw in keywords):
            matched_category = category
            break

    if not matched_category:
        continue

    category_stats[matched_category]["found"] += 1

    # Create category directory
    category_dir = output_base / matched_category
    category_dir.mkdir(parents=True, exist_ok=True)

    # Import ALL instances of this sign
    for instance in entry.get("instances", []):
        video_id = instance.get("video_id")
        if not video_id:
            continue

        source_file = wlasl_path / f"{video_id}.mp4"

        if not source_file.exists():
            category_stats[matched_category]["failed"] += 1
            continue

        try:
            # Name: gloss_videoid.mp4
            target_file = category_dir / f"{gloss}_{video_id}.mp4"
            if not target_file.exists():
                shutil.copy2(source_file, target_file)
                category_stats[matched_category]["imported"] += 1
        except Exception as e:
            logger.warning(f"Failed to copy {video_id}.mp4: {e}")
            category_stats[matched_category]["failed"] += 1

# Display results
logger.info("\n" + "=" * 70)
logger.info("IMPORT RESULTS")
logger.info("=" * 70)

total_imported = 0
for category in sorted(medical_categories.keys()):
    stats = category_stats[category]
    total_imported += stats["imported"]
    status = "✓" if stats["imported"] > 0 else "✗"
    logger.info(
        f"{status} {category:20} Found:{stats['found']:3} Imported:{stats['imported']:3}"
    )

logger.info("-" * 70)
logger.info(f"✅ Total medical videos imported: {total_imported}\n")

# Verify YouTube videos are still there
youtube_count = 0
for cat_dir in output_base.glob("*/"):
    youtube_count += len(list(cat_dir.glob("*.mp4")))

logger.info(f"Total videos now available for training: {youtube_count}")

logger.info("\n" + "=" * 70)
logger.info("NEXT STEPS")
logger.info("=" * 70)
logger.info(
    """
Your dataset is ready! To train the model:

1. Preprocess videos (extract frames):
   python scripts/2_preprocess_videos.py

2. Extract features (MobileNetV2 encoding):
   python scripts/3_extract_features.py

3. Train model on medical + WLASL data:
   python scripts/4_train_medical.py

4. Deploy the improved model:
   python app_medical.py

This combines your YouTube videos with WLASL medical content!
"""
)
logger.info("=" * 70)
