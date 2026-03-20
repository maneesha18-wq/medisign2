"""
Prediction Logger Module — Audit logging for MediSign inference.

Features:
- Log predictions to CSV for auditing and analysis
- Track timestamp, predicted label, confidence, audio file, and video source
- Thread-safe logging with atomic file writes
- Auto-create headers on first write
- Query and analysis utilities
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class PredictionLogger:
    """Thread-safe CSV logger for prediction audit trail."""

    def __init__(
        self,
        log_file: str = "logs/predictions.csv",
        auto_create_dir: bool = True,
    ):
        """Initialize prediction logger.

        Args:
            log_file: Path to CSV log file.
            auto_create_dir: Create directory if it doesn't exist.
        """
        self.log_file = Path(log_file)
        self.lock = threading.Lock()  # Thread-safe logging

        if auto_create_dir:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Define CSV headers
        self.headers = [
            "timestamp",
            "label",
            "confidence",
            "audio_file",
            "video_source",
            "video_path",
            "status",
            "error_message",
        ]

        # Auto-create CSV with headers if it doesn't exist
        self._ensure_csv_exists()
        print(f"[OK] PredictionLogger initialized: {self.log_file}")

    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist."""
        if not self.log_file.exists():
            try:
                with open(self.log_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.headers)
                    writer.writeheader()
                print(f"[OK] Created predictions CSV: {self.log_file}")
            except Exception as e:
                print(f"[ERR] Failed to create CSV: {e}")

    def log_prediction(
        self,
        label: str,
        confidence: float,
        audio_file: Optional[str] = None,
        video_source: str = "unknown",
        video_path: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> bool:
        """Log a single prediction to CSV.

        Args:
            label: Predicted label/class.
            confidence: Prediction confidence [0, 1].
            audio_file: Path to generated audio file (if TTS enabled).
            video_source: Source of video ('upload', 'webcam', 'unknown').
            video_path: Path to input video file.
            status: Status ('success', 'error', 'warning').
            error_message: Error message if status is 'error'.

        Returns:
            True if logging succeeded, False otherwise.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        row = {
            "timestamp": timestamp,
            "label": label,
            "confidence": f"{confidence:.4f}",
            "audio_file": audio_file or "",
            "video_source": video_source,
            "video_path": video_path or "",
            "status": status,
            "error_message": error_message or "",
        }

        try:
            with self.lock:
                with open(self.log_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.headers)
                    writer.writerow(row)
            print(f"[OK] Logged: {label} ({confidence:.4f}) -> {audio_file}")
            return True
        except Exception as e:
            print(f"[ERR] Logging failed: {e}")
            return False

    def log_error(
        self,
        label: str = "unknown",
        video_source: str = "unknown",
        video_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Log an inference error.

        Args:
            label: Attempted label (if known).
            video_source: Source of video.
            video_path: Path to input video.
            error_message: Error description.

        Returns:
            True if logging succeeded, False otherwise.
        """
        return self.log_prediction(
            label=label,
            confidence=0.0,
            status="error",
            video_source=video_source,
            video_path=video_path,
            error_message=error_message,
        )

    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary statistics from log file.

        Returns:
            Dictionary with summary stats.
        """
        if not self.log_file.exists():
            return {"total_predictions": 0, "success_count": 0, "error_count": 0}

        try:
            total_predictions = 0
            success_count = 0
            error_count = 0
            avg_confidence = 0.0
            label_counts = {}

            with open(self.log_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                confidences = []

                for row in reader:
                    total_predictions += 1

                    status = row.get("status", "unknown")
                    if status == "success":
                        success_count += 1
                    elif status == "error":
                        error_count += 1

                    try:
                        conf = float(row.get("confidence", 0))
                        confidences.append(conf)
                    except ValueError:
                        pass

                    label = row.get("label", "unknown")
                    label_counts[label] = label_counts.get(label, 0) + 1

            if confidences:
                avg_confidence = sum(confidences) / len(confidences)

            return {
                "total_predictions": total_predictions,
                "success_count": success_count,
                "error_count": error_count,
                "average_confidence": avg_confidence,
                "label_distribution": label_counts,
                "log_file": str(self.log_file),
            }

        except Exception as e:
            print(f"[ERR] Failed to generate summary: {e}")
            return {"error": str(e)}

    def print_summary(self):
        """Print log summary to console."""
        summary = self.get_log_summary()

        print(f"\n{'=' * 80}")
        print("Prediction Log Summary")
        print(f"{'=' * 80}")

        if "error" in summary:
            print(f"[ERR] Error: {summary['error']}")
            return

        print(f"Total Predictions: {summary['total_predictions']}")
        print(f"  [OK] Successful: {summary['success_count']}")
        print(f"  [ERR] Errors: {summary['error_count']}")
        print(f"Average Confidence: {summary['average_confidence']:.4f}")

        if summary["label_distribution"]:
            print(f"\nLabel Distribution:")
            for label, count in sorted(
                summary["label_distribution"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                print(f"  - {label}: {count}")

        print(f"Log File: {summary['log_file']}")
        print(f"{'=' * 80}\n")

    def export_to_dict_list(self) -> list[Dict[str, Any]]:
        """Export all logs as list of dictionaries.

        Returns:
            List of log entries as dictionaries.
        """
        if not self.log_file.exists():
            return []

        try:
            entries = []
            with open(self.log_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entries.append(dict(row))
            return entries
        except Exception as e:
            print(f"[ERR] Failed to export logs: {e}")
            return []

    def get_recent_predictions(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get the most recent predictions.

        Args:
            limit: Number of recent predictions to return.

        Returns:
            List of recent prediction entries.
        """
        entries = self.export_to_dict_list()
        return entries[-limit:] if entries else []


def main():
    """Demo of prediction logger."""
    print("\n" + "=" * 80)
    print("MediSign Prediction Logger Demo")
    print("=" * 80)

    logger = PredictionLogger()

    # Log some sample predictions
    print("\nLogging sample predictions...")
    logger.log_prediction(
        label="medical_sign_1",
        confidence=0.92,
        audio_file="logs/audio/medical_sign_1_20260215_140000_001.mp3",
        video_source="upload",
        video_path="sample_video_1.mp4",
    )

    logger.log_prediction(
        label="medical_sign_2",
        confidence=0.85,
        audio_file="logs/audio/medical_sign_2_20260215_140001_002.mp3",
        video_source="webcam",
        video_path=None,
    )

    logger.log_prediction(
        label="medical_sign_3",
        confidence=0.78,
        audio_file="logs/audio/medical_sign_3_20260215_140002_003.mp3",
        video_source="upload",
        video_path="sample_video_2.mp4",
    )

    logger.log_error(
        label="unknown",
        video_source="webcam",
        error_message="Preprocessing failed: invalid frame size",
    )

    # Print summary
    print("\nGenerating summary...")
    logger.print_summary()

    # Get recent predictions
    print("\nRecent predictions (last 3):")
    recent = logger.get_recent_predictions(3)
    for entry in recent:
        print(f"  - {entry['timestamp']}: {entry['label']} ({entry['confidence']})")

    print(f"\n[OK] Logger demo complete. Check {logger.log_file} for details.\n")


if __name__ == "__main__":
    main()
