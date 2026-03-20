
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

class PredictionLogger:
    def __init__(self, log_dir: str = "logs", filename: str = "predictions.csv"):
        """
        Initialize the prediction logger.
        
        Args:
            log_dir: Directory to store log files.
            filename: Name of the CSV file.
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / filename
        
        # Create directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.log_file.exists():
            self._init_csv()

    def _init_csv(self):
        """Create the CSV file with headers."""
        try:
            with open(self.log_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "label", "confidence", "video_source"])
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def log_prediction(self, label: str, confidence: float, video_source: str = "upload"):
        """
        Log a single prediction.
        
        Args:
            label: Predicted class label.
            confidence: Prediction confidence score (0.0 - 1.0).
            video_source: Source of the video ("upload" or "webcam").
        """
        try:
            timestamp = datetime.now().isoformat()
            with open(self.log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, label, f"{confidence:.4f}", video_source])
        except Exception as e:
            print(f"Error logging prediction: {e}")

    def validate_integrity(self) -> bool:
        """Check if the CSV file is valid and readable."""
        if not self.log_file.exists():
            return False
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header != ["timestamp", "label", "confidence", "video_source"]:
                    return False
                # Consume remaining lines to ensure readability
                for _ in reader:
                    pass
            return True
        except Exception:
            return False
