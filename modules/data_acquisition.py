
import cv2
import os
import time
import uuid
from pathlib import Path

class DataAcquisition:
    def __init__(self, dataset_dir="dataset", width=640, height=480, fps=30):
        self.dataset_dir = Path(dataset_dir)
        self.width = width
        self.height = height
        self.fps = fps
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

    def record_sample(self, label, duration=2.0):
        """
        Record a video sample for a specific label.
        
        Args:
            label: Class label for the video.
            duration: Duration of recording in seconds.
            
        Returns:
            Path to the saved video file.
        """
        label_dir = self.dataset_dir / label
        label_dir.mkdir(exist_ok=True)
        
        # Unique filename
        filename = f"{label}_{uuid.uuid4().hex[:8]}.mp4"
        filepath = label_dir / filename
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return None

        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(filepath), fourcc, self.fps, (self.width, self.height))
        
        start_time = time.time()
        frame_count = 0
        expected_frames = int(duration * self.fps)
        
        print(f"Recording {duration}s for '{label}'...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Overlay status
            elapsed = time.time() - start_time
            if elapsed < duration:
                cv2.putText(frame, "RECORDING", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                out.write(frame)
                frame_count += 1
            else:
                break
                
            cv2.imshow('Recording', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        print(f"Saved {filepath} ({frame_count} frames)")
        return str(filepath)

    def interactive_session(self, labels, samples_per_label=8):
        """
        Run an interactive session to collect data for a list of labels.
        """
        for label in labels:
            print(f"\n--- Collecting data for: {label} ---")
            count = 0
            label_dir = self.dataset_dir / label
            if label_dir.exists():
                count = len(list(label_dir.glob("*.mp4")))
            
            print(f"Current samples: {count}")
            while count < samples_per_label:
                print(f"Ready to record sample {count+1}/{samples_per_label}. Press SPACE to start, 's' to skip label, 'q' to quit.")
                
                # Wait for user trigger
                key = self._wait_for_key()
                if key == 's':
                    break
                if key == 'q':
                    return
                if key == 'space':
                    self.record_sample(label)
                    count += 1
                    time.sleep(0.5) 

    def _wait_for_key(self):
        """
        Wait for a key press using OpenCV window.
        """
        cap = cv2.VideoCapture(0) 
        # Just to show a preview window while waiting
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.putText(frame, "Press SPACE to record", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Ready', frame)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord(' '):
                cap.release()
                cv2.destroyAllWindows()
                return 'space'
            if key == ord('s'):
                cap.release()
                cv2.destroyAllWindows()
                return 's'
            if key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return 'q'
