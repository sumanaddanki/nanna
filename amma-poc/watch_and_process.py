#!/usr/bin/env python3
"""
Watch & Process - Automated Recording Pipeline
Watches for new recordings and automatically processes them.

Run on Mac Studio:
    python watch_and_process.py

What it does:
    1. Watches voice/raw/ for new .wav files
    2. Automatically processes new recordings:
       - Convert to 22050Hz mono
       - Run speaker separation
       - Transcribe with Whisper
    3. Optionally archives to NAS

Can also pull from Mac Air:
    python watch_and_process.py --pull-from-air
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

# Paths
SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "voice" / "raw"
PROCESSED_DIR = SCRIPT_DIR / "voice" / "processed"
TOOLS_DIR = SCRIPT_DIR.parent / "tools"
SEPARATOR_SCRIPT = TOOLS_DIR / "separate_speakers.py"

# Remote settings
AIR_HOST = "air"  # Uses ~/.ssh/config
AIR_PATH = "~/git/sumanaddanki/amma-poc/voice/raw"
NAS_HOST = "aauser@192.168.1.183"
NAS_PORT = "17183"
NAS_PATH = "/volume1/homes/aauser/amma-archive"

# Processing state - track what we've already processed
processed_files = set()


def log(msg):
    """Print with timestamp"""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def pull_from_air():
    """Pull new recordings from Mac Air"""
    log("Checking Mac Air for new recordings...")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Use rsync for efficient syncing
        result = subprocess.run([
            "rsync", "-avz", "--progress",
            f"{AIR_HOST}:{AIR_PATH}/*.wav",
            str(RAW_DIR) + "/"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            if "total size is 0" not in result.stdout:
                log("✓ Synced new files from Mac Air")
            return True
        else:
            # rsync returns error if no files match, which is okay
            if "No such file" in result.stderr or "failed" in result.stderr.lower():
                log("  No new files on Mac Air")
            return True

    except FileNotFoundError:
        # rsync not available, try scp
        try:
            result = subprocess.run([
                "scp", f"{AIR_HOST}:{AIR_PATH}/*.wav", str(RAW_DIR) + "/"
            ], capture_output=True, text=True)
            return result.returncode == 0
        except:
            log("✗ Could not connect to Mac Air")
            return False


def process_recording(wav_file):
    """Process a single recording"""
    wav_path = Path(wav_file)
    log(f"Processing: {wav_path.name}")

    # Step 1: Convert to 22050Hz mono
    processed_file = PROCESSED_DIR / f"{wav_path.stem}_processed.wav"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    log("  → Converting audio...")
    ffmpeg_path = TOOLS_DIR / "bin" / "ffmpeg"
    if not ffmpeg_path.exists():
        ffmpeg_path = "ffmpeg"

    result = subprocess.run([
        str(ffmpeg_path),
        "-i", str(wav_path),
        "-ar", "22050",
        "-ac", "1",
        "-y",
        str(processed_file)
    ], capture_output=True)

    if result.returncode != 0:
        log(f"  ✗ Conversion failed")
        return False

    log(f"  ✓ Converted: {processed_file.name}")

    # Step 2: Speaker separation
    log("  → Separating speakers...")

    # Activate venv and run separator
    venv_python = TOOLS_DIR / "venv-xtts" / "bin" / "python"
    if not venv_python.exists():
        venv_python = "python3"

    sep_output = TOOLS_DIR / "voices" / "separated" / wav_path.stem

    result = subprocess.run([
        str(venv_python),
        str(SEPARATOR_SCRIPT),
        str(processed_file),
        "-o", str(TOOLS_DIR / "voices" / "separated")
    ], capture_output=True, text=True)

    if result.returncode == 0:
        log(f"  ✓ Speakers separated")
        # Print summary from output
        for line in result.stdout.split('\n'):
            if 'speaker' in line.lower() and ':' in line:
                log(f"    {line.strip()}")
    else:
        log(f"  ⚠ Separation had issues (check manually)")

    # Step 3: Transcribe (optional - can be slow)
    # Uncomment if you want automatic transcription
    # log("  → Transcribing...")
    # transcribe_recording(processed_file)

    return True


def archive_to_nas(wav_file):
    """Archive raw recording to NAS"""
    wav_path = Path(wav_file)
    log(f"Archiving to NAS: {wav_path.name}")

    try:
        # Create directory on NAS
        subprocess.run([
            "ssh", "-p", NAS_PORT, NAS_HOST,
            f"mkdir -p {NAS_PATH}/raw"
        ], capture_output=True)

        # Copy file
        result = subprocess.run([
            "scp", "-P", NAS_PORT,
            str(wav_path),
            f"{NAS_HOST}:{NAS_PATH}/raw/"
        ], capture_output=True)

        if result.returncode == 0:
            log(f"  ✓ Archived to NAS")
            return True
        else:
            log(f"  ✗ Archive failed")
            return False
    except Exception as e:
        log(f"  ✗ Archive error: {e}")
        return False


def get_new_files():
    """Get list of unprocessed WAV files"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_files = set(RAW_DIR.glob("*.wav"))
    new_files = all_files - processed_files

    return sorted(new_files, key=lambda f: f.stat().st_mtime)


def watch_loop(interval=60, pull_air=False, archive=False):
    """Main watch loop"""

    print("\n" + "="*60)
    print("  WATCH & PROCESS - Amma Recording Pipeline")
    print("="*60)
    print(f"\nWatching: {RAW_DIR}")
    print(f"Check interval: {interval} seconds")
    print(f"Pull from Mac Air: {'Yes' if pull_air else 'No'}")
    print(f"Archive to NAS: {'Yes' if archive else 'No'}")
    print("\nPress Ctrl+C to stop\n")
    print("-"*60)

    # Initial scan - mark existing files as already processed
    existing = set(RAW_DIR.glob("*.wav"))
    if existing:
        log(f"Found {len(existing)} existing files (skipping)")
        processed_files.update(existing)

    try:
        while True:
            # Pull from Mac Air if enabled
            if pull_air:
                pull_from_air()

            # Check for new files
            new_files = get_new_files()

            if new_files:
                log(f"Found {len(new_files)} new recording(s)")

                for wav_file in new_files:
                    success = process_recording(wav_file)

                    if success:
                        processed_files.add(wav_file)

                        if archive:
                            archive_to_nas(wav_file)

                    print("-"*60)

            # Wait before next check
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        print(f"Processed {len(processed_files)} files this session")


def main():
    parser = argparse.ArgumentParser(description="Watch and process Amma recordings")
    parser.add_argument("--interval", "-i", type=int, default=60,
                       help="Check interval in seconds (default: 60)")
    parser.add_argument("--pull-from-air", "-p", action="store_true",
                       help="Pull new recordings from Mac Air")
    parser.add_argument("--archive", "-a", action="store_true",
                       help="Archive processed files to NAS")
    parser.add_argument("--once", action="store_true",
                       help="Run once and exit (don't loop)")
    args = parser.parse_args()

    if args.once:
        # One-time processing
        if args.pull_from_air:
            pull_from_air()

        new_files = list(RAW_DIR.glob("*.wav"))
        for wav_file in new_files:
            process_recording(wav_file)
            if args.archive:
                archive_to_nas(wav_file)
    else:
        # Continuous watching
        watch_loop(
            interval=args.interval,
            pull_air=args.pull_from_air,
            archive=args.archive
        )


if __name__ == "__main__":
    main()
