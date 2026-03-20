
import json
import shutil
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
WLASL_VIDEOS = Path(r"C:\Users\vishn\Downloads\archive\videos")
WLASL_JSON = Path(r"C:\Users\vishn\Downloads\archive\WLASL_v0.3.json")
OUTPUT_DIR = Path(r"c:\Users\vishn\OneDrive\Desktop\New folder\medisign\dataset\raw_videos")

# 1. Refined Category Mapping (311 potential videos)
MEDICAL_TERM_MAPPING = {
    "heart_attack": ["heart attack", "heart", "attack", "cardiac"],
    "diabetes": ["diabetes", "sugar", "insulin"],
    "broken_arm": ["broken arm", "arm", "break", "broken", "fracture", "bone", "injury"],
    "fever": ["fever", "temperature", "sick", "illness", "cough", "cold", "flu"],
    "medication": ["medicine", "drug", "pill", "tablet", "medication", "pharmacy", "prescription"],
    "headache": ["headache", "migraine"],
    "hospital": ["hospital", "clinic", "nurse", "patient", "treatment"],
    "surgeon": ["surgeon", "doctor", "physician", "surgery", "operation"],
    "emergency": ["emergency", "ambulance", "911", "urgent"],
    "pain": ["pain", "hurt", "ache", "suffer", "wound", "sore"],
}

BLACKLIST = ["Spain", "Paint", "Painter", "Pillow", "Farm", "Farmer", "Army", "Breakfast", "Sweetheart", "Caterpillar"]

def clean_and_organized_import():
    if not WLASL_JSON.exists():
        logger.error(f"Metadata not found: {WLASL_JSON}")
        return

    # Clear output directory to start fresh
    if OUTPUT_DIR.exists():
        logger.info(f"Clearing existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load WLASL metadata
    logger.info(f"Loading metadata from {WLASL_JSON}...")
    with open(WLASL_JSON, 'r') as f:
        wlasl_data = json.load(f)

    stats = {term: 0 for term in MEDICAL_TERM_MAPPING}
    total_found = 0
    total_imported = 0

    for entry in wlasl_data:
        gloss = entry["gloss"].lower()
        
        # Check blacklist
        if any(b.lower() == gloss for b in BLACKLIST):
            continue

        # Find matching medical term
        matched_term = None
        
        # Exact match first
        if gloss in MEDICAL_TERM_MAPPING:
            matched_term = gloss
        else:
            for term, keywords in MEDICAL_TERM_MAPPING.items():
                if any(kw == gloss for kw in keywords):
                    matched_term = term
                    break
        
        if not matched_term:
            continue

        # Process instances
        instances = entry.get("instances", [])
        for inst in instances:
            video_id = inst["video_id"]
            video_file = WLASL_VIDEOS / f"{video_id}.mp4"
            
            if not video_file.exists():
                continue
            
            # Metadata: framing info
            frame_start = inst.get("frame_start", 1)
            frame_end = inst.get("frame_end", -1)
            
            # Check for corrupted files (size < 0.1 MB)
            file_size = video_file.stat().st_size
            if file_size < 102400:
                continue

            # Create target directory
            target_dir = OUTPUT_DIR / matched_term
            target_dir.mkdir(parents=True, exist_ok=True)

            # NEW: Save framing in filename: term_id_start_end.mp4
            # If frame_end is -1, it means the whole video. 
            # We'll use 0 as a placeholder for "default/whole".
            fs = frame_start if frame_start >= 0 else 0
            fe = frame_end if frame_end >= 0 else 0
            
            target_file = target_dir / f"{matched_term}_{video_id}_{fs}_{fe}.mp4"
            
            try:
                shutil.copy2(video_file, target_file)
                stats[matched_term] += 1
                total_imported += 1
            except Exception as e:
                logger.error(f"Error copying {video_file}: {e}")

    logger.info("=" * 50)
    logger.info(f"CLEANUP & IMPORT COMPLETE: {total_imported} videos")
    for term, count in stats.items():
        logger.info(f"{term:20}: {count} videos")
    logger.info("=" * 50)

if __name__ == "__main__":
    clean_and_organized_import()
