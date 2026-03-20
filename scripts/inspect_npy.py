import numpy as np
from pathlib import Path

files = list(Path("dataset").rglob("*.npy")) + list(Path(".").glob("out_feats.npy"))
files = sorted({str(f) for f in files})
print("Found npy files:")
for f in files:
    try:
        a = np.load(f)
        print(f, "->", a.shape, a.dtype)
    except Exception as e:
        print(f, "-> load error", e)
