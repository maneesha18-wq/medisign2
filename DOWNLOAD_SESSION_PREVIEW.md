# Interactive Download Session - Example Preview

This shows what you'll see when running: `python download_youtube_medical.py`

## Full Session Example

```
PS C:\Users\vishn\OneDrive\Desktop\New folder\medisign> python download_youtube_medical.py

======================================================================
🎬 INTERACTIVE YOUTUBE DOWNLOADER
======================================================================

📋 INSTRUCTIONS:
  1. Search YouTube for each medical sign language video
  2. Copy the full URL (https://www.youtube.com/watch?v=...)
  3. Paste it when prompted
  4. Type 'skip' to skip a term, 'quit' to exit

🎥 HEART_ATTACK (target: 3 videos)
   Description: Cardiac emergency sign
   🔍 Search YouTube for: medical sign language heart attack
   📁 Folder: dataset/raw_videos/heart_attack
   ──────────────────────────────────────────────────────────────

  [1/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=dQw4w9WgXcQ

  ⏳ Downloading: https://www.youtube.com/watch?v=dQw4w9WgXcQ
  ✓ Downloaded: heart_attack_01.mp4 (45.3 MB)
  ✓ Downloaded (1/3)

  [2/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=jNQXAC9IVRw

  ⏳ Downloading: https://www.youtube.com/watch?v=jNQXAC9IVRw
  ✓ Downloaded: heart_attack_02.mp4 (38.1 MB)
  ✓ Downloaded (2/3)

  [3/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=9bZkp7q19f0

  ⏳ Downloading: https://www.youtube.com/watch?v=9bZkp7q19f0
  ✓ Downloaded: heart_attack_03.mp4 (44.2 MB)
  ✓ Downloaded (3/3)

🎥 DIABETES (target: 3 videos)
   Description: Blood sugar disorder sign
   🔍 Search YouTube for: ASL sign for diabetes mellitus
   📁 Folder: dataset/raw_videos/diabetes
   ──────────────────────────────────────────────────────────────

  [1/3] Enter YouTube URL (or 'skip'/'quit'): skip
  ↩️  Skipped diabetes

🎥 BROKEN_ARM (target: 3 videos)
   Description: Bone fracture sign
   🔍 Search YouTube for: sign language broken arm fracture
   📁 Folder: dataset/raw_videos/broken_arm
   ──────────────────────────────────────────────────────────────

  [1/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=kJQP7kiw9Fk

  ⏳ Downloading: https://www.youtube.com/watch?v=kJQP7kiw9Fk
  ✓ Downloaded: broken_arm_01.mp4 (41.2 MB)
  ✓ Downloaded (1/3)

  [2/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=FdHSqSOlXe0

  ⏳ Downloading: https://www.youtube.com/watch?v=FdHSqSOlXe0
  ✗ Download failed. Retries exhausted. Try another URL.

  [2/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=ZYpyNq3V26o

🎥 FEVER (target: 3 videos)
   ... (continuing for remaining terms)

[After all terms are processed...]

==========================================================
📊 DOWNLOAD REPORT - Medical Sign Language Videos
==========================================================
Generated: 2024-01-15 14:32:18
Base directory: dataset/raw_videos

──────────────────────────────────────────────────────────
Medical Term           Videos       Size (MB)       Status
──────────────────────────────────────────────────────────
heart_attack           3            127.6           ✅ Complete (3/3)
diabetes               0            0.0             ❌ No videos
broken_arm             3            112.8           ✅ Complete (3/3)
fever                  2            83.4            ⏳ Partial (2/3)
medication             3            109.2           ✅ Complete (3/3)
headache               1            42.1            ⏳ Partial (1/3)
hospital               3            118.5           ✅ Complete (3/3)
surgeon                3            106.7           ✅ Complete (3/3)
emergency              2            94.6            ⏳ Partial (2/3)
pain                   2            87.3            ⏳ Partial (2/3)
──────────────────────────────────────────────────────────
TOTAL                  22           781.2           (22/30 target)
==========================================================

📈 STATISTICS:
  ✓ Total videos downloaded: 22
  ✓ Total dataset size: 781.2 MB
  ✓ Average per video: 35.5 MB
  ✓ Completion rate: 6/10 terms fully done
  ⏳ Partial terms: 4
  ❌ Empty terms: 1
  ⚠️ Failed downloads: 1

⚠️ FAILED DOWNLOADS:
  1. [broken_arm] Download failed after retries
     URL: https://www.youtube.com/watch?v=FdHSqSOlXe0

==========================================================
✅ NEXT STEPS:
  1. Verify videos: ls dataset/raw_videos/*/
  2. python scripts/2_preprocess_videos.py
  3. python scripts/3_extract_features.py
  4. python scripts/4_train_medical.py
  5. python scripts/5_verify_pipeline.py
  6. python app_medical.py
==========================================================

📄 Detailed report saved to: download_report.json
```

## What Each Message Means

### During Download:
| Icon | Meaning |
|------|---------|
| `⏳` | Starting download |
| `🔄` | Retrying after failure |
| `✓` | Successfully downloaded |
| `❌` | Download failed |
| `✅` | Term completed |
| `⏳` | Term partially done |
| `❌` | No videos for term |
| `↩️` | Skipped this term |

### Commands You Can Use:

1. **Paste a YouTube URL**
   ```
   [1/3] Enter YouTube URL (or 'skip'/'quit'): https://www.youtube.com/watch?v=abc123
   ```

2. **Skip a Term** (move to next)
   ```
   [1/3] Enter YouTube URL (or 'skip'/'quit'): skip
   ```

3. **Quit the Entire Process**
   ```
   [1/3] Enter YouTube URL (or 'skip'/'quit'): quit
   ```

## Final Report Files Generated

### 1. Console Output
Shows summary table with all statistics (printed above)

### 2. JSON Report (`download_report.json`)
```json
{
  "heart_attack": {
    "folder": "dataset/raw_videos/heart_attack",
    "description": "Cardiac emergency sign",
    "videos": [
      {
        "filename": "heart_attack_01.mp4",
        "size_mb": 45.3,
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "status": "success",
        "download_time": "2024-01-15T14:22:33.451230"
      },
      {
        "filename": "heart_attack_02.mp4",
        "size_mb": 38.1,
        "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "status": "success",
        "download_time": "2024-01-15T14:25:18.923456"
      },
      {
        "filename": "heart_attack_03.mp4",
        "size_mb": 44.2,
        "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "status": "success",
        "download_time": "2024-01-15T14:28:45.234567"
      }
    ],
    "count": 3,
    "size_mb": 127.6
  },
  "diabetes": {
    "folder": "dataset/raw_videos/diabetes",
    "description": "Blood sugar disorder sign",
    "videos": [],
    "count": 0,
    "size_mb": 0.0
  }
  ... (8 more terms)
}
```

## Time Estimates

| Number of Videos | Time Estimate |
|------------------|---------------|
| 5-10 videos | 20-30 minutes |
| 10-20 videos | 30-60 minutes |
| 20-30 videos | 60-120 minutes |
| 30+ videos | 2+ hours |

*(Depends on video length, quality, and internet speed)*

## What Happens Next?

After download completes, you'll have:
```
dataset/raw_videos/
├── heart_attack/
│   ├── heart_attack_01.mp4 (45.3 MB)
│   ├── heart_attack_02.mp4 (38.1 MB)
│   └── heart_attack_03.mp4 (44.2 MB)
├── diabetes/ (empty - skipped)
├── broken_arm/
│   ├── broken_arm_01.mp4
│   ├── broken_arm_02.mp4
│   └── broken_arm_03.mp4
└── ... (other terms)
```

Then run the preprocessing pipeline:
```powershell
python scripts/2_preprocess_videos.py      # ~10 min
python scripts/3_extract_features.py       # ~5 min
python scripts/4_train_medical.py          # ~30 min
python scripts/5_verify_pipeline.py        # ~1 min
python app_medical.py                      # Deploy!
```

## Interactive Features Explained

### Smart Retry System
If a download fails:
1. Waits 2 seconds
2. Automatically retries (up to 3 times)
3. Shows which attempt: "🔄 Retry 2/3"
4. If all retries fail, shows message and asks for new URL

### URL Validation
- Must start with `http` or `https`
- Invalid URLs show error: "❌ Invalid input. URL must start with 'http'"

### Skip/Quit Commands
- **skip**: Moves to next medical term immediately
- **quit**: Exits script entirely, saves report

### Real-time Tracking
- Shows current progress: `[2/3]` means 2 of 3 downloaded
- Updating counts as downloads complete
- File size displayed immediately after download

## Troubleshooting During Download

### "Download timeout"
- Network is slow, trying again (script retries automatically)
- Or press Ctrl+C to exit and adjust TIMEOUT in script

### "File is empty"
- Download corrupted, script auto-retries
- Happens sometimes with slow connections

### "Invalid URL format"
- Double-check the URL starts with `https://`
- Copy full URL from address bar

### "Download failed after retries"
- Try a different video URL
- Check internet connection
- Video might be age-restricted or unavailable

---

**Ready to start?** Run:
```powershell
python download_youtube_medical.py
```

Or copy this to understand all 10 medical terms and prepare URLs beforehand!
