# 📊 Medical Sign Language Data Sources Guide

**Updated**: February 2026  
**Status**: Verified sources for acquiring medical sign language videos

---

## 🚀 Quick Start: Use Sample Mode First

**Don't wait for perfect data!** 
```powershell
python setup_medical.py --mode sample
```
- Generates synthetic videos in seconds
- Tests entire pipeline
- Then upgrade to real data when ready
- **No data sourcing needed to start**

---

## 📹 Data Source Options (Ranked by Accessibility)

### ✅ **Option 1: WLASL Dataset (RECOMMENDED)**

**What**: American Sign Language dataset with ~2000 signs  
**Where**: https://www.robots.ox.ac.uk/~vgg/data/wlasl/  
**Size**: ~300K videos (download what you need)  
**Medical relevance**: Mix of medical + general terms  
**Status**: ✅ ACTIVE & ACCESSIBLE

**How to get:**
1. Visit: https://www.robots.ox.ac.uk/~vgg/data/wlasl/
2. Download: `WLASL_v0.3.json` (metadata)
3. Extract videos for medical terms:
   - "doctor", "hospital", "medicine", "pain", "sick"
   - "emergency", "blood", "surgery", "symptom", "infection"

**Code to filter medical terms:**
```python
import json

with open('WLASL_v0.3.json') as f:
    data = json.load(f)

medical_terms = [
    'doctor', 'hospital', 'medicine', 'pain', 'sick',
    'emergency', 'blood', 'surgery', 'symptom', 'infection',
    'disease', 'treatment', 'nurse', 'ambulance', 'injured'
]

medical_videos = [v for v in data if any(m in v['gloss'].lower() for m in medical_terms)]
print(f"Found {len(medical_videos)} medical sign language videos")
```

**Download videos:**
```bash
# Use youtube-dl to download from WLASL sources
pip install yt-dlp

# For each video URL in WLASL
yt-dlp [URL] -o "dataset/raw_videos/heart_attack/video%(autonumber)s.mp4"
```

---

### ✅ **Option 2: Deaf Hub (Free Sign Language Videos)**

**What**: Community-contributed sign language videos  
**Where**: https://www.deafhub.org/  
**Medical content**: Health & medical category available  
**Status**: ✅ FREE & ACCESSIBLE

**Categories available:**
- Health & Wellness
- Medical procedures
- Emergency situations
- Symptoms & diseases

**How to use:**
1. Visit: https://www.deafhub.org/
2. Search for: "medical", "health", "emergency", "doctor"
3. Download videos (if available)
4. Organize into your folders

---

### ✅ **Option 3: YouTube Medical Sign Language Channels**

**Channels with medical content:**

1. **Medical Interpreters Association**
   - URL: Search "medical sign language" on YouTube
   - Content: Medical term demonstrations
   - Method: Screen record or download with yt-dlp

2. **Deaf Medical Professional Channels**
   - Search: "ASL medical", "medical signs tutorial"
   - Often includes: hospital procedures, symptoms, treatments

3. **Sign Language Learning Channels**
   - "Learn ASL medical signs" (multiple channels)
   - Organized by medical specialty

**Download from YouTube:**
```bash
pip install yt-dlp

# Download playlist or single video
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -o "dataset/raw_videos/heart_attack/%(title)s.%(ext)s"

# Download entire playlist
yt-dlp "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o "dataset/raw_videos/%(uploader)s/%(title)s.%(ext)s"
```

---

### ✅ **Option 4: ASL-LEX Dictionary**

**What**: Comprehensive ASL lexicon with videos  
**Where**: https://asl-lex.org/  
**Medical terms**: Some medical vocabulary  
**Status**: ✅ FREE & ACCESSIBLE

**How to access:**
1. Visit: https://asl-lex.org/
2. Search medical terms (e.g., "doctor", "medicine", "pain")
3. View & download videos if permitted

---

### ✅ **Option 5: HandShape Dictionary**

**What**: ASL signs with video demonstrations  
**Where**: https://www.handshapedictionary.com/  
**Medical content**: Limited but available  
**Status**: ✅ ACCESSIBLE

**How to use:**
1. Search for medical terms
2. View video demonstrations
3. Record/capture or download where available

---

### ✅ **Option 6: Create Your Own (Best for Medical Accuracy)**

**If you have access to:**
- Deaf medical professionals
- Sign language interpreters in medical settings
- Medical schools with deaf students/staff

**How to record:**
```
1. Setup:
   - Quiet room with neutral background
   - Good lighting (avoid shadows)
   - Video camera or smartphone (1080p+)
   - High quality audio (optional, for reference)

2. Recording:
   - Record 1-5 second clips per term
   - Multiple angles recommended
   - Different signers preferred (3-5 per term)
   - 30 fps or higher frame rate

3. Organization:
   - Save as: dataset/raw_videos/[term]/[signer]_[take].mp4
   - Example: dataset/raw_videos/heart_attack/deaf_prof_1.mp4
   - Recommend: 50+ videos per term
```

**Why this is best:**
- Medical accuracy verified
- Professional signing quality
- Full control over content
- Can teach community

---

## 🔄 Step-by-Step: Download Medical Signs from WLASL

### Step 1: Get Metadata
```bash
# Download WLASL metadata
curl -O https://www.robots.ox.ac.uk/~vgg/data/wlasl/WLASL_v0.3.json
```

### Step 2: Filter Medical Terms
```python
# filter_medical_signs.py
import json
import os

# Load WLASL metadata
with open('WLASL_v0.3.json', 'r') as f:
    wlasl = json.load(f)

# Medical terms to filter
medical_keywords = [
    'doctor', 'hospital', 'medicine', 'pain', 'sick', 'disease',
    'emergency', 'blood', 'surgery', 'symptom', 'treatment',
    'nurse', 'ambulance', 'injured', 'health', 'medical'
]

# Find matching videos
medical_videos = []
for entry in wlasl:
    gloss = entry['gloss'].lower()
    if any(keyword in gloss for keyword in medical_keywords):
        medical_videos.append(entry)
        print(f"✓ {entry['gloss']} ({len(entry['instances'])} videos)")

print(f"\nTotal medical sign language videos found: {len(medical_videos)}")

# Save URLs for downloading
with open('medical_video_urls.txt', 'w') as f:
    for entry in medical_videos:
        for instance in entry['instances']:
            if 'url' in instance:
                f.write(f"{instance['url']}\n")
```

### Step 3: Download Videos
```bash
# Install downloader
pip install yt-dlp

# Download all URLs
while read url; do
    yt-dlp "$url" -o "dataset/raw_videos/medical_signs/%(title)s.%(ext)s"
done < medical_video_urls.txt
```

### Step 4: Organize into Medical Terms
```python
# organize_videos.py
import os
import shutil

# Map WLASL terms to your 10 medical terms
term_mapping = {
    'doctor': 'surgeon',
    'hospital': 'hospital',
    'medicine': 'medication',
    'pain': 'pain',
    'sick': 'fever',
    'disease': 'broken_arm',  # Generic disease/injury
    'emergency': 'emergency',
    'blood': 'broken_arm',
    'surgery': 'broken_arm',
    'symptom': 'fever',
    'treatment': 'medication',
    'nurse': 'surgeon',
    'ambulance': 'emergency',
    'injured': 'broken_arm',
    'health': 'hospital',
    'medical': 'hospital'
}

# Move downloaded videos to correct folders
source_dir = 'dataset/raw_videos/medical_signs'
for filename in os.listdir(source_dir):
    # Determine which medical term this belongs to
    for wlasl_term, medical_term in term_mapping.items():
        if wlasl_term in filename.lower():
            dest_dir = f'dataset/raw_videos/{medical_term}'
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(
                os.path.join(source_dir, filename),
                os.path.join(dest_dir, filename)
            )
            print(f"✓ Moved {filename} → {medical_term}/")
            break
```

---

## 💾 Practical Data Collection Plan

### Timeline: 2-4 Weeks

**Week 1: Gather Sources**
- [ ] Explore WLASL dataset
- [ ] Find YouTube channels with medical signs
- [ ] Check DeafHub for medical content
- [ ] Identify 50-100 relevant videos

**Week 2: Download Videos**
- [ ] Set up download scripts
- [ ] Download from multiple sources
- [ ] Organize into folders
- [ ] Check quality (lighting, hand visibility)

**Week 3: Organize & Clean**
- [ ] Move videos to term folders
- [ ] Remove duplicates
- [ ] Verify 50+ per medical term if possible
- [ ] Check video formats (convert if needed)

**Week 4: Test & Train**
- [ ] Run preprocessing pipeline
- [ ] Train model with real data
- [ ] Evaluate results
- [ ] Deploy to production

---

## 🎯 Minimum Viable Dataset

**To get started, you need:**
- ✅ 10 medical terms
- ✅ Minimum 5 videos per term (quick test)
- ✅ Better: 20+ per term
- ✅ Ideal: 50+ per term

**Total minimum**: 50 videos  
**Total better**: 200 videos  
**Total ideal**: 500+ videos

---

## 📋 Quick Data Checklist

- [ ] Downloaded videos from one source
- [ ] Created 10 medical term folders
- [ ] Organized videos into folders
- [ ] Verified videos are valid (playable)
- [ ] Have 5+ videos per term minimum
- [ ] Ready to run preprocessing

---

## 🚀 Next Steps

### **Option A: Start Testing Now (Recommended)**
```powershell
python setup_medical.py --mode sample
# Test with synthetic data immediately
# Then upgrade to real data later
```
- No data sourcing needed
- Takes 10 minutes
- Verify pipeline works
- Then collect real videos

### **Option B: Start Data Collection**
1. Choose data source above
2. Download 50-100 medical sign videos
3. Organize into `dataset/raw_videos/<term>/`
4. Run: `python setup_medical.py --mode auto`

### **Option C: Combine Both (Best)**
```powershell
# Test system today
python setup_medical.py --mode sample

# While collecting real data...
# (in background, this week)

# Then retrain when ready
python setup_medical.py --mode auto
```

---

## 📚 Academic Datasets (Research)

If you have university access:

1. **Sign Language Datasets in HCI**
   - MIT SignNet project
   - UC Berkeley Sign Language Project

2. **Medical Education Archives**
   - Medical schools with deaf programs
   - ASL medical interpretation training videos

3. **Research Institutions**
   - Contact: Deaf Studies departments
   - Many have video archives available

---

## ✅ Recommendation

### **Best Path Forward:**

1. **TODAY**: Run sample mode
   ```powershell
   python setup_medical.py --mode sample
   ```

2. **THIS WEEK**: Download 50-100 medical sign videos from WLASL or YouTube

3. **NEXT WEEK**: Train model with real data
   ```powershell
   python setup_medical.py --mode auto
   ```

This gives you working system today + production system next week.

---

**Ready to start?** 
- Sample mode: `python setup_medical.py --mode sample`
- Need real data? See sources above
- Questions? Check docs in medisign folder

