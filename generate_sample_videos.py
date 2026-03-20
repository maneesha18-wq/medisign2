"""
Generate sample medical sign language videos for testing
Creates synthetic video files with recognizable patterns
"""

import os
import cv2
import numpy as np
from pathlib import Path
import time


def create_sample_video(filename, seed=42, video_type="sign1"):
    """Create a synthetic video file for testing

    Args:
        filename: Output video path
        seed: Random seed for reproducibility
        video_type: Type of pattern (sign1, sign2, etc.)
    """
    np.random.seed(seed)

    # Video parameters
    frame_width = 640
    frame_height = 480
    fps = 30
    duration_sec = 2  # 2 seconds
    num_frames = fps * duration_sec

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    print(f"Creating {video_type}...", end="", flush=True)

    for frame_idx in range(num_frames):
        # Create blank frame
        frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

        # Add gradient background
        for i in range(frame_height):
            frame[i, :] = [20 + i // 3, 30 + i // 3, 40 + i // 3]

        # Add movement pattern based on video type
        center_x = frame_width // 2
        center_y = frame_height // 2

        # Create moving shapes (like hand movements in sign language)
        if video_type == "sign1":
            # Circular motion
            angle = (frame_idx / num_frames) * 2 * np.pi
            x = center_x + int(100 * np.cos(angle))
            y = center_y + int(80 * np.sin(angle))
            color = (0, 200, 255)  # Orange
            cv2.circle(frame, (x, y), 30, color, -1)
            cv2.circle(frame, (x, y), 30, (255, 255, 255), 2)

        elif video_type == "sign2":
            # Horizontal sweep motion
            x = center_x + int(150 * np.sin((frame_idx / num_frames) * np.pi))
            y = center_y
            color = (100, 200, 50)  # Greenish
            cv2.rectangle(frame, (x - 40, y - 40), (x + 40, y + 40), color, -1)
            cv2.rectangle(frame, (x - 40, y - 40), (x + 40, y + 40), (255, 255, 255), 2)

        elif video_type == "sign3":
            # Vertical motion with rotation
            y = center_y - 100 + int(150 * (frame_idx / num_frames))
            x = center_x
            color = (255, 100, 50)  # Blue-ish
            angle = (frame_idx / num_frames) * 360
            pts = np.array(
                [
                    [
                        x + 40 * np.cos(angle * np.pi / 180),
                        y + 40 * np.sin(angle * np.pi / 180),
                    ],
                    [
                        x + 40 * np.cos((angle + 120) * np.pi / 180),
                        y + 40 * np.sin((angle + 120) * np.pi / 180),
                    ],
                    [
                        x + 40 * np.cos((angle + 240) * np.pi / 180),
                        y + 40 * np.sin((angle + 240) * np.pi / 180),
                    ],
                ],
                np.int32,
            )
            cv2.polylines(frame, [pts], True, color, 3)
            cv2.fillPoly(frame, [pts], color)

        else:  # sign4, sign5, etc.
            # Complex motion pattern
            t = frame_idx / num_frames
            x1 = center_x + int(50 * np.sin(t * 4 * np.pi))
            y1 = center_y + int(50 * np.cos(t * 3 * np.pi))
            x2 = center_x + int(80 * np.sin(t * 5 * np.pi))
            y2 = center_y + int(80 * np.cos(t * 4 * np.pi))

            color1 = (50, 200, 200)
            color2 = (200, 50, 150)
            cv2.circle(frame, (x1, y1), 25, color1, -1)
            cv2.circle(frame, (x2, y2), 20, color2, -1)
            cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

        # Add frame counter
        cv2.putText(
            frame,
            f"Frame {frame_idx+1}/{num_frames}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            2,
        )
        cv2.putText(
            frame,
            video_type.upper(),
            (10, frame_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        # Write frame
        out.write(frame)

    out.release()
    print(f" OK ({num_frames} frames)")


def main():
    print("\n" + "=" * 70)
    print("Generating Sample Medical Sign Language Videos")
    print("=" * 70 + "\n")

    # Create dataset directories
    demo_dir = Path("dataset/demo")
    demo2_dir = Path("dataset/demo2")

    demo_dir.mkdir(parents=True, exist_ok=True)
    demo2_dir.mkdir(parents=True, exist_ok=True)

    # Generate demo dataset (15-20 samples of sign1 and sign2)
    print("Creating demo/ dataset:")
    signs = ["sign1", "sign2"]

    for i in range(10):
        sign_type = signs[i % len(signs)]
        video_path = demo_dir / f"sample_{i+1:02d}_{sign_type}.mp4"
        create_sample_video(str(video_path), seed=42 + i, video_type=sign_type)

    print("")

    # Generate demo2 dataset (alternative samples)
    print("Creating demo2/ dataset:")
    signs2 = ["sign1", "sign2", "sign3"]

    for i in range(8):
        sign_type = signs2[i % len(signs2)]
        video_path = demo2_dir / f"sample_{i+1:02d}_{sign_type}.mp4"
        create_sample_video(str(video_path), seed=100 + i, video_type=sign_type)

    print("\n" + "=" * 70)
    print("Sample Video Generation Complete!")
    print("=" * 70)

    # Display statistics
    print("\nGenerated Videos:")
    print(f"  demo/     - {len(list(demo_dir.glob('*.mp4')))} videos")
    print(f"  demo2/    - {len(list(demo2_dir.glob('*.mp4')))} videos")

    print("\nVideo Details:")
    print("  • Resolution: 640 x 480 pixels")
    print("  • Duration: 2 seconds per video")
    print("  • Frame Rate: 30 fps (60 frames)")
    print("  • Format: H.264 MP4")

    print("\nUsage:")
    print("  1. Open http://localhost:7860")
    print("  2. Go to 'Inference' tab")
    print("  3. Upload a video from dataset/demo/ or dataset/demo2/")
    print("  4. Click 'Infer' to test the model")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
