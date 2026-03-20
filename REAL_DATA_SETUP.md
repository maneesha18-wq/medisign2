"""
MediSign Real Medical Sign Language Integration
================================================

This guide provides complete instructions for upgrading MediSign
to work with real medical sign language videos.

VERSION: 2.0 (Real Data Edition)
DATE: 2026-02-15
"""

# ============================================================================
# PART 1: PROJECT STRUCTURE FOR REAL MEDICAL SIGN DATA
# ============================================================================

FOLDER_STRUCTURE = """
medisign/
├── dataset/
│   ├── raw_videos/                    # Original video files
│   │   ├── medical_terms/
│   │   │   ├── heart_attack/
│   │   │   │   ├── heart_attack_01.mp4
│   │   │   │   ├── heart_attack_02.mp4
│   │   │   │   └── ...
│   │   │   ├── diabetes/
│   │   │   ├── broken_arm/
│   │   │   ├── fever/
│   │   │   ├── medication/
│   │   │   └── ... (more medical terms)
│   │   └── metadata.csv              # Video labels and info
│   │
│   ├── preprocessed/                 # Extracted frames (60, 224, 224, 3)
│   │   ├── heart_attack/
│   │   │   ├── heart_attack_01.npy
│   │   │   ├── heart_attack_02.npy
│   │   │   └── ...
│   │   ├── diabetes/
│   │   └── ... (one dir per medical term)
│   │
│   ├── features/                     # Extracted features (60, 1280)
│   │   ├── heart_attack/
│   │   │   ├── heart_attack_01.npy
│   │   │   ├── heart_attack_02.npy
│   │   │   └── ...
│   │   ├── diabetes/
│   │   └── ... (organized by medical term)
│   │
│   └── splits/                       # Train/Val/Test splits
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
│
├── models/
│   ├── sequence_model_medical.keras   # Retrained model (NEW)
│   ├── medical_terms_map.json         # Label mapping (NEW)
│   └── tflite/
│       ├── medical_model_fp16.tflite
│       └── medical_model_int8.tflite
│
├── scripts/
│   ├── 1_download_dataset.py         # NEW: Download/prepare dataset
│   ├── 2_preprocess_videos.py        # NEW: Extract frames
│   ├── 3_extract_features.py         # NEW: Extract with MobileNetV2
│   ├── 4_train_medical.py            # NEW: Retrain on medical data
│   └── 5_verify_pipeline.py          # NEW: Verify everything works
│
├── config/
│   ├── medical_terms.json            # NEW: Define medical vocabulary
│   ├── dataset_config.yaml           # NEW: Dataset paths and settings
│   └── training_config.yaml          # NEW: Training hyperparameters
│
├── app_medical.py                    # NEW: Updated Gradio app
└── logs/
    ├── feature_extraction.log
    ├── training_medical.log
    └── predictions.csv
"""

print(__doc__)
print(FOLDER_STRUCTURE)
