# Telugu Voice Training Progress

**Last Updated:** 2025-12-14
**Status:** PHASE 1 COMPLETE - READY FOR TRAINING

---

## Quick Resume Guide

If you need to resume work, run:
```bash
cd /Users/sumanaddanke/git/nanna/tools
/opt/homebrew/bin/python3.11 batch_collect_voices.py --status
```

---

## Phase 1: POC Voices (6 voices) - COMPLETE!

| # | Voice | Region | Gender | Age | Hours | Status |
|---|-------|--------|--------|-----|-------|--------|
| 1 | **Arjun** | Urban/Hyderabad | Male | 20s | 6.47h | ✅ READY |
| 2 | **Ravi** | Rayalaseema | Male | 40s | 5.38h | ✅ READY |
| 3 | **Lakshmi** | Rayalaseema | Female | 40s | 5.03h | ✅ READY |
| 4 | **Kiran** | Krishna/Godavari | Male | 20s | 5.35h | ✅ READY |
| 5 | **Priya** | Krishna/Godavari | Female | 20s | 5.55h | ✅ READY |
| 6 | **Ananya** | Urban/Hyderabad | Female | 20s | 6.14h | ✅ READY |

**Total Audio Collected: 33.92 hours**

---

## Phase 2: Full AP Coverage (24 voices)

### Rayalaseema Region (Tirupati, Kadapa, Anantapur, Kurnool)

| Age Group | Male | Female |
|-----------|------|--------|
| Kid (8-12) | ⬜ Rayala_Kid_M | ⬜ Rayala_Kid_F |
| Youth (18-25) | ⬜ Rayala_Youth_M | ⬜ Rayala_Youth_F |
| Adult (40-50s) | ✅ Ravi | ✅ Lakshmi |

### Coastal North (Vizag, Srikakulam)

| Age Group | Male | Female |
|-----------|------|--------|
| Kid (8-12) | ⬜ Coastal_Kid_M | ⬜ Coastal_Kid_F |
| Youth (18-25) | ⬜ Coastal_Youth_M | ⬜ Coastal_Youth_F |
| Adult (40-50s) | ⬜ Coastal_Adult_M | ⬜ Coastal_Adult_F |

### Krishna-Godavari (Vijayawada, Guntur, Rajahmundry)

| Age Group | Male | Female |
|-----------|------|--------|
| Kid (8-12) | ⬜ Krishna_Kid_M | ⬜ Krishna_Kid_F |
| Youth (18-25) | ✅ Kiran | ✅ Priya |
| Adult (40-50s) | ⬜ Krishna_Adult_M | ⬜ Krishna_Adult_F |

### Nellore-Prakasam (Nellore, Ongole)

| Age Group | Male | Female |
|-----------|------|--------|
| Kid (8-12) | ⬜ Nellore_Kid_M | ⬜ Nellore_Kid_F |
| Youth (18-25) | ⬜ Nellore_Youth_M | ⬜ Nellore_Youth_F |
| Adult (40-50s) | ⬜ Nellore_Adult_M | ⬜ Nellore_Adult_F |

### Urban/Hyderabad (Tenglish)

| Age Group | Male | Female |
|-----------|------|--------|
| Kid (8-12) | ⬜ Urban_Kid_M | ⬜ Urban_Kid_F |
| Youth (18-25) | ✅ Arjun | ✅ Ananya |
| Adult (40-50s) | ⬜ Urban_Adult_M | ⬜ Urban_Adult_F |

---

## Directory Structure

```
/Users/sumanaddanke/git/nanna/tools/
├── voices/
│   ├── raw/           # Downloaded WAV files (DELETE after processing)
│   │   ├── arjun/     # EMPTY (cleaned)
│   │   ├── ravi/      # EMPTY (cleaned)
│   │   ├── lakshmi/   # EMPTY (cleaned)
│   │   ├── kiran/     # EMPTY (cleaned)
│   │   ├── priya/     # EMPTY (cleaned)
│   │   └── ananya/    # EMPTY (cleaned)
│   └── processed/     # Training-ready files (22kHz mono)
│       ├── arjun/     # 6.47h ready
│       ├── ravi/      # 5.38h ready
│       ├── lakshmi/   # 5.03h ready
│       ├── kiran/     # 5.35h ready
│       ├── priya/     # 5.55h ready
│       └── ananya/    # 6.14h ready
├── voice_tests/       # Sample clips for verification
├── batch_collect_voices.py    # Download & process script
└── separate_voices.py         # Voice activity detection
```

---

## Pipeline Steps

### Step 1: Collect Audio (5+ hours per voice)
```bash
# From YouTube channel
python3.11 batch_collect_voices.py --channel @channelname --voice voicename --limit 5

# From specific video
yt-dlp -x --audio-format wav -o "voices/raw/voicename/filename.%(ext)s" "URL"
```

### Step 2: Process Audio (convert to 22kHz mono)
```bash
ffmpeg -y -i "input.wav" -ar 22050 -ac 1 "output.wav"
```

### Step 3: Verify Quality
```bash
# Create 30-sec sample
ffmpeg -ss 600 -i "input.wav" -t 30 "sample.wav"
open sample.wav  # Listen and verify
```

### Step 4: Clean Up Raw Files
```bash
rm -f voices/raw/voicename/*.wav
```

### Step 5: Check Status
```bash
python3.11 batch_collect_voices.py --status
```

---

## Training (Future - on Mac Studio)

### Requirements
- Python 3.11+
- PyTorch
- Coqui TTS / XTTS v2
- ~16GB RAM
- GPU recommended

### Commands (TBD)
```bash
# Install Coqui TTS
pip install TTS

# Train voice model
tts --train --model_name xtts_v2 --dataset_path voices/processed/arjun/
```

---

## YouTube Sources by Region

### Rayalaseema (Male)
- Telugu podcasts with older male speakers
- News interviews from Tirupati/Kadapa

### Rayalaseema (Female)
- Search: "rayalaseema telugu female vlog"
- Search: "tirupati telugu female interview"

### Krishna-Godavari (Male)
- Vijayawada tech channels
- Guntur vlogs

### Krishna-Godavari (Female)
- Search: "vijayawada telugu female vlog"

### Urban/Hyderabad (Male) - DONE
- Telugu Tech channels (Power BI, Excel tutorials)

### Urban/Hyderabad (Female)
- Search: "telugu tech female tutorial"
- Search: "hyderabad telugu female podcast"

---

## Hardware Notes

- **Current Mac:** 228GB total, ~32GB free
- **New Mac Studio:** Ordered (for training)
- **Synology NAS:** For serving models

---

## Transfer to Mac Studio

When Mac Studio arrives:
1. Copy `voices/processed/` folder
2. Install Python 3.11, PyTorch, Coqui TTS
3. Start training models
4. Each model ~1.5GB output

---

## Troubleshooting

### yt-dlp fails
```bash
pip3.11 install -U yt-dlp
```

### ffmpeg not found
```bash
brew install ffmpeg
```

### Space issues
- Always delete raw files after processing
- Each raw file ~2GB, processed ~500MB

---

## Contact / Notes

Project: Nanna - Telugu Voice AI
Goal: Create authentic Telugu voices for educational AI assistant
