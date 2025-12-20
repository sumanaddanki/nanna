#!/usr/bin/env python3
"""
Process WhatsApp Call Recordings
Converts audio and transcribes using Whisper.

Usage:
    python process_recording.py <audio_file>
    python process_recording.py voice/raw/whatsapp_call_20241217_143000.wav

Output:
    - Converted WAV in voice/processed/
    - Transcript in voice/transcripts/
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "voice" / "raw"
PROCESSED_DIR = SCRIPT_DIR / "voice" / "processed"
TRANSCRIPT_DIR = SCRIPT_DIR / "voice" / "transcripts"

# FFmpeg path - check tools/bin first
TOOLS_BIN = SCRIPT_DIR.parent / "tools" / "bin"
if (TOOLS_BIN / "ffmpeg").exists():
    FFMPEG = str(TOOLS_BIN / "ffmpeg")
else:
    FFMPEG = "ffmpeg"


def convert_audio(input_file):
    """Convert audio to 22050Hz mono WAV"""
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return None

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / f"{input_path.stem}_processed.wav"

    print(f"Converting: {input_path.name}")
    print(f"  → {output_file.name}")

    try:
        subprocess.run([
            FFMPEG,
            "-i", str(input_path),
            "-ar", "22050",  # 22.05kHz sample rate
            "-ac", "1",      # Mono
            "-y",            # Overwrite
            str(output_file)
        ], check=True, capture_output=True)

        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e}")
        return None


def transcribe_audio(audio_file, model_size="base"):
    """Transcribe audio using Whisper"""
    audio_path = Path(audio_file)

    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        return None

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"

    print(f"\nTranscribing: {audio_path.name}")
    print(f"  Model: {model_size}")

    try:
        import whisper

        model = whisper.load_model(model_size)
        result = model.transcribe(str(audio_path), language="te")  # Telugu

        # Save transcript
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Transcript: {audio_path.name}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Model: whisper-{model_size}\n\n")
            f.write(result["text"])

        print(f"  → {output_file.name}")
        print(f"\nTranscript preview:")
        print("-" * 40)
        print(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])
        print("-" * 40)

        return output_file

    except ImportError:
        print("Whisper not installed. Install with:")
        print("  pip install openai-whisper")
        return None
    except Exception as e:
        print(f"Error transcribing: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        # List available recordings
        print("\nUsage: python process_recording.py <audio_file>")
        print("\nAvailable recordings in voice/raw/:")

        if RAW_DIR.exists():
            recordings = list(RAW_DIR.glob("*.wav"))
            if recordings:
                for r in sorted(recordings):
                    size_mb = r.stat().st_size / (1024 * 1024)
                    print(f"  - {r.name} ({size_mb:.1f} MB)")
            else:
                print("  (no recordings yet)")
        else:
            print("  (directory doesn't exist)")
        return

    input_file = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"

    print("\n" + "="*60)
    print("  PROCESS RECORDING")
    print("="*60)

    # Convert audio
    processed_file = convert_audio(input_file)
    if not processed_file:
        return

    # Transcribe
    transcript_file = transcribe_audio(processed_file, model_size)

    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print(f"\nProcessed audio: {processed_file}")
    if transcript_file:
        print(f"Transcript: {transcript_file}")

    print("\nNext step - separate speakers:")
    print(f"  python ../tools/separate_speakers.py {processed_file}")


if __name__ == "__main__":
    main()
