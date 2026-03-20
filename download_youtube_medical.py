#!/usr/bin/env python3
"""
MediSign Medical Sign Language Dataset Auto-Downloader

Downloads medical sign language videos from YouTube and organizes them
into folders by medical term for the MediSign project.

Usage:
    python download_youtube_medical.py

Requirements:
    pip install yt-dlp
    pip install requests
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Medical terms to download
MEDICAL_TERMS = {
    "heart_attack": {
        "search_keywords": [
            "heart attack sign language",
            "ASL heart attack",
            "deaf medical heart",
        ],
        "target_videos": 3,
        "description": "Cardiac emergency sign",
    },
    "diabetes": {
        "search_keywords": [
            "diabetes sign language",
            "ASL diabetes",
            "medical sugar disease",
        ],
        "target_videos": 3,
        "description": "Blood sugar disorder sign",
    },
    "broken_arm": {
        "search_keywords": ["broken arm sign language", "ASL fracture", "injury sign"],
        "target_videos": 3,
        "description": "Bone fracture sign",
    },
    "fever": {
        "search_keywords": [
            "fever sign language",
            "ASL fever",
            "high temperature sign",
        ],
        "target_videos": 3,
        "description": "High temperature sign",
    },
    "medication": {
        "search_keywords": [
            "medication sign language",
            "ASL medicine",
            "pill drug sign",
        ],
        "target_videos": 3,
        "description": "Medicine administration sign",
    },
    "headache": {
        "search_keywords": ["headache sign language", "ASL headache", "head pain"],
        "target_videos": 3,
        "description": "Head pain sign",
    },
    "hospital": {
        "search_keywords": [
            "hospital sign language",
            "ASL hospital",
            "medical facility sign",
        ],
        "target_videos": 3,
        "description": "Healthcare facility sign",
    },
    "surgeon": {
        "search_keywords": [
            "surgeon sign language",
            "ASL doctor",
            "professional medical",
        ],
        "target_videos": 3,
        "description": "Medical professional sign",
    },
    "emergency": {
        "search_keywords": [
            "emergency sign language",
            "ASL emergency",
            "urgent medical",
        ],
        "target_videos": 3,
        "description": "Urgent situation sign",
    },
    "pain": {
        "search_keywords": ["pain sign language", "ASL pain", "hurt suffering"],
        "target_videos": 3,
        "description": "Physical discomfort sign",
    },
}

# Download settings
DOWNLOAD_DIR = "dataset/raw_videos"
VIDEO_FORMAT = "best[ext=mp4]/best"
MAX_RETRIES = 3
TIMEOUT = 300  # 5 minutes per video
MIN_VIDEO_LENGTH = 5  # seconds
MAX_VIDEO_LENGTH = 600  # seconds

# ============================================================================
# UTILITIES
# ============================================================================


class MedicalDownloader:
    """Main downloader class for medical sign language videos"""

    def __init__(self, base_dir=DOWNLOAD_DIR):
        self.base_dir = Path(base_dir)
        self.download_report = {}
        self.total_size = 0
        self.total_videos = 0
        self.failed_downloads = []

    def check_dependencies(self):
        """Verify yt-dlp is installed"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"], capture_output=True, text=True, timeout=5
            )
            version = result.stdout.strip()
            logger.info(f"✓ yt-dlp installed: {version}")
            return True
        except FileNotFoundError:
            logger.error("❌ yt-dlp not installed")
            logger.error("Install with: pip install yt-dlp")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking yt-dlp: {e}")
            return False

    def create_folder_structure(self):
        """Create medical term folders"""
        logger.info("\n📁 Creating folder structure...")

        for term in MEDICAL_TERMS.keys():
            term_dir = self.base_dir / term
            term_dir.mkdir(parents=True, exist_ok=True)
            self.download_report[term] = {
                "folder": str(term_dir),
                "videos": [],
                "count": 0,
                "size_mb": 0.0,
                "description": MEDICAL_TERMS[term]["description"],
            }
            logger.info(f"  ✓ {term_dir}")

        return True

    def search_youtube_urls(self, search_query, count=3):
        """Search YouTube for videos matching query"""
        urls = []

        # YouTube search URL (basic - you may need to implement more robust search)
        search_keywords = quote(search_query)
        search_url = f"https://www.youtube.com/results?search_query={search_keywords}"

        try:
            # This is a simple approach - in production, use YouTube API
            # For now, we provide guidance to user
            logger.debug(f"Search query: {search_query}")
        except Exception as e:
            logger.debug(f"Search error: {e}")

        return urls

    def download_video(self, url, output_dir, filename_prefix):
        """Download single video from YouTube with retry logic"""
        output_path = Path(output_dir) / f"{filename_prefix}.mp4"

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if attempt == 1:
                    logger.info(f"  ⏳ Downloading: {url}")
                else:
                    logger.info(f"  🔄 Retry {attempt}/{MAX_RETRIES}: {url}")

                cmd = [
                    "yt-dlp",
                    "-f",
                    VIDEO_FORMAT,
                    "-o",
                    str(output_path),
                    "--quiet",
                    "--no-warnings",
                    "--socket-timeout",
                    str(TIMEOUT),
                    "--retries",
                    "3",
                    url,
                ]

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=TIMEOUT
                )

                if result.returncode == 0 and output_path.exists():
                    file_size_mb = output_path.stat().st_size / (1024 * 1024)

                    # Verify file is valid
                    if file_size_mb > 0:
                        logger.info(
                            f"  ✓ Downloaded: {output_path.name} ({file_size_mb:.1f} MB)"
                        )
                        return output_path, file_size_mb
                    else:
                        logger.warning(f"  ⚠️  File is empty, retrying...")
                        if output_path.exists():
                            output_path.unlink()
                        continue
                else:
                    if attempt < MAX_RETRIES:
                        logger.debug(
                            f"  Download attempt {attempt} failed, retrying..."
                        )
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        logger.warning(
                            f"  ❌ Download failed after {MAX_RETRIES} attempts"
                        )
                        return None, 0

            except subprocess.TimeoutExpired:
                if attempt < MAX_RETRIES:
                    logger.debug(f"  Timeout on attempt {attempt}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.warning(
                        f"  ❌ Download timeout after {MAX_RETRIES} attempts"
                    )
                    return None, 0
            except Exception as e:
                if attempt < MAX_RETRIES:
                    logger.debug(f"  Error on attempt {attempt}: {e}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.warning(
                        f"  ❌ Download error after {MAX_RETRIES} attempts: {e}"
                    )
                    return None, 0

        return None, 0

    def download_term_videos(self, term, keywords, count):
        """Download videos for a medical term"""
        logger.info(f"\n🎬 Downloading videos for: {term}")
        logger.info(f"   Target: {count} videos | {keywords[0]}")

        term_dir = self.base_dir / term
        downloaded = 0

        # For each search keyword, try to find videos
        for keyword_idx, keyword in enumerate(keywords):
            if downloaded >= count:
                break

            logger.info(f"   Searching: '{keyword}'...")

            # Build YouTube search URL
            search_query = quote(keyword)

            # Try to get videos from search
            # Note: Direct YouTube search is complex; here we use a list of common channels
            video_urls = self._get_youtube_urls_for_keyword(keyword)

            for url_idx, url in enumerate(video_urls):
                if downloaded >= count:
                    break

                filename = f"{term}_{downloaded + 1:02d}"
                video_path, size_mb = self.download_video(url, term_dir, filename)

                if video_path:
                    downloaded += 1
                    self.total_videos += 1
                    self.total_size += size_mb

                    self.download_report[term]["videos"].append(
                        {
                            "filename": video_path.name,
                            "size_mb": size_mb,
                            "url": url,
                            "download_time": datetime.now().isoformat(),
                        }
                    )
                    self.download_report[term]["count"] += 1
                    self.download_report[term]["size_mb"] += size_mb
                else:
                    self.failed_downloads.append(
                        {"term": term, "url": url, "reason": "Download failed"}
                    )

        # If no videos downloaded, show guidance
        if downloaded == 0:
            logger.warning(f"   ℹ️  No videos available from automatic search")
            logger.warning(f"   💡 Tip: Manually search YouTube for '{keywords[0]}'")
            logger.warning(f"       and use the YOUTUBE_DOWNLOAD_GUIDE.md")
        else:
            logger.info(f"   ✓ Downloaded {downloaded}/{count} videos")

    def _get_youtube_urls_for_keyword(self, keyword):
        """Get YouTube URLs for keyword (returns example URLs)"""
        # This returns popular channels - in production, implement actual YouTube search

        popular_channels = {
            "ASL": [
                "https://www.youtube.com/results?search_query=ASL+medical+signs",
                "https://www.youtube.com/results?search_query=sign+language+tutorial",
            ],
            "medical": [
                "https://www.youtube.com/results?search_query=medical+sign+language+tutorial",
                "https://www.youtube.com/results?search_query=deaf+interpreter+medical",
            ],
            "deaf": [
                "https://www.youtube.com/results?search_query=deaf+medical+professionals",
            ],
        }

        # Return empty for now - will use manual URLs
        return []

    def generate_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 75)
        print("📊 DOWNLOAD REPORT - Medical Sign Language Videos")
        print("=" * 75)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base directory: {self.base_dir}")

        print("\n" + "-" * 75)
        print(f"{'Medical Term':<18} {'Videos':<12} {'Size (MB)':<15} {'Status':<20}")
        print("-" * 75)

        terms_complete = 0
        terms_partial = 0
        terms_empty = 0
        total_target = 0

        for term, data in self.download_report.items():
            count = data["count"]
            size = data["size_mb"]
            target = MEDICAL_TERMS[term]["target_videos"]
            total_target += target

            if count == 0:
                status = "❌ No videos"
                terms_empty += 1
            elif count >= target:
                status = f"✅ Complete ({count}/{target})"
                terms_complete += 1
            else:
                status = f"⏳ Partial ({count}/{target})"
                terms_partial += 1

            print(f"{term:<18} {count:<12} {size:<15.1f} {status:<20}")

        print("-" * 75)
        avg_size = self.total_size / max(1, self.total_videos)
        print(
            f"{'TOTAL':<18} {self.total_videos:<12} {self.total_size:<15.1f} "
            f"({self.total_videos}/{total_target} target)"
        )
        print("=" * 75)

        print("\n📈 STATISTICS:")
        print(f"  ✓ Total videos downloaded: {self.total_videos}")
        print(f"  ✓ Total dataset size: {self.total_size:.1f} MB")
        print(f"  ✓ Average per video: {avg_size:.1f} MB")
        print(
            f"  ✓ Completion rate: {terms_complete}/{len(MEDICAL_TERMS)} terms fully done"
        )
        print(f"  ⏳ Partial terms: {terms_partial}")
        print(f"  ❌ Empty terms: {terms_empty}")
        print(f"  ⚠️  Failed downloads: {len(self.failed_downloads)}")

        if self.failed_downloads:
            print("\n⚠️  FAILED DOWNLOADS:")
            for i, fail in enumerate(self.failed_downloads, 1):
                print(f"  {i}. [{fail['term']}] {fail['reason']}")
                print(f"     URL: {fail['url']}")

        print("\n" + "=" * 75)
        print("✅ NEXT STEPS:")
        print("  1. Verify videos: ls dataset/raw_videos/*/")
        print("  2. python scripts/2_preprocess_videos.py")
        print("  3. python scripts/3_extract_features.py")
        print("  4. python scripts/4_train_medical.py")
        print("  5. python scripts/5_verify_pipeline.py")
        print("  6. python app_medical.py")
        print("=" * 75)

        # Save report as JSON
        report_file = Path("download_report.json")
        try:
            with open(report_file, "w") as f:
                json.dump(self.download_report, f, indent=2)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

    def run_interactive_mode(self):
        """Interactive mode for user to provide YouTube URLs"""
        print("\n" + "=" * 70)
        print("🔗 INTERACTIVE YOUTUBE DOWNLOADER")
        print("=" * 70)
        print("\n📌 INSTRUCTIONS:")
        print("  1. Search YouTube for each medical sign language video")
        print("  2. Copy the full URL (https://www.youtube.com/watch?v=...)")
        print("  3. Paste it when prompted")
        print("  4. Type 'skip' to skip a term, 'quit' to exit\n")

        skipped_terms = []

        for term in MEDICAL_TERMS.keys():
            term_dir = self.base_dir / term
            target = MEDICAL_TERMS[term]["target_videos"]

            print(f"\n📺 {term.upper()} (target: {target} videos)")
            print(f"   Description: {MEDICAL_TERMS[term]['description']}")
            print(
                f"   📍 Search YouTube for: {MEDICAL_TERMS[term]['search_keywords'][0]}"
            )
            print(f"   💾 Folder: {term_dir}")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            downloaded = 0
            term_attempts = 0
            max_attempts = target * 3  # Allow extra attempts

            while downloaded < target and term_attempts < max_attempts:
                term_attempts += 1
                url_input = input(
                    f"  [{downloaded + 1}/{target}] Enter YouTube URL (or 'skip'/'quit'): "
                ).strip()

                if not url_input:
                    print("  ⚠️  Empty input. Please enter a URL or 'skip'.")
                    continue

                if url_input.lower() == "skip":
                    print(f"  ⏭️  Skipped {term}")
                    skipped_terms.append(term)
                    break
                elif url_input.lower() == "quit":
                    print("\n🛑 Download cancelled by user")
                    return False
                elif url_input.startswith("http"):
                    filename = f"{term}_{downloaded + 1:02d}"
                    video_path, size_mb = self.download_video(
                        url_input, term_dir, filename
                    )

                    if video_path:
                        downloaded += 1
                        self.total_videos += 1
                        self.total_size += size_mb

                        self.download_report[term]["videos"].append(
                            {
                                "filename": video_path.name,
                                "size_mb": round(size_mb, 2),
                                "url": url_input,
                                "status": "success",
                                "download_time": datetime.now().isoformat(),
                            }
                        )
                        self.download_report[term]["count"] += 1
                        self.download_report[term]["size_mb"] += size_mb
                        print(f"  ✓ Downloaded ({downloaded}/{target})\n")
                    else:
                        print(
                            f"  ❌ Download failed. Retries exhausted. Try another URL.\n"
                        )
                        self.failed_downloads.append(
                            {
                                "term": term,
                                "url": url_input,
                                "reason": "Download failed after retries",
                            }
                        )
                else:
                    print(
                        f"  ❌ Invalid input. URL must start with 'http' or type 'skip'/'quit'\n"
                    )

            if downloaded == 0 and term not in skipped_terms:
                logger.warning(f"   ⚠️  No videos downloaded for {term}")

        return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("🎬 MediSign Medical Sign Language Auto-Downloader")
    print("=" * 70)
    print(
        f"Python {sys.version.split()[0]} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    # Initialize downloader
    downloader = MedicalDownloader(DOWNLOAD_DIR)

    # Check dependencies
    if not downloader.check_dependencies():
        print("\n❌ yt-dlp is required!")
        print("Install with: pip install yt-dlp")
        return False

    # Create folder structure
    if not downloader.create_folder_structure():
        logger.error("Failed to create folder structure")
        return False

    # Try interactive mode (since automatic YouTube search is complex)
    logger.info("\n🎯 Mode: Interactive Download")
    logger.info("   Please provide YouTube URLs manually\n")

    if not downloader.run_interactive_mode():
        logger.warning("Download cancelled by user")
        return False

    # Generate report
    downloader.generate_report()

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
