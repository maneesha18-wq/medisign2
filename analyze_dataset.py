"""
Dataset Analysis - Show what data is being used
"""

import numpy as np
from pathlib import Path

print("=" * 70)
print("MEDISIGN DATASET ANALYSIS")
print("=" * 70)

dataset_path = Path("dataset")
print("\nDataset Structure:\n")

for category in ["demo", "demo2", "samples", "scaled"]:
    cat_path = dataset_path / category
    if cat_path.exists():
        npy_files = list(cat_path.glob("*.npy"))
        print(f"{category}/:")
        print(f"  - Total files: {len(npy_files)}")

        if npy_files:
            sample = np.load(npy_files[0])
            print(f"  - Sample shape: {sample.shape}")
            print(f"  - Data type: {sample.dtype}")
            print(f"  - Value range: [{sample.min():.4f}, {sample.max():.4f}]")
            print(f"  - First few files:")
            for f in sorted(npy_files)[:3]:
                print(f"      • {f.name}")
        print()

print("=" * 70)
print("WHAT IS THIS DATA?")
print("=" * 70)
print(
    """
DATA SOURCE:
  - NOT real medical sign language videos
  - SYNTHETIC/EXTRACTED features from videos
  - Format: Pre-computed deep learning embeddings
  
DATA CHARACTERISTICS:
  - Shape: 60 frames × 1280 features per sample
  - Features: MobileNetV2 CNN visual embeddings
  - Classes: 2 categories (demo, demo2)
  
WHAT WE HAVE:
  The model works with EXTRACTED FEATURES, not raw videos.
  This is like having the "visual understanding" already computed.
  
HOW IT WORKS:
  1. Raw video → Extract 60 frames
  2. MobileNetV2 processes each frame → 1280-dim feature vector
  3. BiLSTM processes 60 frame features → Prediction
  
DATA STATISTICS:
"""
)

total_samples = 0
for category in ["demo", "demo2", "samples", "scaled"]:
    cat_path = dataset_path / category
    if cat_path.exists():
        npy_files = list(cat_path.glob("*.npy"))
        total_samples += len(npy_files)
        print(f"  - {category}: {len(npy_files)} samples")

print(f"\n  Total: {total_samples} samples")

print("\n" + "=" * 70)
print("USING REAL SIGN LANGUAGE DATA?")
print("=" * 70)
print(
    """
CURRENT STATUS: Synthetic/Demo Data
  - Created synthetic test videos for demonstration
  - Uses placeholder medical sign patterns
  - Good for TESTING the pipeline
  
TO USE REAL DATA: You would need to:
  1. Obtain medical sign language dataset:
     • ASL (American Sign Language)
     • LSF (Langue des Signes Française)
     • Other signed languages
  
  2. Source options:
     ✓ Public datasets (limited):
       - DERF-20 (20 signs)
       - RWTH-BOSTON-50 (50 signs)
       - WLASL (10,000 ASL signs)
     
     ✓ Create custom dataset:
       - Record sign language videos
       - Label with medical terms
       - Extract features with preprocessing
     
  3. Extract features from new videos:
     - Process through MobileNetV2
     - Create (60, 1280) arrays
     - Organize into dataset/class_name/ folders
  
  4. Retrain model:
     python train_full.py --epochs 50 --batch-size 32
"""
)

print("=" * 70)
