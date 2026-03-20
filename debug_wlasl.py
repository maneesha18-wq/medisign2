#!/usr/bin/env python
"""Debug WLASL video finding"""

import json
from pathlib import Path

wlasl_path = Path(r"C:\Users\vishn\Downloads\archive\videos")
metadata_path = Path(r"C:\Users\vishn\Downloads\archive\WLASL_v0.3.json")

# Load metadata
with open(metadata_path) as f:
    data = json.load(f)

print(f"Total entries in WLASL: {len(data)}")

# Find all medical entries
medical_keywords = [
    "heart",
    "diabetes",
    "broken",
    "arm",
    "fever",
    "medicine",
    "medication",
    "headache",
    "hospital",
    "doctor",
    "surgeon",
    "emergency",
    "pain",
    "hurt",
    "ache",
    "sugar",
    "blood",
    "temperature",
]

found_entries = []
for entry in data:
    gloss = entry["gloss"].lower()
    if any(kw in gloss for kw in medical_keywords):
        found_entries.append(entry)

print(f"\nFound {len(found_entries)} medical entries")
print("\nChecking video files...")

found_count = 0
not_found_count = 0

for i, entry in enumerate(found_entries[:20]):  # Check first 20
    gloss = entry["gloss"]

    for instance in entry.get("instances", [])[:1]:  # First instance only
        video_id = instance.get("video_id")
        if not video_id:
            continue

        video_path = wlasl_path / f"{video_id}.mp4"
        exists = video_path.exists()

        if exists:
            found_count += 1
            print(f"✓ {gloss:30} ID:{video_id:6} -> EXISTS")
        else:
            if not_found_count < 5:
                print(f"✗ {gloss:30} ID:{video_id:6} -> NOT FOUND")
            not_found_count += 1

print(f"\nSummary: {found_count} found, {not_found_count} not found")

# Check if any video file exists at all
sample = list(wlasl_path.glob("*.mp4"))
if sample:
    print(f"\nSample video files exist (showing first 5):")
    for f in sample[:5]:
        print(f"  {f.name}")
