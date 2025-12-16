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
/Users/sumanaddanke/git/sumanaddanki/nanna/tools/
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

### MacBook Air M2 (Voice Collection - Source)
- **Model:** MacBook Air M2 (Mac14,2)
- **Serial:** XQVFY6V256
- **Hostname:** Mac
- **User:** sumanaddanke
- **RAM:** 8GB
- **Location:** US
- **Voice data path:** `/Users/sumanaddanke/git/sumanaddanki/nanna/tools/voices/processed/` (5.1GB)

### Mac Studio M4 Max (Training - Target) - SETUP COMPLETE!
- **Model:** Mac Studio M4 Max
- **RAM:** 36GB
- **GPU:** 32-core
- **Storage:** 512GB SSD
- **Price:** $1,999
- **Hostname:** Mac-Studio
- **Username:** semostudio
- **IP Address:** 192.168.1.196 (WiFi - en1)
- **Git Repo:** `/Users/semostudio/git/sumanaddanki/nanna/`
- **Voice Data:** `/Users/semostudio/git/sumanaddanki/nanna/tools/voices/processed/` (5.1GB transferred)
- **Purpose:** Train 6 voices with Coqui XTTS v2
- **SSH Key:** Configured from MacBook Air
- **Remote Login:** Enabled

### NAS Infrastructure

**US (Home) - Current:**
- **Model:** Synology DS225+
- **Current:** 2x 2TB HDD
- **Upgrade:** 2x 4TB HDD (buying)

**India (Dev/QA) - New:**
- **Model:** Synology DS923+ (~$550)
- **Main Bays:** 2x 2TB HDD (reused from US)
- **M.2 Slots:** 2x 2TB NVMe (buying)
- **Purpose:** Dev/QA testing, serve India users

---

## Transfer to Mac Studio

### When Mac Studio Arrives (Tomorrow):

**Step 1: Transfer voice data (5.2GB)**
```bash
# Option A: AirDrop (easiest)
# Open Finder → AirDrop → drag voices/processed/ folder

# Option B: USB Drive
# Copy to USB, then to Mac Studio

# Option C: Network transfer (if on same WiFi)
# On Mac Studio, enable File Sharing in System Settings
# From MacBook:
scp -r /Users/sumanaddanke/git/nanna/tools/voices/processed/ macstudio.local:/Users/[username]/nanna/voices/

# Option D: Direct cable (Thunderbolt Target Disk Mode)
# Fastest for large files
```

**Step 2: Clone git repo on Mac Studio**
```bash
cd ~
git clone [your-repo-url] nanna
cd nanna
```

**Step 3: Install dependencies**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install Coqui TTS
pip3.11 install TTS torch torchaudio
```

**Step 4: Start training**
```bash
cd ~/nanna/tools
# Training commands TBD after setup
```

### Files to Transfer:
| Source (MacBook Air) | Size | Destination (Mac Studio) |
|---------------------|------|-------------------------|
| `tools/voices/processed/` | 5.2GB | `~/nanna/tools/voices/processed/` |

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
