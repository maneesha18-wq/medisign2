"""Split existing demo feature files into two labels for a minimal two-class demo.

Usage: python scripts/split_demo_labels.py --src demo --dst demo2 --keep 15
"""

from pathlib import Path
import shutil
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="demo")
    parser.add_argument("--dst", default="demo2")
    parser.add_argument("--keep", type=int, default=15)
    args = parser.parse_args()

    src = Path("dataset") / args.src
    dst = Path("dataset") / args.dst
    dst.mkdir(parents=True, exist_ok=True)

    files = sorted(src.glob("*.npy"))
    if len(files) < args.keep:
        raise RuntimeError("Not enough files to split")

    for i, f in enumerate(files[: args.keep]):
        dest = dst / f.name
        shutil.copy(f, dest)

    print(f"Copied {args.keep} files from {src} to {dst}")


if __name__ == "__main__":
    main()
