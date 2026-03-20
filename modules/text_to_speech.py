"""Text-to-Speech (TTS) module using gTTS for medical sign language predictions.

Features:
- Convert predicted medical terms to audio using gTTS
- Save audio files with timestamps
- Handle file overwrites safely (atomic writes)
- Support multiple languages (default: English)
"""

from __future__ import annotations
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import gtts
from googletrans import Translator

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech converter for predictions."""

    def __init__(
        self,
        output_dir: str = "logs/audio",
        language: str = "en",
        slow: bool = False,
    ):
        """Initialize TTS converter.

        Args:
            output_dir: Directory to save audio files.
            language: Language code (e.g., 'en', 'es', 'fr').
            slow: If True, speak slowly for better clarity.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.default_language = language
        self.slow = slow
        
        # Initialize translator with safer defaults
        try:
            self.translator = Translator(service_urls=['translate.googleapis.com'])
            logger.info("Translator initialized with googleapis.com")
        except Exception as e:
            logger.warning(f"Failed to initialize Translator: {e}")
            self.translator = None
            
        logger.info(f"TTS initialized: {output_dir} ({language})")

    def convert_and_save(
        self,
        text: str,
        label: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Convert text to speech and save to file.

        Args:
            text: Text to convert to speech.
            label: Optional label prefix for filename.
            target_language: Optional target language (overrides default).

        Returns:
            Tuple of (audio_file_path, error_message, translated_text)
            Returns (None, error_msg, None) on failure.
        """
        try:
            # Determine language
            lang = target_language if target_language else self.default_language

            # Translate if lang is not 'en'
            speech_text = text
            try:
                if lang and lang != "en":
                    logger.info(f"Translating '{text}' to '{lang}'...")
                    
                    try:
                        # Try with the persistent translator first
                        if not hasattr(self, 'translator') or not self.translator:
                            self.translator = Translator(service_urls=['translate.googleapis.com'])
                        
                        translated = self.translator.translate(text, dest=lang)
                    except Exception as e:
                        logger.warning(f"First translation attempt failed: {e}. Retrying with fresh translator...")
                        # Fallback: Fresh translator with different URL
                        temp_translator = Translator(service_urls=['translate.google.com'])
                        translated = temp_translator.translate(text, dest=lang)

                    if translated and translated.text:
                        speech_text = translated.text
                        # Safe logging for non-ASCII terminals
                        safe_translated = speech_text.encode('ascii', 'backslashreplace').decode('ascii')
                        logger.info(f"Translation successful: '{text}' -> '{safe_translated}' ({lang})")
                    else:
                        logger.warning(f"Translation returned empty result for '{text}' to '{lang}'")
                else:
                    logger.info(f"Skipping translation: language is '{lang}'")
            except Exception as tr_err:
                logger.error(f"Translation failed: {tr_err}")
                import traceback
                logger.debug(traceback.format_exc())
                speech_text = text

            # Sanitize text for filename
            safe_label = (label or "prediction").replace(" ", "_").lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # ms precision
            filename = f"{safe_label}_{timestamp}.mp3"
            filepath = self.output_dir / filename

            # Generate speech using gTTS
            safe_speech = speech_text.encode('ascii', 'backslashreplace').decode('ascii')
            logger.info(f"Generating audio for language '{lang}': {safe_speech}")
            tts = gtts.gTTS(text=speech_text, lang=lang, slow=self.slow)

            # Save to temporary file first, then rename (atomic write)
            temp_path = filepath.with_suffix(".tmp.mp3")
            tts.save(temp_path)

            # Atomic rename
            temp_path.rename(filepath)

            print(f"[OK] Audio saved: {filepath}")
            return str(filepath), None, speech_text

        except Exception as e:
            error_msg = f"TTS error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, None

    def list_recent_audio(self, limit: int = 10) -> list[str]:
        """List recent audio files.

        Args:
            limit: Max number of files to return.

        Returns:
            List of audio file paths (most recent first).
        """
        audio_files = sorted(
            self.output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return [str(p) for p in audio_files[:limit]]

    def cleanup_old_files(self, keep_last_n: int = 50) -> int:
        """Remove old audio files, keeping only most recent N.

        Args:
            keep_last_n: Number of most recent files to keep.

        Returns:
            Number of files deleted.
        """
        audio_files = sorted(
            self.output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime
        )
        excess = audio_files[:-keep_last_n]
        for f in excess:
            f.unlink()
        print(f"[OK] Cleaned up {len(excess)} old audio files")
        return len(excess)


def main(argv=None):
    """CLI demo: Convert text to speech."""
    import argparse

    parser = argparse.ArgumentParser(description="Text-to-Speech converter")
    parser.add_argument("text", nargs="?", default="Pharmacy", help="Text to convert")
    parser.add_argument(
        "--label", type=str, default="prediction", help="Filename prefix"
    )
    parser.add_argument("--language", type=str, default="en", help="Language code")
    parser.add_argument("--slow", action="store_true", help="Speak slowly")
    parser.add_argument(
        "--output-dir", type=str, default="logs/audio", help="Output directory"
    )
    args = parser.parse_args(argv)

    tts = TextToSpeech(
        output_dir=args.output_dir,
        language=args.language,
        slow=args.slow,
    )

    audio_path, error, translated_text = tts.convert_and_save(args.text, label=args.label)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Audio saved: {audio_path}")
        if translated_text:
            print(f"Translated text: {translated_text}")
        print(f"Recent files: {tts.list_recent_audio(5)}")


if __name__ == "__main__":
    main()
