#!/usr/bin/env python3
"""
Auto-Record WhatsApp Calls
Automatically detects when a WhatsApp call is active and starts recording.

Usage:
    python auto_record_calls.py
    python auto_record_calls.py --person amma

Naming Convention:
    {person}_whatsapp_{YYYYMMDD}_{HHMM}_{minutes}min.wav
    Examples:
        amma_whatsapp_20241217_1423_15min.wav
        chinna_whatsapp_20241217_2230_8min.wav

Requirements:
    - BlackHole 2ch installed (virtual audio device)
    - Multi-Output Device configured (Speakers + BlackHole)
    - Aggregate Device configured (Mic + BlackHole)
    - System audio output set to Multi-Output Device

How it works:
    1. Monitors WhatsApp CPU usage (call = ~15-30% vs chat = ~2-5%)
    2. Detects audio activity
    3. When both conditions met → starts recording
    4. After 15s of silence → stops and saves recording
"""

import subprocess
import time
import os
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
WHATSAPP_CPU_THRESHOLD = 10.0  # CPU% above this = likely call
SILENCE_TIMEOUT = 15  # Seconds of silence before stopping
CHECK_INTERVAL = 10  # Seconds between checks (saves CPU)
OUTPUT_DIR = Path(__file__).parent / "voice" / "raw"
DEFAULT_PERSON = "amma"  # Default person name for recordings

# Recording state
is_recording = False
recording_process = None
current_recording_file = None
temp_recording_file = None  # Temporary name until we know duration
recording_start_time = None
silence_counter = 0
person_name = DEFAULT_PERSON


def get_whatsapp_cpu():
    """Get WhatsApp CPU usage percentage"""
    try:
        result = subprocess.run(
            ["ps", "-A", "-o", "%cpu,comm"],
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if 'WhatsApp' in line:
                try:
                    cpu = float(line.strip().split()[0])
                    return cpu
                except (ValueError, IndexError):
                    pass
        return 0.0
    except Exception as e:
        print(f"Error checking WhatsApp CPU: {e}")
        return 0.0


def is_audio_active():
    """Check if there's audio activity (simple check)"""
    # On Mac, we check if any audio is flowing through the system
    # This is a simplified check - in production, you'd use pyaudio to check levels
    try:
        # Check if WhatsApp is using significant CPU (proxy for audio activity)
        cpu = get_whatsapp_cpu()
        return cpu > 5.0  # Any significant activity
    except:
        return False


def start_recording():
    """Start recording audio"""
    global is_recording, recording_process, temp_recording_file, recording_start_time

    if is_recording:
        return

    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Record start time for duration calculation
    recording_start_time = datetime.now()

    # Use temporary filename - will rename when we know duration
    temp_recording_file = OUTPUT_DIR / f"_recording_in_progress.wav"

    print(f"\n{'='*60}")
    print(f"🎙️  RECORDING STARTED")
    print(f"   Person: {person_name}")
    print(f"   Time: {recording_start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    # Use sox to record from Aggregate Device
    # The Aggregate Device should combine mic + BlackHole (system audio)
    # Try multiple paths for sox (homebrew installs to /opt/homebrew/bin on Apple Silicon)
    sox_paths = ["/opt/homebrew/bin/sox", "/usr/local/bin/sox", "sox"]
    sox_found = False

    for sox_path in sox_paths:
        try:
            recording_process = subprocess.Popen([
                sox_path,
                "-d",  # Default input device (set to Aggregate Device in System Settings)
                "-c", "2",  # Stereo
                "-r", "22050",  # Sample rate
                str(temp_recording_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            is_recording = True
            sox_found = True
            print(f"   Using: {sox_path}")
            break
        except FileNotFoundError:
            continue

    if not sox_found:
        print("ERROR: sox not found. Trying ffmpeg...")
        # Try ffmpeg as fallback
        ffmpeg_paths = ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "ffmpeg"]
        for ffmpeg_path in ffmpeg_paths:
            try:
                recording_process = subprocess.Popen([
                    ffmpeg_path,
                    "-f", "avfoundation",
                    "-i", ":0",  # Default audio input
                    "-ar", "22050",
                    "-ac", "2",
                    "-y",
                    str(temp_recording_file)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                is_recording = True
                print(f"   Using: {ffmpeg_path}")
                break
            except FileNotFoundError:
                continue
        else:
            print("ERROR: Neither sox nor ffmpeg found!")


def stop_recording():
    """Stop recording and save file with proper naming convention"""
    global is_recording, recording_process, temp_recording_file, recording_start_time

    if not is_recording:
        return

    if recording_process:
        recording_process.terminate()
        recording_process.wait()
        recording_process = None

    is_recording = False

    if temp_recording_file and temp_recording_file.exists():
        # Calculate duration in minutes (rounded)
        end_time = datetime.now()
        duration_seconds = (end_time - recording_start_time).total_seconds()
        duration_minutes = round(duration_seconds / 60)
        if duration_minutes < 1:
            duration_minutes = 1  # Minimum 1 minute

        # Create final filename: {person}_whatsapp_{YYYYMMDD}_{HHMM}_{minutes}min.wav
        date_str = recording_start_time.strftime("%Y%m%d")
        time_str = recording_start_time.strftime("%H%M")
        final_filename = f"{person_name}_whatsapp_{date_str}_{time_str}_{duration_minutes}min.wav"
        final_file = OUTPUT_DIR / final_filename

        # Rename temp file to final name
        temp_recording_file.rename(final_file)

        size_mb = final_file.stat().st_size / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"💾 RECORDING SAVED: {final_filename}")
        print(f"   Duration: {duration_minutes} min ({duration_seconds:.0f}s)")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"{'='*60}")
        print(f"\nNext: Run speaker separation to isolate Amma's voice:")
        print(f"  python ../tools/separate_speakers.py {final_file}")

    temp_recording_file = None
    recording_start_time = None


def monitor_calls():
    """Main monitoring loop"""
    global silence_counter

    print("\n" + "="*60)
    print("  WHATSAPP CALL AUTO-RECORDER")
    print("="*60)
    print("\nMonitoring for WhatsApp calls...")
    print(f"  - CPU threshold: {WHATSAPP_CPU_THRESHOLD}%")
    print(f"  - Silence timeout: {SILENCE_TIMEOUT}s")
    print(f"  - Output directory: {OUTPUT_DIR}")
    print("\nMake sure:")
    print("  1. System audio output = Multi-Output Device")
    print("  2. System audio input = Aggregate Device")
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            cpu = get_whatsapp_cpu()
            call_active = cpu > WHATSAPP_CPU_THRESHOLD

            if call_active:
                if not is_recording:
                    print(f"📞 Call detected! (WhatsApp CPU: {cpu:.1f}%)")
                    start_recording()
                silence_counter = 0
            else:
                if is_recording:
                    silence_counter += CHECK_INTERVAL
                    if silence_counter >= SILENCE_TIMEOUT:
                        print(f"🔇 Silence detected ({SILENCE_TIMEOUT}s), stopping...")
                        stop_recording()
                        silence_counter = 0
                    else:
                        remaining = SILENCE_TIMEOUT - silence_counter
                        print(f"   Silence: {silence_counter}s (stopping in {remaining}s if continues)")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        if is_recording:
            stop_recording()
        print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-record WhatsApp calls")
    parser.add_argument("--person", "-p", default=DEFAULT_PERSON,
                       help=f"Person name for recording (default: {DEFAULT_PERSON})")
    args = parser.parse_args()

    person_name = args.person
    monitor_calls()
