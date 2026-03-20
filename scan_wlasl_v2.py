
import json
from pathlib import Path

WLASL_JSON = Path(r"C:\Users\vishn\Downloads\archive\WLASL_v0.3.json")

with open(WLASL_JSON, 'r') as f:
    data = json.load(f)

# Expanded medical terms
MEDICAL_GLOSSES = {
    "heart_attack": ["heart attack", "heart", "attack", "cardiac"],
    "diabetes": ["diabetes", "sugar", "insulin"],
    "broken_arm": ["broken arm", "arm", "break", "broken", "fracture", "bone", "injury"],
    "fever": ["fever", "temperature", "sick", "illness", "cough", "cold", "flu"],
    "medication": ["medicine", "drug", "pill", "tablet", "medication", "pharmacy", "prescription"],
    "headache": ["headache", "migraine", "head"],
    "hospital": ["hospital", "clinic", "nurse", "patient", "treatment"],
    "surgeon": ["surgeon", "doctor", "physician", "surgery", "operation"],
    "emergency": ["emergency", "ambulance", "911", "urgent"],
    "pain": ["pain", "hurt", "ache", "suffer", "wound", "sore"],
}

found_counts = {k: [] for k in MEDICAL_GLOSSES}
total_videos = 0

for entry in data:
    gloss = entry["gloss"].lower()
    for category, keywords in MEDICAL_GLOSSES.items():
        if any(kw == gloss for kw in keywords):
            indices = [inst["video_id"] for inst in entry.get("instances", [])]
            found_counts[category].append((gloss, len(indices)))
            total_videos += len(indices)
            break

print(f"Summary of potential medical data:")
for cat, glosses in found_counts.items():
    print(f"{cat}:")
    for g, c in glosses:
        print(f"  - {g} ({c})")
print(f"Total potential videos: {total_videos}")
