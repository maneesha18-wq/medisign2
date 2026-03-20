"""
MediSign 2.0 - COMPLETE SETUP GUIDE
Real Medical Sign Language Recognition
"""

# ============================================================================
# PART 1: QUICK START
# ============================================================================

QUICK_START = """
===========================================================================
MEDISIGN 2.0 - MEDICAL SIGN LANGUAGE INTEGRATION
===========================================================================

OBJECTIVE: Upgrade MediSign from demo data to real medical sign language

TIMELINE: ~2-4 hours for complete setup
REQUIREMENTS:
  - GPU: 8GB+ VRAM (recommended)
  - Storage: 50GB+ for raw videos
  - Internet: For downloading datasets

===========================================================================
STEP-BY-STEP SETUP
===========================================================================

PHASE 1: PREPARE ENVIRONMENT (5 minutes)
-------

1. Create folder structure:
   $ python scripts/1_download_dataset.py --mode create_folders

2. Verify config files exist:
   - config/medical_terms.json
   - config/dataset_config.yaml
   - config/training_config.yaml


PHASE 2: ACQUIRE DATA (15-60 minutes depending on source)
-------

Option A: Use Sample/Demo Data (FAST - 5 min)
   $ python scripts/1_download_dataset.py --mode sample --output-dir dataset/raw_videos

Option B: Download WLASL Dataset (2-3 hours)
   See instructions in scripts/1_download_dataset.py

Option C: Use Your Own Videos (Variable)
   Place videos in dataset/raw_videos/<medical_term>/ folders
   
   Example structure:
   dataset/raw_videos/
   ├── heart_attack/
   │   ├── video1.mp4
   │   ├── video2.mp4
   │   └── ...
   ├── diabetes/
   │   ├── video1.mp4
   │   └── ...
   └── ...


PHASE 3: PREPROCESS VIDEOS (10-30 minutes)
-------

Extract frames to (60, 224, 224, 3) arrays:

   $ python scripts/2_preprocess_videos.py \\
       --input-dir dataset/raw_videos \\
       --output-dir dataset/preprocessed \\
       --num-frames 60 \\
       --frame-size 224 224

Output: dataset/preprocessed/<medical_term>/*.npy


PHASE 4: EXTRACT FEATURES (15-45 minutes)
-------

Convert frames to MobileNetV2 embeddings (60, 1280):

   $ python scripts/3_extract_features.py \\
       --input-dir dataset/preprocessed \\
       --output-dir dataset/features \\
       --backbone mobilenetv2 \\
       --device gpu

Output: dataset/features/<medical_term>/*.npy


PHASE 5: TRAIN MODEL (30-120 minutes)
-------

Retrain BiLSTM+Attention on medical data:

   $ python scripts/4_train_medical.py \\
       --features-dir dataset/features \\
       --output-model models/sequence_model_medical.keras \\
       --config config/training_config.yaml

Output:
   - models/sequence_model_medical.keras
   - models/medical_terms_map.json


PHASE 6: VERIFY PIPELINE (5 minutes)
-------

Check all components work:

   $ python scripts/5_verify_pipeline.py \\
       --model models/sequence_model_medical.keras \\
       --label-map models/medical_terms_map.json \\
       --features-dir dataset/features

Expected output: ALL CHECKS PASSED


PHASE 7: DEPLOY (2 minutes)
-------

Run updated Gradio app:

   $ python app_medical.py

Open browser: http://localhost:7860


===========================================================================
COMPLETE COMMAND SEQUENCE
===========================================================================

All steps in one bash script:

```bash
#!/bin/bash
set -e

echo "=== MEDISIGN 2.0 SETUP ==="

# Step 1: Create structure
echo "Step 1: Creating folder structure..."
python scripts/1_download_dataset.py --mode create_folders

# Step 2: Prepare data (sample)
echo "Step 2: Preparing sample data..."
python scripts/1_download_dataset.py --mode sample

# Step 3: Preprocess
echo "Step 3: Preprocessing videos..."
python scripts/2_preprocess_videos.py \\
    --input-dir dataset/raw_videos \\
    --output-dir dataset/preprocessed

# Step 4: Extract features
echo "Step 4: Extracting features..."
python scripts/3_extract_features.py \\
    --input-dir dataset/preprocessed \\
    --output-dir dataset/features

# Step 5: Train model
echo "Step 5: Training model..."
python scripts/4_train_medical.py \\
    --features-dir dataset/features \\
    --output-model models/sequence_model_medical.keras

# Step 6: Verify
echo "Step 6: Verifying pipeline..."
python scripts/5_verify_pipeline.py

# Step 7: Run
echo "Step 7: Launching app..."
python app_medical.py
```


===========================================================================
TROUBLESHOOTING
===========================================================================

ERROR: "No videos found in dataset/raw_videos"
FIX: Run Step 2 with --mode sample or --mode create_folders first

ERROR: "Out of memory during feature extraction"
FIX: Process fewer videos at once or use smaller batch size:
     Reduce --batch-size in config/training_config.yaml

ERROR: "Model not found during inference"
FIX: Ensure models/sequence_model_medical.keras exists
     Check training completed successfully (look for model file)

ERROR: "TF-Lite export failed"
FIX: Model needs to be in Keras format (.keras not .h5)
     Verify trained model is saved with .save() not .save_weights()

ERROR: "Audio not generating"
FIX: Install gTTS: pip install gTTS
     Check logs/audio directory exists
     Verify internet connection for TTS API


===========================================================================
DATA ORGANIZATION REFERENCE
===========================================================================

After complete setup, directory structure:

medisign/
├── dataset/
│   ├── raw_videos/          # Original videos
│   │   ├── heart_attack/     (30+ videos)
│   │   ├── diabetes/         (30+ videos)
│   │   └── ...               (10 different medical terms)
│   │
│   ├── preprocessed/         # Extracted frames (60, 224, 224, 3)
│   │   ├── heart_attack/
│   │   ├── diabetes/
│   │   └── ...
│   │
│   └── features/             # MobileNetV2 features (60, 1280)
│       ├── heart_attack/     (100+ feature files)
│       ├── diabetes/         (100+ feature files)
│       └── ...
│
├── models/
│   ├── sequence_model_medical.keras         # Trained model
│   ├── medical_terms_map.json               # Label mapping
│   └── tflite/
│       ├── medical_model_fp16.tflite        # Mobile version
│       └── medical_model_int8.tflite        # Embedded version
│
├── config/
│   ├── medical_terms.json          # Medical vocabulary
│   ├── dataset_config.yaml         # Dataset settings
│   └── training_config.yaml        # Training params
│
├── scripts/
│   ├── 1_download_dataset.py       # Acquire & organize data
│   ├── 2_preprocess_videos.py      # Extract frames
│   ├── 3_extract_features.py       # Get MobileNetV2 embeddings
│   ├── 4_train_medical.py          # Train model
│   └── 5_verify_pipeline.py        # Test everything
│
├── app_medical.py                  # Updated Gradio app
└── logs/
    ├── audio/                       # Generated TTS audio
    ├── training_medical.log
    └── predictions_medical.csv


===========================================================================
CUSTOMIZATION
===========================================================================

To add more medical terms:

1. Edit config/medical_terms.json:
   Add new entry with:
   - "id": (next available number)
   - "term": "medical_term_name"
   - "english": "Human Readable Name"
   - "category": "category_name"

2. Create video folder:
   $ mkdir dataset/raw_videos/medical_term_name

3. Add videos to that folder

4. Retrain model with new term:
   $ python scripts/4_train_medical.py --features-dir dataset/features


To change training parameters:

Edit config/training_config.yaml:
- epochs: Number of training iterations
- batch_size: Samples per batch (16-32 recommended)
- learning_rate: Model learning speed (0.001 typical)
- early_stopping: patience before stopping
- lstm_units: LSTM hidden size (256 recommended)


===========================================================================
PERFORMANCE EXPECTATIONS
===========================================================================

With 10 medical terms × 50 videos each (500 total):
- Preprocessing: ~20 minutes
- Feature extraction: ~45 minutes
- Training: ~60 minutes
- Total: ~2 hours

Model performance:
- Accuracy: 85-95% (depends on video quality)
- Inference speed: 50-200ms per video
- Model size: 56 MB (float32), 28 MB (fp16), 14 MB (int8)


===========================================================================
PRODUCTION DEPLOYMENT
===========================================================================

1. Export TFLite for mobile:
   $ python -c "
   from modules.tflite_exporter import TFLiteExporter
   exp = TFLiteExporter('models/sequence_model_medical.keras')
   exp.export_all()
   "

2. Deploy on iOS/Android:
   - Follow TFLite_Deployment_Guide.md
   - Use model_fp16.tflite (balanced)

3. Deploy on server:
   - Use app_medical.py
   - Run with: gunicorn -w 4 app_medical:app

4. Monitor predictions:
   - View logs/predictions_medical.csv
   - Check accuracy and error rates
   - Retrain periodically with new data


===========================================================================
END OF SETUP GUIDE
===========================================================================
"""

print(__doc__)
print(QUICK_START)
