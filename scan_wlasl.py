
import json
from pathlib import Path

WLASL_JSON = Path(r"C:\Users\vishn\Downloads\archive\WLASL_v0.3.json")

with open(WLASL_JSON, 'r') as f:
    data = json.load(f)

print(f"Total glosses: {len(data)}")

medical_keywords = ["head", "pain", "hurt", "sick", "doctor", "medicine", "pill", "blood", "heart", "emergency", "hospital", "arm", "fever", "cough"]

found = []
for entry in data:
    gloss = entry["gloss"].lower()
    if any(kw in gloss for kw in medical_keywords):
        found.append(gloss)

print("Potential medical glosses found:")
print(", ".join(sorted(found)[:100]))
