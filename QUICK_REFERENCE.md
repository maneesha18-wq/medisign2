# 🚀 MediSign 2.0 - Quick Reference Card

## ⚡ Ultra Quick Start (Pick One)

### For Testing (10 min)
```powershell
python setup_medical.py --mode sample
# Then visit: http://localhost:7860
```

### For Real Data (2-5 hours)
```powershell
# 1. Place videos in: dataset/raw_videos/[medical_term]/
# 2. Run:
python setup_medical.py --mode auto
# 3. Visit: http://localhost:7860
```

### Manual Control (Varies)
```powershell
python scripts/1_download_dataset.py --mode sample
python scripts/2_preprocess_videos.py
python scripts/3_extract_features.py
python scripts/4_train_medical.py
python scripts/5_verify_pipeline.py
python app_medical.py
```

---

## 📋 Medical Terms (10 Total)
```
0  → heart_attack        (cardiac)
1  → diabetes            (endocrine)
2  → broken_arm          (orthopedic)
3  → fever               (symptoms)
4  → medication          (treatment)
5  → headache            (symptoms)
6  → hospital            (location)
7  → surgeon             (professional)
8  → emergency           (urgency)
9  → pain                (symptoms)
```

---

## 🎯 File Organization

```
Place videos here:
  dataset/raw_videos/heart_attack/*.mp4
  dataset/raw_videos/diabetes/*.mp4
  ... (one folder per term)

Everything else auto-generated:
  dataset/preprocessed/    (step 2)
  dataset/features/        (step 3)
  models/                  (step 4)
  logs/                    (ongoing)
```

---

## 📊 Pipeline at a Glance

```
Script 1: Download → Organize data
Script 2: Preprocess → Extract 60 frames
Script 3: Features → MobileNetV2 embeddings
Script 4: Train → BiLSTM+Attention model
Script 5: Verify → 6-point validation
App: Deploy → Gradio web interface
```

---

## ⚙️ Configuration

### dataset_config.yaml
```yaml
num_frames: 60              # Can change to 30 or 120
frame_size: [224, 224]      # Keep for MobileNetV2
train_split: 0.7            # Train/val/test ratios
```

### training_config.yaml
```yaml
epochs: 100                 # Number of training iterations
batch_size: 16              # Reduce if GPU out of memory
learning_rate: 0.001        # Adjust for convergence speed
```

### medical_terms.json
```json
Add new term:
{
  "id": 10,
  "english": "stroke",
  "category": "neurological"
}
```

---

## 🔍 Check System Status

```powershell
# Verify data organized
Get-ChildItem dataset/raw_videos -Directory

# Check preprocessing
Get-ChildItem dataset/preprocessed -Recurse -Filter *.npy | Measure-Object

# Check features
Get-ChildItem dataset/features -Recurse -Filter *.npy | Measure-Object

# Verify model
Test-Path models/sequence_model_medical.keras
Get-Item models/medical_terms_map.json

# Run full validation
python scripts/5_verify_pipeline.py
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | `pip install tensorflow opencv-python mediapipe gradio gTTS` |
| "CUDA out of memory" | Reduce batch_size in training_config.yaml |
| "No videos found" | Check folder structure in dataset/raw_videos/ |
| "Model crashes" | Run `python scripts/5_verify_pipeline.py` |
| App won't load | Browser to http://localhost:7860 |

---

## 📈 Expected Outputs

| File | Size | Check |
|------|------|-------|
| Preprocessed video | 3.6 MB | `dataset/preprocessed/` |
| Feature file | 307 KB | `dataset/features/` |
| Trained model | 56 MB | `models/sequence_model_medical.keras` |
| Label mapping | <1 KB | `models/medical_terms_map.json` |
| Predictions log | Grows | `logs/predictions_medical.csv` |

---

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] TensorFlow 2.13+ available
- [ ] Run `python setup_medical.py --mode sample` works
- [ ] Web app loads at localhost:7860
- [ ] Can upload video to test
- [ ] Predictions show medical terms (not "demo")
- [ ] `python scripts/5_verify_pipeline.py` shows ✓

---

## 📚 Documentation Map

| Need | File |
|------|------|
| First time? | DOCUMENTATION_INDEX.md |
| Overview? | SYSTEM_DELIVERY_SUMMARY.md |
| How to run? | README_MEDICAL_INTEGRATION.md |
| Step-by-step? | IMPLEMENTATION_CHECKLIST.md |
| Deep dive? | MEDICAL_INTEGRATION_GUIDE.md |
| Architecture? | ARCHITECTURE_REFERENCE.md |

---

## 🎬 Data Organization Example

```
Raw videos structure:
dataset/raw_videos/
├── heart_attack/
│   ├── video1.mp4           (any length)
│   ├── video2.avi
│   └── video3.mov
├── diabetes/
│   ├── patient_demo_1.mp4
│   ├── patient_demo_2.mp4
│   └── ...
└── ... (one folder per medical term)

After preprocessing:
dataset/preprocessed/
├── heart_attack/
│   ├── video1_frames.npy    (60, 224, 224, 3)
│   ├── video2_frames.npy
│   └── video3_frames.npy
├── diabetes/
│   └── ...
```

---

## 💡 Pro Tips

✓ Start with sample mode to verify system works  
✓ Use 50+ videos per medical term for best accuracy  
✓ Video length 1-5 seconds is optimal  
✓ Use `--mode sample` to test without real videos  
✓ Monitor `logs/predictions_medical.csv` for history  
✓ Run verification after each major step  
✓ Save trained model before retraining  
✓ Use TFLite export for mobile deployment  

---

## 🚀 One-Command Deployment

```powershell
# Everything automated with sample data
python setup_medical.py --mode sample

# Then for real data later
python setup_medical.py --mode auto
```

---

## 📞 Quick Answers

**Q: How long to get first working system?**  
A: 20 minutes with sample mode

**Q: How long to production?**  
A: 2-5 hours depending on video count

**Q: Do I need GPU?**  
A: No, CPU works too (just slower)

**Q: Can I add more medical terms?**  
A: Yes, edit medical_terms.json

**Q: Where do I put videos?**  
A: `dataset/raw_videos/[medical_term]/`

**Q: What if I have no videos?**  
A: Use `--mode sample` for testing

**Q: How do I access the app?**  
A: Browser to http://localhost:7860

---

## 🎯 Next 5 Minutes

1. **Read** this card
2. **Run** `python setup_medical.py --mode sample`
3. **Open** http://localhost:7860
4. **Upload** test video
5. **Get** medical term prediction ✅

---

**System Status**: ✅ READY TO DEPLOY

Print this card | Bookmark reference | Share with team

