"""
Step 2: Preprocess Videos - Extract Frames

Converts raw medical sign language videos into (60, 224, 224, 3) arrays
ready for feature extraction.
"""

import os
import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional
import argparse
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VideoPreprocessor:
    """Preprocess medical sign language videos"""

    def __init__(self, num_frames: int = 60, target_size: Tuple = (224, 224)):
        """
        Initialize preprocessor

        Args:
            num_frames: Extract this many frames per video
            target_size: Resize each frame to this size
        """
        self.num_frames = num_frames
        self.target_size = target_size

    def extract_frames(self, video_path: str) -> Optional[np.ndarray]:
        """
        Extract fixed number of frames from video, respecting frame_start/end in filename
        Filename format: term_id_start_end.mp4
        Returns: Array of shape (num_frames, 224, 224, 3)
        """
        try:
            # Parse filename for framing info
            filename = Path(video_path).stem
            parts = filename.split('_')
            
            frame_start = 0
            frame_end = -1
            
            # Check if filename has framing info: term_id_start_end
            if len(parts) >= 4:
                try:
                    frame_start = int(parts[-2])
                    frame_end = int(parts[-1])
                except ValueError:
                    pass

            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                logger.error(f"Cannot open video: {video_path}")
                return None

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames == 0:
                logger.error(f"Video has 0 frames: {video_path}")
                return None
                
            # Apply framing relative to total frames
            actual_start = max(0, frame_start - 1) if frame_start > 0 else 0
            actual_end = frame_end if (frame_end > 0 and frame_end <= total_frames) else total_frames
            
            if actual_end <= actual_start:
                actual_end = total_frames
                
            available_frames = actual_end - actual_start

            # Calculate frame indices to extract
            if available_frames >= self.num_frames:
                frame_indices = np.linspace(
                    actual_start, actual_end - 1, self.num_frames, dtype=int
                )
            else:
                # If video has fewer frames, repeat some
                frame_indices = np.linspace(
                    actual_start, actual_end - 1, self.num_frames, dtype=int
                )

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()

                if ret:
                    # Resize to target size
                    frame = cv2.resize(frame, self.target_size)
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame)
                else:
                    logger.warning(f"Failed to read frame {idx} from {video_path}")
                    # Use previous frame or black frame
                    if frames:
                        frames.append(frames[-1])
                    else:
                        frames.append(np.zeros((*self.target_size, 3), dtype=np.uint8))

            cap.release()

            # Stack into array
            if len(frames) == self.num_frames:
                array = np.stack(frames, axis=0).astype(np.float32)
                # Normalize to [0, 1]
                array = array / 255.0
                return array
            else:
                logger.error(
                    f"Could not extract {self.num_frames} frames from {video_path}"
                )
                return None

        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            return None

    def preprocess_dataset(
        self, input_dir: str, output_dir: str, skip_existing: bool = True
    ):
        """
        Preprocess all videos in dataset

        Args:
            input_dir: Directory containing video subdirectories (one per medical term)
            output_dir: Where to save preprocessed arrays
            skip_existing: Skip files that already exist
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return

        stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # Process each medical term folder
        for term_dir in sorted(input_path.iterdir()):
            if not term_dir.is_dir():
                continue

            term = term_dir.name
            output_term_dir = output_path / term
            output_term_dir.mkdir(exist_ok=True)

            logger.info(f"\nProcessing term: {term}")

            # Process each video in term folder
            video_files = (
                sorted(term_dir.glob("*.mp4"))
                + sorted(term_dir.glob("*.avi"))
                + sorted(term_dir.glob("*.mov"))
            )

            for video_file in tqdm(video_files, desc=f"  {term}"):
                output_file = output_term_dir / f"{video_file.stem}.npy"

                stats["total"] += 1

                # Skip if exists
                if output_file.exists() and skip_existing:
                    stats["skipped"] += 1
                    continue

                # Extract and save
                frames = self.extract_frames(str(video_file))

                if frames is not None:
                    np.save(output_file, frames)
                    stats["success"] += 1
                else:
                    stats["failed"] += 1

        # Print summary
        self._print_summary(stats, output_path)

    def _print_summary(self, stats, output_dir):
        """Print preprocessing summary"""
        print("\n" + "=" * 70)
        print("PREPROCESSING SUMMARY")
        print("=" * 70)
        print(f"Total videos: {stats['total']}")
        print(f"Successfully processed: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"\nOutput directory: {output_dir}")
        print(f"Output format: (60, 224, 224, 3) float32 arrays [0-1]")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess medical sign language videos"
    )
    parser.add_argument(
        "--input-dir",
        default="dataset/raw_videos",
        help="Directory containing videos organized by medical term",
    )
    parser.add_argument(
        "--output-dir",
        default="dataset/preprocessed",
        help="Output directory for preprocessed arrays",
    )
    parser.add_argument(
        "--num-frames",
        type=int,
        default=60,
        help="Number of frames to extract per video",
    )
    parser.add_argument(
        "--frame-size",
        type=int,
        nargs=2,
        default=[224, 224],
        help="Target frame size (width height)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip videos that already exist",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("STEP 2: VIDEO PREPROCESSING")
    print("=" * 70)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Frames per video: {args.num_frames}")
    print(f"Frame size: {args.frame_size}")
    print("=" * 70 + "\n")

    preprocessor = VideoPreprocessor(
        num_frames=args.num_frames, target_size=tuple(args.frame_size)
    )

    preprocessor.preprocess_dataset(
        args.input_dir, args.output_dir, skip_existing=args.skip_existing
    )


if __name__ == "__main__":
    main()
