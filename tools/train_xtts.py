#!/usr/bin/env python3
"""
XTTS Voice Cloning Script for Nanna Voice Training
Creates voice profiles using XTTS v2 speaker embeddings on Mac Studio M2 Ultra

This uses the voice cloning approach (speaker embedding extraction) which is:
1. Fast - extracts embeddings in minutes
2. High quality - XTTS v2 is already multilingual
3. No GPU training required - just embedding extraction
"""

import os
import sys
import torch
from pathlib import Path
from datetime import datetime

# Set environment
os.environ['COQUI_TOS_AGREED'] = '1'

# Fix PyTorch 2.6+ weights_only issue with TTS library
# The TTS library's model files use pickle which PyTorch 2.6 blocks by default
import torch.serialization
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

def extract_reference_clip(input_wav, output_wav, duration=25, start_offset=60):
    """Extract a short reference clip from a large audio file.

    XTTS works best with 15-30 second reference clips that are:
    - Clear speech with minimal background noise
    - Representative of the speaker's voice
    """
    import subprocess

    # Try sox with full path (macOS homebrew)
    sox_paths = ["/opt/homebrew/bin/sox", "/usr/local/bin/sox", "sox"]

    for sox_path in sox_paths:
        try:
            cmd = [
                sox_path, str(input_wav), str(output_wav),
                "trim", str(start_offset), str(duration),  # Start at offset, take duration seconds
                "norm"  # Normalize audio
            ]
            result = subprocess.run(cmd, check=True, capture_output=True)
            print(f"  Extracted {duration}s clip using sox")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    # Fallback to ffmpeg
    ffmpeg_paths = ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "ffmpeg"]
    for ffmpeg_path in ffmpeg_paths:
        try:
            cmd = [
                ffmpeg_path, "-y", "-i", str(input_wav),
                "-ss", str(start_offset), "-t", str(duration),
                "-af", "loudnorm", str(output_wav)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"  Extracted {duration}s clip using ffmpeg")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    print("  Could not extract clip - sox and ffmpeg not found")
    return False


def train_voice(voice_name, sample_duration=25):
    """Create voice profile using XTTS speaker embeddings"""
    from TTS.api import TTS

    base_dir = Path(__file__).parent
    voice_dir = base_dir / "voices" / "processed" / voice_name
    output_dir = base_dir / "voices" / "models" / voice_name

    if not voice_dir.exists():
        print(f"Error: Voice directory not found: {voice_dir}")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all WAV files
    wav_files = list(voice_dir.glob("*.wav"))
    if not wav_files:
        print(f"Error: No WAV files found in {voice_dir}")
        return False

    # Calculate total audio duration
    total_size_mb = sum(f.stat().st_size for f in wav_files) / (1024*1024)

    print(f"\n{'='*60}")
    print(f"  XTTS Voice Profile Creation: {voice_name}")
    print(f"{'='*60}")
    print(f"\nWAV files found: {len(wav_files)}")
    for f in wav_files:
        size_mb = f.stat().st_size / (1024*1024)
        print(f"  - {f.name}: {size_mb:.1f} MB")
    print(f"\nTotal audio: {total_size_mb:.1f} MB")
    print(f"Output directory: {output_dir}")

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
        print(f"\nUsing Apple Metal (MPS) acceleration!")
    elif torch.cuda.is_available():
        device = "cuda"
        print(f"\nUsing NVIDIA CUDA acceleration!")
    else:
        device = "cpu"
        print(f"\nUsing CPU")

    # Extract a short reference clip (XTTS needs 15-30 sec, not hours!)
    wav_files_sorted = sorted(wav_files, key=lambda f: f.stat().st_size, reverse=True)
    source_wav = wav_files_sorted[0]
    reference_wav = output_dir / "reference.wav"

    print(f"\nExtracting {sample_duration}s reference clip from: {source_wav.name}")
    if not extract_reference_clip(source_wav, reference_wav, duration=sample_duration):
        print("Failed to extract clip, using original (may be slow)")
        reference_wav = source_wav

    # Initialize TTS with XTTS v2
    print(f"\nLoading XTTS v2 model...")
    start_time = datetime.now()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    load_time = (datetime.now() - start_time).total_seconds()
    print(f"Model loaded in {load_time:.1f}s")

    print(f"\nReference audio: {reference_wav}")
    print(f"Creating voice profile...")

    # Test the voice by generating a sample
    test_texts = [
        "Chinna, nenu neeku proud ga feel avthunna.",
        "Hello, this is a voice cloning test.",
        "Baaga cheppav ra, very good progress."
    ]

    output_samples = output_dir / "samples"
    output_samples.mkdir(exist_ok=True)

    print(f"\nGenerating test samples...")
    for i, text in enumerate(test_texts):
        output_file = output_samples / f"sample_{i+1}.wav"
        print(f"  [{i+1}/{len(test_texts)}] Generating: {text[:40]}...")

        tts.tts_to_file(
            text=text,
            file_path=str(output_file),
            speaker_wav=str(reference_wav),
            language="en"
        )
        print(f"       Saved: {output_file.name}")

    # Save reference info for later use
    reference_info = output_dir / "voice_profile.txt"
    with open(reference_info, 'w') as f:
        f.write(f"Voice: {voice_name}\n")
        f.write(f"Created: {datetime.now().isoformat()}\n")
        f.write(f"Reference audio: {reference_wav}\n")
        f.write(f"Reference duration: {sample_duration}s\n")
        f.write(f"Total source audio: {total_size_mb:.1f} MB\n")
        f.write(f"Source files:\n")
        for wav in wav_files:
            f.write(f"  - {wav.name}\n")

    total_time = (datetime.now() - start_time).total_seconds()

    print(f"\n{'='*60}")
    print(f"  Voice profile created successfully!")
    print(f"{'='*60}")
    print(f"\nOutput files:")
    print(f"  - {output_dir}/reference.wav (for voice cloning)")
    print(f"  - {output_dir}/voice_profile.txt (metadata)")
    print(f"  - {output_dir}/samples/ (test samples)")
    print(f"\nTotal time: {total_time:.1f}s")
    print(f"\nTo use this voice:")
    print(f"  python train_xtts.py test {voice_name} \"Your text here\"")

    return True

def test_voice(voice_name, text, language="en"):
    """Test a trained voice"""
    from TTS.api import TTS

    base_dir = Path(__file__).parent
    model_dir = base_dir / "voices" / "models" / voice_name

    # Use the saved reference audio
    reference_wav = model_dir / "reference.wav"
    if not reference_wav.exists():
        # Fallback to processed audio
        voice_dir = base_dir / "voices" / "processed" / voice_name
        wav_files = list(voice_dir.glob("*.wav"))
        if not wav_files:
            print(f"No audio files found for {voice_name}")
            return
        reference_wav = wav_files[0]

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Loading XTTS v2 model on {device}...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    output_file = base_dir / "voices" / "test_output" / f"{voice_name}_test_{datetime.now().strftime('%H%M%S')}.wav"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating speech with {voice_name}'s voice...")
    print(f"Text: {text}")
    print(f"Language: {language}")

    tts.tts_to_file(
        text=text,
        file_path=str(output_file),
        speaker_wav=str(reference_wav),
        language=language
    )
    print(f"\nOutput saved to: {output_file}")
    print(f"\nPlay with: open \"{output_file}\"")

def train_all_voices():
    """Train all 6 voices sequentially"""
    voices = ["arjun", "ananya", "kiran", "lakshmi", "priya", "ravi"]
    results = {}

    print(f"\n{'='*60}")
    print(f"  TRAINING ALL 6 VOICES")
    print(f"{'='*60}")

    for i, voice in enumerate(voices):
        print(f"\n[{i+1}/{len(voices)}] Training {voice}...")
        success = train_voice(voice)
        results[voice] = "SUCCESS" if success else "FAILED"

    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE - SUMMARY")
    print(f"{'='*60}")
    for voice, status in results.items():
        emoji = "✓" if status == "SUCCESS" else "✗"
        print(f"  {emoji} {voice}: {status}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python train_xtts.py train <voice_name>   - Train single voice")
        print("  python train_xtts.py train-all            - Train all 6 voices")
        print("  python train_xtts.py test <voice_name> <text> [language]")
        print("\nVoices available: arjun, ananya, priya, kiran, ravi, lakshmi")
        print("\nExamples:")
        print("  python train_xtts.py train arjun")
        print("  python train_xtts.py train-all")
        print("  python train_xtts.py test arjun 'Hello Chinna!'")
        print("  python train_xtts.py test arjun 'Baaga cheppav ra' te")
        sys.exit(1)

    command = sys.argv[1]

    if command == "train":
        voice_name = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        train_voice(voice_name)

    elif command == "train-all":
        train_all_voices()

    elif command == "test":
        voice_name = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        text = sys.argv[3] if len(sys.argv) > 3 else "Hello Chinna, this is a test."
        language = sys.argv[4] if len(sys.argv) > 4 else "en"
        test_voice(voice_name, text, language)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
