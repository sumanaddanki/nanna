#!/usr/bin/env python3
"""
Batch Telugu Voice Collector
Downloads and processes multiple videos for voice training

Usage:
    # Download from a specific channel (last 10 videos)
    python3.11 batch_collect_voices.py --channel @telugutechoffice --voice arjun --limit 10

    # Download from a playlist
    python3.11 batch_collect_voices.py --playlist PLxxxxx --voice ravi --limit 5

    # Download from a list of URLs
    python3.11 batch_collect_voices.py --file urls.txt --voice lakshmi
"""

import os
import argparse
import subprocess
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Directories
BASE_DIR = Path(__file__).parent
VOICES_DIR = BASE_DIR / "voices"
RAW_DIR = VOICES_DIR / "raw"
PROCESSED_DIR = VOICES_DIR / "processed"

VOICES = ["ravi", "lakshmi", "kiran", "priya", "arjun", "ananya"]

def setup_dirs():
    """Create necessary directories."""
    for voice in VOICES:
        (RAW_DIR / voice).mkdir(parents=True, exist_ok=True)
        (PROCESSED_DIR / voice).mkdir(parents=True, exist_ok=True)

def get_channel_videos(channel: str, limit: int = 10) -> list:
    """Get video URLs from a YouTube channel."""
    print(f"Fetching videos from channel: {channel}")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "-j",
        f"--playlist-end={limit}",
        f"https://www.youtube.com/{channel}/videos"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    videos = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                videos.append({
                    "id": data.get("id"),
                    "url": f"https://www.youtube.com/watch?v={data.get('id')}",
                    "title": data.get("title", "Unknown")
                })
            except:
                pass

    return videos

def get_playlist_videos(playlist_id: str, limit: int = 10) -> list:
    """Get video URLs from a YouTube playlist."""
    print(f"Fetching videos from playlist: {playlist_id}")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "-j",
        f"--playlist-end={limit}",
        f"https://www.youtube.com/playlist?list={playlist_id}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    videos = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                videos.append({
                    "id": data.get("id"),
                    "url": f"https://www.youtube.com/watch?v={data.get('id')}",
                    "title": data.get("title", "Unknown")
                })
            except:
                pass

    return videos

def download_audio(video: dict, voice: str) -> Path:
    """Download audio from a YouTube video."""
    output_path = RAW_DIR / voice / f"{video['id']}.wav"

    if output_path.exists():
        print(f"  Skip (exists): {video['title'][:50]}")
        return output_path

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", str(output_path).replace('.wav', '.%(ext)s'),
        video["url"]
    ]

    print(f"  Downloading: {video['title'][:50]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    return output_path if output_path.exists() else None

def process_audio(audio_path: Path, voice: str) -> Path:
    """Convert audio to training format (22kHz mono)."""
    if not audio_path or not audio_path.exists():
        return None

    output_path = PROCESSED_DIR / voice / audio_path.name

    if output_path.exists():
        return output_path

    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path),
        "-ar", "22050",
        "-ac", "1",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True)
    return output_path if output_path.exists() else None

def get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds."""
    if not audio_path or not audio_path.exists():
        return 0

    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0

def show_status():
    """Show collection status for all voices."""
    print("\n" + "="*60)
    print("Telugu Voice Collection Status")
    print("="*60)

    total_hours = 0
    for voice in VOICES:
        raw_files = list((RAW_DIR / voice).glob("*.wav"))
        processed_files = list((PROCESSED_DIR / voice).glob("*.wav"))

        duration = sum(get_audio_duration(f) for f in processed_files)
        hours = duration / 3600
        total_hours += hours

        progress = min(100, int(hours / 5 * 100))
        bar = "█" * (progress // 5) + "░" * (20 - progress // 5)

        status = "✓ READY" if hours >= 5 else f"{5-hours:.1f}h more"
        print(f"  {voice:10} | {len(raw_files):3} files | {hours:5.2f}h | [{bar}] {status}")

    print("="*60)
    print(f"  Total collected: {total_hours:.2f} hours")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Batch collect Telugu voice samples")
    parser.add_argument("--channel", help="YouTube channel (e.g., @telugutechoffice)")
    parser.add_argument("--playlist", help="YouTube playlist ID")
    parser.add_argument("--file", help="File with video URLs (one per line)")
    parser.add_argument("--voice", choices=VOICES, help="Target voice to train")
    parser.add_argument("--limit", type=int, default=10, help="Max videos to download")
    parser.add_argument("--status", action="store_true", help="Show collection status")

    args = parser.parse_args()

    setup_dirs()

    if args.status:
        show_status()
        return

    # Get video list
    videos = []

    if args.channel:
        videos = get_channel_videos(args.channel, args.limit)
    elif args.playlist:
        videos = get_playlist_videos(args.playlist, args.limit)
    elif args.file:
        with open(args.file) as f:
            for i, line in enumerate(f):
                url = line.strip()
                if url and 'youtube' in url:
                    video_id = url.split('v=')[-1].split('&')[0]
                    videos.append({
                        "id": video_id,
                        "url": url,
                        "title": f"Video {i+1}"
                    })
    else:
        print("Usage: python3.11 batch_collect_voices.py --channel @channel --voice arjun")
        print("       python3.11 batch_collect_voices.py --status")
        return

    if not args.voice:
        print("Error: --voice is required for downloading")
        return

    print(f"\nFound {len(videos)} videos")
    print(f"Downloading for voice: {args.voice}")
    print("-" * 40)

    # Download and process
    for video in videos:
        audio = download_audio(video, args.voice)
        if audio:
            process_audio(audio, args.voice)

    # Show final status
    show_status()

if __name__ == "__main__":
    main()
