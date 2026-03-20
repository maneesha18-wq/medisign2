#!/usr/bin/env python3
"""
WLASL Dataset Integration for MediSign

Organize and import WLASL (World Deaf Sign Language) videos into MediSign dataset.
Maps WLASL signs to medical term categories, processes videos, and integrates with
existing downloaded data.

Usage:
    python organize_wlasl_data.py --wlasl-path /path/to/wlasl --output dataset/raw_videos
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Medical terms mapped to WLASL sign keywords
MEDICAL_TERM_MAPPING = {
    "heart_attack": ["heart", "attack", "cardiac", "chest", "pain", "emergency"],
    "diabetes": ["diabetes", "sugar", "blood", "glucose", "insulin", "disease"],
    "broken_arm": ["arm", "break", "broken", "fracture", "bone", "injury", "shoulder"],
    "fever": ["fever", "temperature", "hot", "sick", "illness", "disease"],
    "medication": [
        "medicine",
        "drug",
        "pill",
        "tablet",
        "medication",
        "treatment",
        "pharmaceutical",
    ],
    "headache": ["headache", "head", "pain", "migraine", "ache", "hurt"],
    "hospital": [
        "hospital",
        "clinic",
        "medical",
        "health",
        "care",
        "facility",
        "emergency",
    ],
    "surgeon": ["doctor", "surgeon", "physician", "medical", "professional", "nurse"],
    "emergency": ["emergency", "urgent", "urgent", "critical", "alert", "danger"],
    "pain": ["pain", "hurt", "ache", "suffer", "discomfort", "injury"],
}


class WLASLOrganizer:
    def __init__(self, wlasl_path, output_path="dataset/raw_videos"):
        self.wlasl_path = Path(wlasl_path)
        self.output_path = Path(output_path)
        self.stats = defaultdict(lambda: {"added": 0, "skipped": 0})

    def find_wlasl_metadata(self):
        """Find WLASL metadata JSON file"""
        # Common WLASL metadata locations
        possible_paths = [
            self.wlasl_path / "WLASL_v0.3.json",
            self.wlasl_path / "WLASL.json",
            self.wlasl_path / "data" / "WLASL_v0.3.json",
            self.wlasl_path / "metadata.json",
            self.wlasl_path.parent / "WLASL_v0.3.json",  # Check parent directory
            self.wlasl_path.parent / "WLASL.json",  # Check parent directory
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Found WLASL metadata: {path}")
                return path

        logger.warning("WLASL metadata not found in:")
        for path in possible_paths:
            logger.warning(f"  - {path}")
        return None

    def find_video_file(self, video_id):
        """Find video file for given video ID in WLASL directory"""
        # Common WLASL video locations
        common_structures = [
            self.wlasl_path / "videos" / f"{video_id}.mp4",
            self.wlasl_path / f"{video_id}.mp4",
            self.wlasl_path / "WLASL_data" / f"{video_id}.mp4",
        ]

        for potential_path in common_structures:
            if potential_path.exists():
                return potential_path

        return None

    def map_sign_to_medical_term(self, sign_text):
        """Map WLASL sign text to medical term category"""
        sign_text_lower = sign_text.lower()

        # Check each medical term's keywords
        for medical_term, keywords in MEDICAL_TERM_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in sign_text_lower:
                    return medical_term

        return None

    def organize_wlasl(self):
        """Main workflow: load WLASL data and organize into medical terms"""
        logger.info("=" * 70)
        logger.info("WLASL DATASET INTEGRATION")
        logger.info("=" * 70)

        # Find metadata
        metadata_path = self.find_wlasl_metadata()
        if not metadata_path:
            logger.error("Cannot find WLASL metadata. Please check WLASL path.")
            return False

        # Load metadata
        try:
            with open(metadata_path, "r") as f:
                wlasl_data = json.load(f)
            logger.info(f"Loaded WLASL metadata: {len(wlasl_data)} entries")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load metadata: {e}")
            return False

        # Create output directories
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Process each WLASL entry
        processed = 0
        medical_matches = defaultdict(list)

        for entry in wlasl_data:
            # Get sign information
            sign_id = entry.get("id")
            sign_text = entry.get("text") or entry.get("gloss", "")

            if not sign_text:
                continue

            # Map to medical term
            medical_term = self.map_sign_to_medical_term(sign_text)
            if not medical_term:
                continue

            # Get video ID (usually in signs array)
            signs = entry.get("signs", [])
            if not signs:
                continue

            # Process first sign's videos
            sign_videos = signs[0].get("videos", [])
            for video_id in sign_videos:
                # Find video file
                video_path = self.find_video_file(video_id)
                if not video_path:
                    continue

                # Copy to medical term folder
                medical_folder = self.output_path / medical_term
                medical_folder.mkdir(parents=True, exist_ok=True)

                # Generate output filename
                output_name = f"{medical_term}_wlasl_{video_id}.mp4"
                output_path = medical_folder / output_name

                try:
                    if not output_path.exists():
                        shutil.copy2(video_path, output_path)
                        self.stats[medical_term]["added"] += 1
                        medical_matches[medical_term].append(sign_text)
                        logger.info(
                            f"✓ {medical_term:15} ← {sign_text:30} ({video_id})"
                        )
                    else:
                        self.stats[medical_term]["skipped"] += 1
                except Exception as e:
                    logger.warning(f"Failed to copy {video_id}: {e}")
                    self.stats[medical_term]["skipped"] += 1

                processed += 1

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("WLASL INTEGRATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"\nProcessed {processed} WLASL videos\n")

        print(f"{'Medical Term':<20} {'Added':<10} {'Skipped':<10}")
        print("-" * 40)

        total_added = 0
        for term in sorted(MEDICAL_TERM_MAPPING.keys()):
            added = self.stats[term]["added"]
            skipped = self.stats[term]["skipped"]
            total_added += added

            status = "✓" if added > 0 else "○"
            print(f"{term:<20} {added:<10} {skipped:<10} {status}")

        print("-" * 40)
        print(f"{'TOTAL':<20} {total_added:<10}")

        logger.info(f"\n✅ Total videos imported: {total_added}")
        logger.info(f"📁 Output directory: {self.output_path}")

        # Save integration report
        report = {
            "total_processed": processed,
            "total_added": total_added,
            "by_term": {term: data for term, data in self.stats.items()},
            "wlasl_source": str(metadata_path),
            "output_path": str(self.output_path),
            "timestamp": str(Path.cwd()),
        }

        report_path = Path("wlasl_integration_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Report saved to: {report_path}")

        return True

    def display_next_steps(self):
        """Show next steps for using integrated data"""
        logger.info("\n" + "=" * 70)
        logger.info("NEXT STEPS")
        logger.info("=" * 70)
        logger.info(
            """
To use the integrated WLASL data with your MediSign system:

1. Preprocess videos (extract frames):
   python scripts/2_preprocess_videos.py

2. Extract features (MobileNetV2 encoding):
   python scripts/3_extract_features.py

3. Train model with WLASL + YouTube data:
   python scripts/4_train_medical.py

4. Verify pipeline:
   python scripts/5_verify_pipeline.py

5. Deploy:
   python app_medical.py

Your model will benefit from WLASL's larger, diverse dataset!
        """
        )


def main():
    parser = argparse.ArgumentParser(
        description="Organize and integrate WLASL dataset with MediSign"
    )
    parser.add_argument(
        "--wlasl-path", required=True, help="Path to WLASL dataset directory"
    )
    parser.add_argument(
        "--output",
        default="dataset/raw_videos",
        help="Output directory for organized medical videos",
    )

    args = parser.parse_args()

    # Validate WLASL path
    wlasl_path = Path(args.wlasl_path)
    if not wlasl_path.exists():
        logger.error(f"❌ WLASL path not found: {wlasl_path}")
        return False

    logger.info(f"📁 WLASL path: {wlasl_path}")

    # Organize WLASL data
    organizer = WLASLOrganizer(wlasl_path, args.output)
    success = organizer.organize_wlasl()

    if success:
        organizer.display_next_steps()
        return True
    else:
        logger.error("❌ Failed to process WLASL dataset")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
