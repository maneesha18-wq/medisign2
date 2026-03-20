import glob
import json
from pathlib import Path


def main():
    files = sorted(Path("logs").glob("history_*.json"))
    if not files:
        print("No history files")
        return
    p = files[-1]
    print("Latest history file:", p)
    print("-----")
    print(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
