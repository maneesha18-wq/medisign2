
from modules.logger import PredictionLogger
import os
import shutil

# Setup
if os.path.exists("logs_test"):
    shutil.rmtree("logs_test")

logger = PredictionLogger(log_dir="logs_test")

# Test 1: Log file creation
if os.path.exists("logs_test/predictions.csv"):
    print("PASS: Log file created")
else:
    print("FAIL: Log file not created")

# Test 2: Log prediction
logger.log_prediction("test_label", 0.95, "upload")

with open("logs_test/predictions.csv", "r") as f:
    lines = f.readlines()
    if len(lines) == 2 and "test_label" in lines[1]:
        print("PASS: Prediction logged correctly")
    else:
        print(f"FAIL: Logging content incorrect. Got {len(lines)} lines.")

# Test 3: Integrity check
if logger.validate_integrity():
    print("PASS: Integrity check passed")
else:
    print("FAIL: Integrity check failed")

# Cleanup
# shutil.rmtree("logs_test") 
