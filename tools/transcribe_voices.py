#!/usr/bin/env python3
"""
Transcribe all voice audio files using Whisper
Creates transcripts needed for XTTS fine-tuning
"""

import whisper
import os
import sys
import json
from pathlib import Path
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def transcribe_voice(voice_name, model_size="small"):
    """Transcribe all WAV files for a voice"""

    base_dir = Path(__file__).parent
    voice_dir = base_dir / "voices" / "processed" / voice_name
    output_dir = base_dir / "voices" / "transcripts" / voice_name

    if not voice_dir.exists():
        print(f"Error: Voice directory not found: {voice_dir}")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all WAV files
    wav_files = sorted(voice_dir.glob("*.wav"))

    print(f"\n{'='*60}")
    print(f"Transcribing voice: {voice_name}")
    print(f"WAV files: {len(wav_files)}")
    print(f"Model: whisper-{model_size}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")

    # Load Whisper model
    print(f"Loading Whisper {model_size} model...")
    model = whisper.load_model(model_size)
    print("Model loaded!\n")

    all_transcripts = []

    for i, wav_file in enumerate(wav_files, 1):
        file_size = wav_file.stat().st_size / (1024*1024)
        print(f"[{i}/{len(wav_files)}] {wav_file.name} ({file_size:.1f} MB)")

        # Transcribe with English forced (audio is English with Telugu accent)
        result = model.transcribe(str(wav_file), language="en", verbose=False)

        # Save individual transcript
        transcript_file = output_dir / f"{wav_file.stem}.txt"
        with open(transcript_file, 'w') as f:
            f.write(result['text'])

        # Save segments with timestamps (needed for XTTS training)
        segments_file = output_dir / f"{wav_file.stem}_segments.json"
        with open(segments_file, 'w') as f:
            json.dump(result['segments'], f, indent=2)

        all_transcripts.append({
            'audio_file': wav_file.name,
            'transcript': result['text'],
            'segments': len(result['segments']),
            'duration': result['segments'][-1]['end'] if result['segments'] else 0
        })

        print(f"   Duration: {all_transcripts[-1]['duration']:.1f}s, Segments: {all_transcripts[-1]['segments']}")
        print(f"   Preview: {result['text'][:100]}...")
        print()

    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'voice': voice_name,
            'total_files': len(wav_files),
            'total_duration': sum(t['duration'] for t in all_transcripts),
            'transcripts': all_transcripts
        }, f, indent=2)

    total_duration = sum(t['duration'] for t in all_transcripts)
    print(f"\n{'='*60}")
    print(f"Completed: {voice_name}")
    print(f"Total duration: {total_duration/60:.1f} minutes")
    print(f"Transcripts saved to: {output_dir}")
    print(f"{'='*60}\n")

    return True

def transcribe_all_voices(model_size="small"):
    """Transcribe all 6 voices"""
    voices = ["arjun", "ananya", "priya", "kiran", "ravi", "lakshmi"]

    for voice in voices:
        print(f"\n{'#'*60}")
        print(f"# Processing: {voice}")
        print(f"{'#'*60}")
        transcribe_voice(voice, model_size)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        voice_name = sys.argv[1]
        model_size = sys.argv[2] if len(sys.argv) > 2 else "small"

        if voice_name == "all":
            transcribe_all_voices(model_size)
        else:
            transcribe_voice(voice_name, model_size)
    else:
        print("Usage:")
        print("  python transcribe_voices.py <voice_name> [model_size]")
        print("  python transcribe_voices.py all [model_size]")
        print("\nVoices: arjun, ananya, priya, kiran, ravi, lakshmi")
        print("Models: tiny, base, small, medium, large")
        print("\nExample:")
        print("  python transcribe_voices.py arjun small")
        print("  python transcribe_voices.py all medium")
