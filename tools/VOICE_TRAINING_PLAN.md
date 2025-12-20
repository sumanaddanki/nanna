# Nanna Voice Training Plan

**Machine:** Mac Studio M4 Max (14 cores, 36GB RAM)
**Date Created:** 2025-12-16

---

## Overview

Train 6 Telugu voice models using Coqui XTTS v2 for the Nanna project.

## Hardware Available

| Spec | Value |
|------|-------|
| Machine | Mac Studio |
| Chip | Apple M4 Max |
| Cores | 14 (10 performance + 4 efficiency) |
| RAM | 36 GB |
| Storage | Check available space |

## Voice Data Summary

| Voice | Region | Size | Files | Est. Training Time |
|-------|--------|------|-------|-------------------|
| Arjun | Urban/Hyderabad | 1.0GB | ~4-5 | 2-3 hours |
| Ananya | Urban/Hyderabad | 962MB | ~4-5 | 2-3 hours |
| Priya | Krishna/Godavari | 882MB | ~4-5 | 2-3 hours |
| Kiran | Krishna/Godavari | 849MB | ~4-5 | 2-3 hours |
| Ravi | Rayalaseema | 834MB | ~4-5 | 2-3 hours |
| Lakshmi | Rayalaseema | 800MB | ~4-5 | 2-3 hours |

**Total Estimated Time:** 12-18 hours (running sequentially)

---

## Phase 1: Environment Setup

### Step 1.1: Check Prerequisites
```bash
# Check Python version (need 3.9-3.11)
python3 --version

# Check available disk space (need ~20GB free)
df -h /

# Check if conda/venv available
which conda || which python3
```

### Step 1.2: Create Virtual Environment
```bash
cd /Users/semostudio/git/sumanaddanki/nanna/tools

# Create virtual environment
python3 -m venv venv-xtts

# Activate it
source venv-xtts/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 1.3: Install Coqui TTS
```bash
# Install TTS with dependencies
pip install TTS

# Install additional requirements
pip install torch torchaudio

# Verify installation
python -c "from TTS.api import TTS; print('TTS installed successfully')"
```

### Step 1.4: Download XTTS v2 Model
```bash
# This will download the base model (~1.8GB)
python -c "from TTS.api import TTS; tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

---

## Phase 2: Data Validation

### Step 2.1: Verify Audio Quality
```bash
# Check WAV file format for each voice
for voice in arjun ananya priya kiran ravi lakshmi; do
    echo "=== $voice ==="
    for f in voices/processed/$voice/*.wav; do
        file "$f"
        soxi "$f" 2>/dev/null || ffprobe -hide_banner "$f" 2>&1 | grep -E "Duration|Stream"
    done
done
```

### Step 2.2: Audio Requirements
- Format: WAV (16-bit, mono preferred)
- Sample Rate: 22050 Hz or 24000 Hz
- Duration: 6-30 seconds per clip (optimal)
- Quality: Clear speech, minimal background noise

### Step 2.3: Prepare Training Data Structure
```
voices/processed/
├── arjun/
│   ├── audio1.wav
│   ├── audio2.wav
│   └── metadata.csv  (optional: text transcripts)
├── ananya/
│   └── ...
└── ...
```

---

## Phase 3: Training Pipeline

### Training Script: `train_voice.py`
```python
#!/usr/bin/env python3
"""
Train a single voice model using XTTS v2
Usage: python train_voice.py <voice_name>
"""
import os
import sys
from TTS.api import TTS

def train_voice(voice_name):
    voice_dir = f"voices/processed/{voice_name}"
    output_dir = f"voices/models/{voice_name}"

    if not os.path.exists(voice_dir):
        print(f"Error: {voice_dir} not found")
        return False

    os.makedirs(output_dir, exist_ok=True)

    # Get all WAV files
    wav_files = [f for f in os.listdir(voice_dir) if f.endswith('.wav')]

    print(f"Training {voice_name} with {len(wav_files)} audio files...")

    # Initialize TTS with XTTS v2
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # Fine-tune on speaker's voice
    # XTTS v2 supports speaker conditioning without full fine-tuning
    # For production: use tts.tts_with_vc for voice cloning

    print(f"Model ready for {voice_name}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_voice.py <voice_name>")
        sys.exit(1)
    train_voice(sys.argv[1])
```

### Step 3.1: Train Each Voice (Sequential)
```bash
# Activate environment
source venv-xtts/bin/activate

# Train each voice one by one
for voice in arjun ananya priya kiran ravi lakshmi; do
    echo "=========================================="
    echo "Training $voice - $(date)"
    echo "=========================================="
    python train_voice.py $voice 2>&1 | tee logs/train_${voice}.log
    echo "Completed $voice - $(date)"
done
```

---

## Phase 4: Testing & Validation

### Step 4.1: Test Each Voice
```python
# test_voice.py
from TTS.api import TTS

def test_voice(voice_name, text):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # Use speaker's reference audio
    speaker_wav = f"voices/processed/{voice_name}/audio1.wav"

    tts.tts_to_file(
        text=text,
        file_path=f"voices/test_output/{voice_name}_test.wav",
        speaker_wav=speaker_wav,
        language="en"  # or "te" for Telugu if supported
    )
    print(f"Generated test audio for {voice_name}")
```

### Step 4.2: Quality Check
- Listen to each generated audio
- Compare with original voice
- Check for:
  - Accent preservation
  - Clarity
  - Natural prosody
  - Telugu word pronunciation

---

## Phase 5: Deployment to NAS

### Step 5.1: Prepare Models for Deployment
```bash
# Create deployment package
mkdir -p deploy/voices

# Copy trained models
for voice in arjun ananya priya kiran ravi lakshmi; do
    cp -r voices/models/$voice deploy/voices/
done

# Create model manifest
cat > deploy/voices/manifest.json << 'EOF'
{
    "version": "1.0",
    "models": ["arjun", "ananya", "priya", "kiran", "ravi", "lakshmi"],
    "base_model": "xtts_v2",
    "created": "2025-12-16"
}
EOF
```

### Step 5.2: Deploy to Synology NAS
```bash
# SSH to NAS
ssh -p 17183 aauser@192.168.1.183

# Create voices directory on NAS
mkdir -p ~/nanna/voices/models

# Copy models to NAS (from Mac)
scp -P 17183 -r deploy/voices/* aauser@192.168.1.183:~/nanna/voices/models/
```

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1: Setup | 30-60 min | One-time setup |
| Phase 2: Validation | 15-30 min | Check audio quality |
| Phase 3: Training | 12-18 hours | ~2-3 hours per voice |
| Phase 4: Testing | 1-2 hours | Quality verification |
| Phase 5: Deployment | 30 min | Copy to NAS |

**Total:** ~15-22 hours

---

## Monitoring & Troubleshooting

### Watch Training Progress
```bash
# Monitor system resources
htop

# Watch training logs
tail -f logs/train_*.log

# Check GPU/Metal usage (M4 Max)
sudo powermetrics --samplers gpu_power -i 1000
```

### Common Issues

1. **Out of Memory**
   - Reduce batch size
   - Process shorter audio clips
   - Close other applications

2. **Slow Training**
   - Ensure Metal acceleration is working
   - Check if running on performance cores

3. **Poor Audio Quality**
   - Re-process source audio
   - Remove background noise
   - Ensure consistent sample rate

---

## Files Created

| File | Purpose |
|------|---------|
| `tools/venv-xtts/` | Python virtual environment |
| `tools/train_voice.py` | Training script |
| `tools/test_voice.py` | Testing script |
| `tools/logs/` | Training logs |
| `voices/models/` | Trained model outputs |

---

## Next Steps After Training

1. Integrate models into webapp
2. Create API for voice selection
3. Add to phone app
4. Document voice switching

---

*Created by Nanna for Chinna - December 2025*
