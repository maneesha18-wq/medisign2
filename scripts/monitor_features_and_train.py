import time
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("monitor")

def count_files(directory, pattern="*.npy"):
    """Count files matching pattern in directory recursively."""
    return len(list(Path(directory).rglob(pattern)))

def main():
    # Configuration
    PREPROCESSED_DIR = Path("dataset/preprocessed")
    FEATURES_DIR = Path("dataset/features")
    TRAIN_SCRIPT = "scripts/4_train_medical.py"
    POLL_INTERVAL = 10  # Seconds

    print("\n" + "="*60)
    print("MATCHING FEATURE COUNTS & TRAINING MONITOR")
    print("="*60)

    # 1. Determine Target Count
    if not PREPROCESSED_DIR.exists():
        logger.error(f"Preprocessed directory not found: {PREPROCESSED_DIR}")
        logger.info("Cannot determine target count. Exiting.")
        return

    target_count = count_files(PREPROCESSED_DIR, "*.npy")
    logger.info(f"Target count (from {PREPROCESSED_DIR}): {target_count} files")

    if target_count == 0:
        logger.warning("No preprocessed files found! Is the path correct?")
        return

    # 2. Monitor Loop
    logger.info(f"Monitoring {FEATURES_DIR}...")
    
    while True:
        try:
            current_count = count_files(FEATURES_DIR, "*.npy")
            
            # Progress bar visual
            percent = (current_count / target_count) * 100 if target_count > 0 else 0
            bar_length = 20
            filled_length = int(bar_length * current_count // target_count)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            sys.stdout.write(f"\rProgress: [{bar}] {current_count}/{target_count} ({percent:.1f}%)")
            sys.stdout.flush()

            if current_count >= target_count:
                sys.stdout.write("\n")
                logger.info("Feature extraction complete/matched!")
                break
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user.")
            return
        except Exception as e:
            logger.error(f"\nError during monitoring: {e}")
            time.sleep(POLL_INTERVAL)

    # 3. Trigger Training
    logger.info("\n" + "="*60)
    logger.info("STARTING MODEL TRAINING")
    logger.info("="*60)
    
    try:
        # construct command
        cmd = [sys.executable, TRAIN_SCRIPT]
        
        # Run and stream output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        
        if process.returncode == 0:
            logger.info("\n✅ Training finished successfully!")
            
            # Optional: Launch App?
            # User only asked to "retrain models", but prev script deployed.
            # I will leave it at training for now to be safe and modular.
        else:
            logger.error(f"\n❌ Training failed with return code {process.returncode}")
            
    except Exception as e:
        logger.error(f"Failed to run training script: {e}")

if __name__ == "__main__":
    main()
