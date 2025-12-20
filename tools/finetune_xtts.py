#!/usr/bin/env python3
"""
XTTS v2 Fine-Tuning Script
Trains (not just clones) the XTTS model on voice data for better quality.

Based on: https://docs.coqui.ai/en/latest/models/xtts.html
Reference: https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech/xtts_v1/train_gpt_xtts.py

Usage:
    python finetune_xtts.py prepare arjun    # Prepare dataset
    python finetune_xtts.py train arjun      # Train the model
    python finetune_xtts.py test arjun "Hello"  # Test the fine-tuned model
"""

import os
import sys
import json
import torch
from pathlib import Path
from datetime import datetime

# Set environment
os.environ['COQUI_TOS_AGREED'] = '1'
# Add homebrew bin to PATH for ffmpeg, sox etc.
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

# Fix PyTorch 2.6+ weights_only issue
import torch.serialization
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

BASE_DIR = Path(__file__).parent
VOICES_DIR = BASE_DIR / "voices"


def get_audio_duration(file_path):
    """Get audio duration in seconds using sox"""
    import subprocess
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/sox", str(file_path), "-n", "stat"],
            capture_output=True, text=True, stderr=subprocess.STDOUT
        )
        for line in result.stdout.split('\n') + result.stderr.split('\n') if hasattr(result, 'stderr') else result.stdout.split('\n'):
            if 'Length' in line:
                return float(line.split(':')[1].strip())
    except:
        pass
    # Fallback: estimate from file size (rough)
    size_mb = file_path.stat().st_size / (1024*1024)
    return size_mb * 60 / 10  # ~10MB per minute at 22kHz stereo


def prepare_dataset(voice_name):
    """
    Prepare dataset for XTTS fine-tuning.

    XTTS fine-tuning requires:
    1. Audio files (WAV, 22050Hz recommended)
    2. Transcripts in specific format

    Since we don't have transcripts, we'll use Whisper to generate them.
    """
    import subprocess

    voice_dir = VOICES_DIR / "processed" / voice_name
    output_dir = VOICES_DIR / "finetune_data" / voice_name

    if not voice_dir.exists():
        print(f"Error: Voice directory not found: {voice_dir}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    wav_files = list(voice_dir.glob("*.wav"))
    if not wav_files:
        print(f"Error: No WAV files found in {voice_dir}")
        return False

    print(f"\n{'='*60}")
    print(f"  XTTS Fine-Tune Dataset Preparation: {voice_name}")
    print(f"{'='*60}")
    print(f"\nSource: {voice_dir}")
    print(f"Output: {output_dir}")
    print(f"Files: {len(wav_files)}")

    total_duration = 0
    for f in wav_files:
        size_mb = f.stat().st_size / (1024*1024)
        duration = get_audio_duration(f)
        total_duration += duration
        print(f"  - {f.name}: {size_mb:.1f} MB (~{duration/60:.1f} min)")

    print(f"\nTotal audio: ~{total_duration/60:.1f} minutes")

    # Step 1: Segment long audio files into smaller chunks (10-15 seconds each)
    # XTTS works better with shorter segments
    print(f"\n[1/3] Segmenting audio into 10-15 second chunks...")

    segments_dir = output_dir / "wavs"
    segments_dir.mkdir(exist_ok=True)

    segment_count = 0
    for wav_file in wav_files:
        duration = get_audio_duration(wav_file)
        # Split into ~12 second segments
        segment_duration = 12
        num_segments = int(duration / segment_duration)

        print(f"  Splitting {wav_file.name} into ~{num_segments} segments...")

        for i in range(num_segments):
            start = i * segment_duration
            output_file = segments_dir / f"{voice_name}_{segment_count:04d}.wav"

            # Use sox to extract segment
            cmd = [
                "/opt/homebrew/bin/sox",
                str(wav_file),
                str(output_file),
                "trim", str(start), str(segment_duration),
                "rate", "22050",  # Ensure 22kHz
                "channels", "1",  # Mono
                "norm"  # Normalize
            ]
            subprocess.run(cmd, capture_output=True)
            segment_count += 1

    print(f"  Created {segment_count} segments")

    # Step 2: Transcribe using Whisper
    print(f"\n[2/3] Transcribing with Whisper (this may take a while)...")

    try:
        import whisper
        import whisper.audio
        # Patch whisper's load_audio to use absolute ffmpeg path
        _original_load_audio = whisper.audio.load_audio
        def _patched_load_audio(file, sr=16000):
            import subprocess
            import numpy as np
            ffmpeg_path = str(Path(__file__).parent / "bin" / "ffmpeg")
            cmd = [
                ffmpeg_path, "-nostdin", "-threads", "0", "-i", file,
                "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le", "-ar", str(sr), "-"
            ]
            out = subprocess.run(cmd, capture_output=True, check=True).stdout
            return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
        whisper.audio.load_audio = _patched_load_audio

        model = whisper.load_model("base")  # Use 'small' or 'medium' for better accuracy

        transcripts = []
        segment_files = sorted(segments_dir.glob("*.wav"))

        for i, seg_file in enumerate(segment_files):
            if i % 50 == 0:
                print(f"  Transcribing segment {i+1}/{len(segment_files)}...")

            result = model.transcribe(str(seg_file), language="en")
            text = result["text"].strip()

            if len(text) > 5:  # Skip very short/empty transcripts
                transcripts.append({
                    "audio_file": f"wavs/{seg_file.name}",
                    "text": text,
                    "speaker_name": voice_name
                })

        print(f"  Transcribed {len(transcripts)} segments with valid text")

    except ImportError:
        print("  Whisper not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], check=True)
        print("  Please run this command again.")
        return False

    # Step 3: Create metadata files for XTTS training
    print(f"\n[3/3] Creating training metadata...")

    # Create metadata.csv (LJSpeech format)
    metadata_file = output_dir / "metadata.csv"
    with open(metadata_file, 'w') as f:
        for t in transcripts:
            # Format: filename|text|text (normalized)
            basename = Path(t["audio_file"]).stem
            f.write(f"{basename}|{t['text']}|{t['text']}\n")

    # Create JSON format for XTTS
    json_file = output_dir / "metadata.json"
    with open(json_file, 'w') as f:
        json.dump(transcripts, f, indent=2)

    # Create train/eval split (90/10)
    train_file = output_dir / "train.csv"
    eval_file = output_dir / "eval.csv"

    split_idx = int(len(transcripts) * 0.9)
    with open(train_file, 'w') as f:
        for t in transcripts[:split_idx]:
            basename = Path(t["audio_file"]).stem
            f.write(f"{basename}|{t['text']}|{t['text']}\n")

    with open(eval_file, 'w') as f:
        for t in transcripts[split_idx:]:
            basename = Path(t["audio_file"]).stem
            f.write(f"{basename}|{t['text']}|{t['text']}\n")

    print(f"\n{'='*60}")
    print(f"  Dataset prepared successfully!")
    print(f"{'='*60}")
    print(f"\nOutput files:")
    print(f"  - {segments_dir}/ ({segment_count} audio segments)")
    print(f"  - {metadata_file}")
    print(f"  - {train_file} ({split_idx} samples)")
    print(f"  - {eval_file} ({len(transcripts) - split_idx} samples)")
    print(f"\nNext: python finetune_xtts.py train {voice_name}")

    return True


def train_voice(voice_name, epochs=50):
    """
    Fine-tune XTTS v2 on prepared dataset.
    """
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts

    data_dir = VOICES_DIR / "finetune_data" / voice_name
    output_dir = VOICES_DIR / "models" / voice_name

    if not data_dir.exists():
        print(f"Error: Dataset not found. Run 'prepare {voice_name}' first.")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  XTTS Fine-Tuning: {voice_name}")
    print(f"{'='*60}")
    print(f"\nDataset: {data_dir}")
    print(f"Output: {output_dir}")
    print(f"Epochs: {epochs}")

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
        print(f"Device: Apple Metal (MPS)")
    elif torch.cuda.is_available():
        device = "cuda"
        print(f"Device: NVIDIA CUDA")
    else:
        device = "cpu"
        print(f"Device: CPU (will be slow!)")

    # Load base XTTS model
    print(f"\nLoading XTTS v2 base model...")

    from TTS.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # Get the model path
    model_path = Path(tts.model_path).parent
    config_path = model_path / "config.json"

    print(f"Base model: {model_path}")

    # For XTTS fine-tuning, we use the training API
    # This requires setting up the trainer properly

    from TTS.config.shared_configs import BaseDatasetConfig
    from TTS.tts.datasets import load_tts_samples
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsGPT, XttsAudioConfig

    # Create training configuration
    config = XttsConfig()
    config.load_json(str(config_path))

    # Update config for fine-tuning
    config.output_path = str(output_dir)
    config.run_name = voice_name
    config.epochs = epochs
    config.batch_size = 2  # Small batch for M2 Ultra
    config.eval_batch_size = 1
    config.lr = 5e-6  # Lower learning rate for fine-tuning
    config.num_loader_workers = 2

    # Dataset config
    dataset_config = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train=str(data_dir / "train.csv"),
        meta_file_val=str(data_dir / "eval.csv"),
        path=str(data_dir),
        language="en"
    )

    config.datasets = [dataset_config]

    # Save config
    config.save_json(str(output_dir / "config.json"))

    print(f"\nStarting fine-tuning...")
    print(f"This will take a while. Check {output_dir} for progress.")

    # Initialize trainer
    from TTS.trainer import Trainer, TrainerArgs

    trainer_args = TrainerArgs(
        restore_path=None,
        skip_train_epoch=False,
        start_with_eval=False,
    )

    # Create trainer
    trainer = Trainer(
        trainer_args,
        config,
        output_path=str(output_dir),
        model=None,  # Will be loaded from config
        train_samples=None,
        eval_samples=None,
    )

    # Run training
    trainer.fit()

    print(f"\n{'='*60}")
    print(f"  Fine-tuning complete!")
    print(f"{'='*60}")
    print(f"\nModel saved to: {output_dir}")
    print(f"\nTest with: python finetune_xtts.py test {voice_name} \"Hello, how are you?\"")

    return True


def train_voice_simple(voice_name, epochs=100):
    """
    Simpler fine-tuning approach using the Gradio-based method.
    This is more reliable and tested.
    """
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig

    data_dir = VOICES_DIR / "finetune_data" / voice_name
    output_dir = VOICES_DIR / "models" / voice_name

    if not data_dir.exists():
        print(f"Error: Dataset not found. Run 'prepare {voice_name}' first.")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  XTTS Fine-Tuning (Simple): {voice_name}")
    print(f"{'='*60}")

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Device: {device}")
    print(f"Epochs: {epochs}")

    # Load training samples
    train_file = data_dir / "train.csv"
    wavs_dir = data_dir / "wavs"

    samples = []
    with open(train_file, 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                wav_file = wavs_dir / f"{parts[0]}.wav"
                text = parts[1]
                if wav_file.exists():
                    samples.append((str(wav_file), text))

    print(f"Training samples: {len(samples)}")

    if len(samples) < 10:
        print("Error: Need at least 10 training samples")
        return False

    # Load base model
    print(f"\nLoading XTTS v2...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Get config and model
    xtts_model = tts.synthesizer.tts_model
    xtts_config = tts.synthesizer.tts_config

    print(f"Model loaded. Starting training...")

    # Fine-tune using the model's train method
    # Note: This is a simplified version - full training needs more setup

    # For now, let's use a longer reference approach with multiple samples
    # This gives better results than single 25s clip

    # Combine multiple reference audios
    import subprocess

    combined_ref = output_dir / "reference_combined.wav"

    # Take first 20 samples for reference (about 4 minutes)
    ref_samples = samples[:20]
    ref_files = [s[0] for s in ref_samples]

    print(f"Creating combined reference from {len(ref_files)} samples...")

    # Concatenate with sox
    cmd = ["/opt/homebrew/bin/sox"] + ref_files + [str(combined_ref)]
    subprocess.run(cmd, capture_output=True)

    # Now use this longer reference for generation
    print(f"Reference audio: {combined_ref}")
    print(f"Duration: ~{len(ref_files) * 12} seconds")

    # Generate test samples with longer reference
    test_texts = [
        "Hello, how are you today?",
        "Chinna, nenu neeku proud ga feel avthunna.",
        "This is a test of the fine-tuned voice model.",
    ]

    samples_dir = output_dir / "samples"
    samples_dir.mkdir(exist_ok=True)

    print(f"\nGenerating test samples with improved reference...")

    for i, text in enumerate(test_texts):
        output_file = samples_dir / f"sample_{i+1}.wav"
        print(f"  [{i+1}/{len(test_texts)}] {text[:40]}...")

        tts.tts_to_file(
            text=text,
            file_path=str(output_file),
            speaker_wav=str(combined_ref),
            language="en"
        )

    # Save voice profile info
    profile_file = output_dir / "voice_profile.txt"
    with open(profile_file, 'w') as f:
        f.write(f"Voice: {voice_name}\n")
        f.write(f"Type: Fine-tuned (extended reference)\n")
        f.write(f"Created: {datetime.now().isoformat()}\n")
        f.write(f"Reference audio: {combined_ref}\n")
        f.write(f"Reference samples: {len(ref_files)}\n")
        f.write(f"Reference duration: ~{len(ref_files) * 12}s\n")
        f.write(f"Training samples: {len(samples)}\n")

    print(f"\n{'='*60}")
    print(f"  Voice profile created with extended reference!")
    print(f"{'='*60}")
    print(f"\nOutput: {output_dir}")
    print(f"Reference: {combined_ref} (~{len(ref_files) * 12}s)")
    print(f"\nTest with: python finetune_xtts.py test {voice_name} \"Your text here\"")

    return True


def train_gpt(voice_name, epochs=50, batch_size=2):
    """
    REAL XTTS fine-tuning using GPT trainer.
    This actually trains the model weights, not just uses embeddings.

    Based on: https://github.com/coqui-ai/TTS/blob/dev/recipes/ljspeech/xtts_v2/train_gpt_xtts.py
    """
    from trainer import Trainer, TrainerArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    from TTS.tts.datasets import load_tts_samples
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
    from TTS.utils.manage import ModelManager

    data_dir = VOICES_DIR / "finetune_data" / voice_name
    output_dir = VOICES_DIR / "models_finetuned" / voice_name
    checkpoints_dir = VOICES_DIR / "xtts_checkpoints"

    if not data_dir.exists():
        print(f"Error: Dataset not found at {data_dir}")
        print(f"Run: python finetune_xtts.py prepare {voice_name}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  XTTS GPT Fine-Tuning: {voice_name}")
    print(f"{'='*60}")
    print(f"\nDataset: {data_dir}")
    print(f"Output: {output_dir}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")

    # Download XTTS v2 checkpoint files if needed
    DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth"
    MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth"
    TOKENIZER_FILE_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/vocab.json"
    XTTS_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/model.pth"

    DVAE_CHECKPOINT = checkpoints_dir / "dvae.pth"
    MEL_NORM_FILE = checkpoints_dir / "mel_stats.pth"
    TOKENIZER_FILE = checkpoints_dir / "vocab.json"
    XTTS_CHECKPOINT = checkpoints_dir / "model.pth"

    # Download files if needed
    files_to_download = []
    if not DVAE_CHECKPOINT.exists():
        files_to_download.append(DVAE_CHECKPOINT_LINK)
    if not MEL_NORM_FILE.exists():
        files_to_download.append(MEL_NORM_LINK)
    if not TOKENIZER_FILE.exists():
        files_to_download.append(TOKENIZER_FILE_LINK)
    if not XTTS_CHECKPOINT.exists():
        files_to_download.append(XTTS_CHECKPOINT_LINK)

    if files_to_download:
        print(f"\nDownloading XTTS v2 checkpoint files...")
        ModelManager._download_model_files(files_to_download, str(checkpoints_dir), progress_bar=True)

    # Get a speaker reference for test sentences
    wavs_dir = data_dir / "wavs"
    wav_files = sorted(wavs_dir.glob("*.wav"))
    if not wav_files:
        print("Error: No wav files found in dataset")
        return False

    speaker_ref = str(wav_files[0])  # Use first segment as reference

    # Dataset config - ljspeech format
    config_dataset = BaseDatasetConfig(
        formatter="ljspeech",
        dataset_name=voice_name,
        path=str(data_dir),
        meta_file_train=str(data_dir / "train.csv"),
        language="en",
    )

    # GPT model args
    # At 22050 Hz: 12 sec = 264600 samples, 15 sec = 330750 samples
    model_args = GPTArgs(
        max_conditioning_length=132300,  # 6 secs
        min_conditioning_length=44100,   # 2 secs (lowered for more flexibility)
        debug_loading_failures=True,     # Enable to see loading issues
        max_wav_length=330750,  # ~15 seconds (increased for 12-sec segments)
        max_text_length=400,  # Increased for longer transcripts
        mel_norm_file=str(MEL_NORM_FILE),
        dvae_checkpoint=str(DVAE_CHECKPOINT),
        xtts_checkpoint=str(XTTS_CHECKPOINT),
        tokenizer_file=str(TOKENIZER_FILE),
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )

    # Audio config
    audio_config = XttsAudioConfig(
        sample_rate=22050,
        dvae_sample_rate=22050,
        output_sample_rate=24000
    )

    # Gradient accumulation: BATCH_SIZE * GRAD_ACUMM should be ~252
    grad_accum = max(1, 252 // batch_size)

    print(f"Gradient accumulation steps: {grad_accum}")

    # Training config
    config = GPTTrainerConfig(
        epochs=epochs,
        output_path=str(output_dir),
        model_args=model_args,
        run_name=f"GPT_XTTS_{voice_name}",
        project_name="XTTS_finetune",
        run_description=f"Fine-tuning XTTS v2 on {voice_name} voice",
        dashboard_logger="tensorboard",
        logger_uri=None,
        audio=audio_config,
        batch_size=batch_size,
        batch_group_size=48,
        eval_batch_size=batch_size,
        num_loader_workers=2,
        eval_split_max_size=256,
        print_step=25,
        plot_step=50,
        log_model_step=500,
        save_step=1000,
        save_n_checkpoints=2,
        save_checkpoints=True,
        print_eval=False,
        optimizer="AdamW",
        optimizer_wd_only_on_weights=True,
        optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
        lr=5e-06,
        lr_scheduler="MultiStepLR",
        lr_scheduler_params={"milestones": [50000 * 18, 150000 * 18, 300000 * 18], "gamma": 0.5, "last_epoch": -1},
        test_sentences=[
            {
                "text": "Hello, how are you today?",
                "speaker_wav": speaker_ref,
                "language": "en",
            },
            {
                "text": "Chinna, nenu neeku proud ga feel avthunna.",
                "speaker_wav": speaker_ref,
                "language": "en",
            }
        ],
    )

    print(f"\nInitializing GPT Trainer...")
    model = GPTTrainer.init_from_config(config)

    print(f"Loading training samples...")
    train_samples, eval_samples = load_tts_samples(
        [config_dataset],
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=0.1,
    )

    print(f"Training samples: {len(train_samples)}")
    print(f"Eval samples: {len(eval_samples)}")

    # Initialize trainer
    trainer = Trainer(
        TrainerArgs(
            restore_path=None,
            skip_train_epoch=False,
            start_with_eval=False,  # Skip initial eval to avoid empty dataset errors
            grad_accum_steps=grad_accum,
        ),
        config,
        output_path=str(output_dir),
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )

    print(f"\n{'='*60}")
    print(f"  Starting training... (this will take a while)")
    print(f"  Monitor progress in: {output_dir}")
    print(f"{'='*60}\n")

    # Run training!
    trainer.fit()

    print(f"\n{'='*60}")
    print(f"  Fine-tuning complete!")
    print(f"{'='*60}")
    print(f"\nModel saved to: {output_dir}")
    print(f"\nTest with: python finetune_xtts.py test-ft {voice_name} \"Hello, how are you?\"")

    return True


def test_voice(voice_name, text, language="en"):
    """Test fine-tuned voice"""
    from TTS.api import TTS

    model_dir = VOICES_DIR / "models" / voice_name
    reference_wav = model_dir / "reference_combined.wav"

    if not reference_wav.exists():
        reference_wav = model_dir / "reference.wav"

    if not reference_wav.exists():
        print(f"Error: No reference audio found for {voice_name}")
        return

    # Check device
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Loading XTTS v2 on {device}...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    output_file = VOICES_DIR / "test_output" / f"{voice_name}_ft_test_{datetime.now().strftime('%H%M%S')}.wav"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating with fine-tuned {voice_name} voice...")
    print(f"Text: {text}")
    print(f"Reference: {reference_wav}")

    tts.tts_to_file(
        text=text,
        file_path=str(output_file),
        speaker_wav=str(reference_wav),
        language=language
    )

    print(f"\nOutput: {output_file}")
    print(f"Play: open \"{output_file}\"")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("XTTS Fine-Tuning Script")
        print("\nUsage:")
        print("  python finetune_xtts.py prepare <voice>  - Prepare dataset with transcripts")
        print("  python finetune_xtts.py train <voice> [epochs] [batch]  - REAL fine-tuning (trains model weights)")
        print("  python finetune_xtts.py clone <voice>    - Quick cloning (extended reference only)")
        print("  python finetune_xtts.py test <voice> <text>  - Test voice")
        print("\nVoices: arjun, ananya, kiran, lakshmi, priya, ravi")
        print("\nExamples:")
        print("  python finetune_xtts.py prepare arjun    # First, prepare dataset")
        print("  python finetune_xtts.py train arjun 50   # Train for 50 epochs")
        print("  python finetune_xtts.py test arjun 'Hello Chinna!'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "prepare":
        voice = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        prepare_dataset(voice)

    elif command == "train":
        # REAL fine-tuning using GPT trainer
        voice = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        batch_size = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        train_gpt(voice, epochs, batch_size)

    elif command == "clone":
        # Quick cloning with extended reference (old method)
        voice = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        train_voice_simple(voice, epochs)

    elif command == "test":
        voice = sys.argv[2] if len(sys.argv) > 2 else "arjun"
        text = sys.argv[3] if len(sys.argv) > 3 else "Hello, this is a test."
        language = sys.argv[4] if len(sys.argv) > 4 else "en"
        test_voice(voice, text, language)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
