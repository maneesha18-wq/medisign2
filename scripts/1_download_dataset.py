"""
Step 1: Download and Prepare Medical Sign Language Dataset

This script helps you obtain real medical sign language data from multiple sources.
Supports: WLASL, custom videos, or existing video files.
"""

import os
import json
import csv
import shutil
from pathlib import Path
import urllib.request
import zipfile
import argparse
from typing import List, Dict


class MedicalSignDatasetPrep:
    """Prepare medical sign language dataset"""

    def __init__(self, output_dir: str = "dataset/raw_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []

    def create_folder_structure(self, medical_terms: List[str]):
        """Create folder structure for medical terms"""
        print("\n" + "=" * 70)
        print("Creating folder structure for medical terms")
        print("=" * 70)

        for term in medical_terms:
            term_dir = self.output_dir / term
            term_dir.mkdir(exist_ok=True)
            print(f"✓ Created: {term_dir}")

        print(f"\nAll medical term folders created in {self.output_dir}/")

    def organize_videos_by_term(self, videos_dir: str, term_mapping: Dict):
        """
        Organize existing videos into medical term folders

        Expected input format:
        videos_dir/
        ├── video1.mp4 (metadata in CSV or filename)
        ├── video2.mp4
        └── ...

        term_mapping: {"video1": "heart_attack", "video2": "diabetes", ...}
        """
        print("\n" + "=" * 70)
        print("Organizing videos by medical term")
        print("=" * 70)

        videos_path = Path(videos_dir)
        if not videos_path.exists():
            print(f"Input directory not found: {videos_dir}")
            return False

        moved_count = 0
        for video_file in videos_path.glob("*.mp4"):
            video_name = video_file.stem

            if video_name in term_mapping:
                term = term_mapping[video_name]
                dest_dir = self.output_dir / term
                dest_path = dest_dir / video_file.name

                if not dest_dir.exists():
                    dest_dir.mkdir(parents=True, exist_ok=True)

                shutil.copy2(video_file, dest_path)
                self.metadata.append(
                    {
                        "filename": video_file.name,
                        "term": term,
                        "path": str(dest_path),
                        "source": "local",
                    }
                )
                print(f"  {video_file.name} → {term}/")
                moved_count += 1

        print(f"\nMoved {moved_count} videos.")
        return True

    def create_sample_dataset(self):
        """
        Create sample medical sign language dataset
        (For testing - uses synthetic/placeholder data)
        """
        print("\n" + "=" * 70)
        print("Creating sample medical sign language dataset")
        print("=" * 70)

        import cv2
        import numpy as np

        medical_terms = [
            "heart_attack",
            "diabetes",
            "broken_arm",
            "fever",
            "medication",
            "headache",
        ]

        for term in medical_terms[:3]:  # Start with 3 terms
            term_dir = self.output_dir / term
            term_dir.mkdir(parents=True, exist_ok=True)

            # Create 5 sample videos per term
            for i in range(5):
                video_path = term_dir / f"{term}_{i:02d}.mp4"

                # Create synthetic video (placeholder)
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))

                for frame_idx in range(60):  # 60 frames = 2 seconds
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    # Create placeholder visual
                    cv2.putText(
                        frame,
                        f"{term.upper()}",
                        (150, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (0, 255, 0),
                        3,
                    )
                    cv2.putText(
                        frame,
                        f"Frame {frame_idx+1}/60",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (200, 200, 200),
                        2,
                    )
                    out.write(frame)

                out.release()
                print(f"  Created: {video_path.name}")
                self.metadata.append(
                    {
                        "filename": video_path.name,
                        "term": term,
                        "path": str(video_path),
                        "source": "synthetic",
                    }
                )

        print(f"\nCreated sample dataset with {len(self.metadata)} videos.")

    def download_wlasl_subset(self, medical_terms: List[str]):
        """
        Download medical sign language subset from WLASL
        (Requires WLASL dataset to be available)

        To use:
        1. Clone WLASL repo: git clone https://github.com/dxli94/WLASL
        2. Follow their setup instructions
        3. Extract relevant medical terms
        """
        print("\n" + "=" * 70)
        print("WLASL Dataset Integration")
        print("=" * 70)
        print(
            """
To use WLASL dataset with MediSign:

1. Clone WLASL repository:
   $ git clone https://github.com/dxli94/WLASL
   $ cd WLASL

2. Download videos (requires ~100GB space):
   $ python download_videos.py

3. Extract medical terms to MediSign:
   $ python scripts/extract_medical_subset.py --wlasl-dir ./WLASL --output ./dataset/raw_videos

4. Or organize manually:
   - Move WLASL videos to dataset/raw_videos/<term>/
   - Update metadata.csv with video information
"""
        )

    def save_metadata(self):
        """Save metadata about collected videos"""
        metadata_file = self.output_dir / "metadata.csv"

        if not self.metadata:
            print("No metadata to save.")
            return

        with open(metadata_file, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["filename", "term", "path", "source"]
            )
            writer.writeheader()
            writer.writerows(self.metadata)

        print(f"\n✓ Metadata saved: {metadata_file}")

    def print_summary(self):
        """Print summary of dataset"""
        print("\n" + "=" * 70)
        print("DATASET PREPARATION SUMMARY")
        print("=" * 70)

        # Count videos per term
        terms = {}
        for item in self.metadata:
            term = item["term"]
            terms[term] = terms.get(term, 0) + 1

        print(f"\nTotal videos: {len(self.metadata)}")
        print(f"Medical terms: {len(terms)}")
        print("\nVideos per term:")
        for term in sorted(terms.keys()):
            print(f"  - {term}: {terms[term]} videos")

        print(f"\nOutput directory: {self.output_dir}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare medical sign language dataset"
    )
    parser.add_argument(
        "--mode",
        choices=["create_folders", "organize", "sample", "wlasl"],
        default="create_folders",
        help="Operation mode",
    )
    parser.add_argument(
        "--input-dir", help="Input directory with videos (for organize mode)"
    )
    parser.add_argument(
        "--output-dir", default="dataset/raw_videos", help="Output directory"
    )
    parser.add_argument(
        "--config",
        default="config/medical_terms.json",
        help="Medical terms configuration file",
    )

    args = parser.parse_args()

    # Load medical terms
    with open(args.config, "r") as f:
        config = json.load(f)
        medical_terms = [term["term"] for term in config["medical_terms"]]

    prep = MedicalSignDatasetPrep(output_dir=args.output_dir)

    if args.mode == "create_folders":
        prep.create_folder_structure(medical_terms)

    elif args.mode == "organize":
        if not args.input_dir:
            print("Error: --input-dir required for organize mode")
            return
        input_dir = args.input_dir

        # Try to load explicit metadata mapping first (metadata.csv or metadata.json)
        term_mapping = {}
        meta_csv = Path(input_dir) / "metadata.csv"
        meta_json = Path(input_dir) / "metadata.json"

        if meta_csv.exists():
            with open(meta_csv, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = Path(row.get("filename", "")).stem
                    term = row.get("term") or row.get("label")
                    if fname and term:
                        term_mapping[fname] = term
            print(f"Loaded metadata mapping from {meta_csv}")

        elif meta_json.exists():
            with open(meta_json) as f:
                data = json.load(f)
                for item in data:
                    fname = Path(item.get("filename", "")).stem
                    term = item.get("term") or item.get("label")
                    if fname and term:
                        term_mapping[fname] = term
            print(f"Loaded metadata mapping from {meta_json}")

        else:
            # Auto-map by filename heuristics: look for medical term substrings
            medical_terms_lower = [t.lower() for t in medical_terms]
            for video_file in Path(input_dir).glob("*.mp4"):
                stem = video_file.stem.lower()
                matched = None
                for term in medical_terms:
                    if term.lower() in stem:
                        if matched is None or len(term) > len(matched):
                            matched = term
                if matched:
                    term_mapping[video_file.stem] = matched
                else:
                    term_mapping[video_file.stem] = "unsorted"

            if any(v == "unsorted" for v in term_mapping.values()):
                (Path(args.output_dir) / "unsorted").mkdir(parents=True, exist_ok=True)
            print(
                "Auto-mapped videos by filename; unmatched files moved to 'unsorted'."
            )

        prep.organize_videos_by_term(input_dir, term_mapping)
        prep.save_metadata()

    elif args.mode == "sample":
        prep.create_sample_dataset()
        prep.save_metadata()

    elif args.mode == "wlasl":
        prep.download_wlasl_subset(medical_terms)

    prep.print_summary()


if __name__ == "__main__":
    main()
