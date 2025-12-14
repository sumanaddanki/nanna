#!/usr/bin/env python3
"""
Telugu Voice Sample Collector
Downloads audio from YouTube videos for voice training

Usage:
    python3.11 collect_voice_samples.py --url "https://youtube.com/watch?v=xxx" --voice ravi

Requirements:
    pip3.11 install yt-dlp whisper pyannote-audio
"""

import os
import argparse
import subprocess
import json
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
VOICES_DIR = BASE_DIR / "voices"
RAW_DIR = VOICES_DIR / "raw"
PROCESSED_DIR = VOICES_DIR / "processed"

def setup_dirs():
    """Create necessary directories."""
    for voice in ["ravi", "lakshmi", "kiran", "priya", "arjun", "ananya"]:
        (RAW_DIR / voice).mkdir(parents=True, exist_ok=True)
        (PROCESSED_DIR / voice).mkdir(parents=True, exist_ok=True)

def download_audio(url: str, voice: str) -> Path:
    """Download audio from YouTube video."""
    output_template = str(RAW_DIR / voice / "%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",
        "--audio-quality", "0",  # Best quality
        "-o", output_template,
        url
    ]

    print(f"Downloading: {url}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    # Find the downloaded file
    video_id = url.split("v=")[-1].split("&")[0]
    audio_file = RAW_DIR / voice / f"{video_id}.wav"

    return audio_file if audio_file.exists() else None

def convert_to_training_format(audio_path: Path, voice: str) -> Path:
    """Convert audio to training format (22kHz mono)."""
    output_path = PROCESSED_DIR / voice / audio_path.name

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-ar", "22050",  # 22kHz sample rate
        "-ac", "1",       # Mono
        str(output_path)
    ]

    print(f"Converting: {audio_path.name}")
    subprocess.run(cmd, capture_output=True)

    return output_path if output_path.exists() else None

def transcribe_audio(audio_path: Path) -> dict:
    """Transcribe audio using Whisper."""
    try:
        import whisper

        print(f"Transcribing: {audio_path.name}")
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_path))

        # Save transcript
        transcript_path = audio_path.with_suffix(".json")
        with open(transcript_path, "w") as f:
            json.dump(result, f, indent=2)

        return result
    except ImportError:
        print("Whisper not installed. Run: pip3.11 install openai-whisper")
        return None

def get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip()) if result.stdout else 0

def show_collection_status():
    """Show current collection status."""
    print("\n" + "="*50)
    print("Voice Collection Status")
    print("="*50)

    for voice in ["ravi", "lakshmi", "kiran", "priya", "arjun", "ananya"]:
        raw_files = list((RAW_DIR / voice).glob("*.wav"))
        processed_files = list((PROCESSED_DIR / voice).glob("*.wav"))

        total_duration = sum(get_audio_duration(f) for f in processed_files)
        hours = total_duration / 3600

        status = "READY" if hours >= 5 else "NEED MORE"
        print(f"  {voice:10} | {len(raw_files):3} files | {hours:.1f}h / 5h | {status}")

    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="Collect Telugu voice samples")
    parser.add_argument("--url", help="YouTube video URL")
    parser.add_argument("--voice", choices=["ravi", "lakshmi", "kiran", "priya", "arjun", "ananya"],
                       help="Target voice")
    parser.add_argument("--status", action="store_true", help="Show collection status")

    args = parser.parse_args()

    setup_dirs()

    if args.status:
        show_collection_status()
        return

    if not args.url or not args.voice:
        print("Usage: python3.11 collect_voice_samples.py --url 'URL' --voice VOICE")
        print("       python3.11 collect_voice_samples.py --status")
        return

    # Download
    audio_file = download_audio(args.url, args.voice)
    if not audio_file:
        print("Download failed")
        return

    # Convert
    processed = convert_to_training_format(audio_file, args.voice)
    if not processed:
        print("Conversion failed")
        return

    # Transcribe
    transcribe_audio(processed)

    # Show status
    show_collection_status()

if __name__ == "__main__":
    main()
