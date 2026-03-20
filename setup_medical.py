#!/usr/bin/env python
"""
MediSign 2.0 - Automated Setup Script
Complete medical sign language integration in one command
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time


class MediSignSetup:
    """Automated setup for MediSign with real medical data"""

    def __init__(self, use_sample=False):
        self.use_sample = use_sample
        self.start_time = time.time()

    def run_command(self, cmd, description):
        """Run a shell command with error handling"""
        print(f"\n{'='*70}")
        print(f"{description}")
        print(f"{'='*70}")
        print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, check=True)
            else:
                result = subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Command failed with exit code {e.returncode}")
            return False

    def setup_complete(self):
        """Run complete setup"""
        steps = [
            (
                "Creating folder structure",
                ["python", "scripts/1_download_dataset.py", "--mode", "create_folders"],
            ),
            (
                (
                    "Preparing data (sample)"
                    if self.use_sample
                    else "Preparing data (manual required)"
                ),
                ["python", "scripts/1_download_dataset.py", "--mode", "sample"],
            ),
            (
                "Preprocessing videos",
                [
                    "python",
                    "scripts/2_preprocess_videos.py",
                    "--input-dir",
                    "dataset/raw_videos",
                    "--output-dir",
                    "dataset/preprocessed",
                ],
            ),
            (
                "Extracting features",
                [
                    "python",
                    "scripts/3_extract_features.py",
                    "--input-dir",
                    "dataset/preprocessed",
                    "--output-dir",
                    "dataset/features",
                ],
            ),
            (
                "Training model",
                [
                    "python",
                    "scripts/4_train_medical.py",
                    "--features-dir",
                    "dataset/features",
                    "--output-model",
                    "models/sequence_model_medical.keras",
                ],
            ),
            ("Verifying pipeline", ["python", "scripts/5_verify_pipeline.py"]),
        ]

        print("\n" + "█" * 70)
        print("█  MediSign 2.0 - Automated Setup")
        print("█" * 70)

        completed = 0
        for description, cmd in steps:
            if self.run_command(cmd, description):
                completed += 1
            else:
                print(f"\nSetup stopped at step {completed + 1}")
                return False

        elapsed = time.time() - self.start_time
        print(f"\n✓ Setup complete! ({elapsed/60:.1f} minutes)")
        print("Next: python app_medical.py")
        return True

    def setup_interactive(self):
        """Interactive setup wizard"""
        print("\n" + "█" * 70)
        print("█  MediSign 2.0 - Interactive Setup Wizard")
        print("█" * 70)

        print("\nWould you like to:")
        print("1. Use SAMPLE data (fast, ~10 minutes)")
        print("2. Use EXISTING videos (provide folder path)")
        print("3. Download WLASL dataset (requires ~100GB, several hours)")

        choice = input("\nSelect (1-3): ").strip()

        if choice == "1":
            self.use_sample = True
            return self.setup_complete()
        elif choice == "2":
            video_dir = input("Enter path to video directory: ").strip()
            if Path(video_dir).exists():
                # Organize provided videos into the dataset structure
                cmd = [
                    "python",
                    "scripts/1_download_dataset.py",
                    "--mode",
                    "organize",
                    "--input-dir",
                    video_dir,
                ]
                if self.run_command(cmd, f"Organizing videos from: {video_dir}"):
                    print(f"Using videos from: {video_dir}")
                    return self.setup_complete()
                else:
                    print("Video organization failed.")
                    return False
            else:
                print(f"Directory not found: {video_dir}")
                return False
        elif choice == "3":
            print("See MEDICAL_INTEGRATION_GUIDE.md for WLASL setup instructions")
            return False
        else:
            print("Invalid choice")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="MediSign 2.0 - Setup automated medical sign language"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "interactive", "sample"],
        default="interactive",
        help="Setup mode",
    )
    parser.add_argument(
        "--skip-verify", action="store_true", help="Skip pipeline verification"
    )

    args = parser.parse_args()

    setup = MediSignSetup(use_sample=(args.mode == "sample"))

    if args.mode == "interactive":
        success = setup.setup_interactive()
    elif args.mode == "sample":
        success = setup.setup_complete()
    elif args.mode == "auto":
        success = setup.setup_complete()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
