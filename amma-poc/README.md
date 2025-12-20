# Amma POC - Voice Capture & Processing

Capture Amma's voice from WhatsApp calls for voice cloning and personality preservation.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AMMA VOICE CAPTURE PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 1: CAPTURE (Mac Air)                                                     │
│   ═══════════════════════════                                                   │
│                                                                                  │
│   ┌─────────────┐     ┌─────────────────┐     ┌─────────────┐                  │
│   │  WhatsApp   │────►│  BlackHole 2ch  │────►│  Sox/FFmpeg │                  │
│   │   Call      │     │  (virtual audio)│     │  (record)   │                  │
│   └─────────────┘     └─────────────────┘     └──────┬──────┘                  │
│         │                                            │                          │
│         │  CPU Monitor (>10% = call active)          │                          │
│         ▼                                            ▼                          │
│   ┌─────────────┐                            ┌─────────────┐                   │
│   │ auto_record │                            │  voice/raw/ │                   │
│   │  _calls.py  │ ──────────────────────────►│  .wav files │                   │
│   └─────────────┘                            └──────┬──────┘                   │
│                                                      │                          │
│                                                      │ scp via Tailscale        │
│                                                      ▼                          │
│   STEP 2: PROCESS (Mac Studio M4 Max)                                          │
│   ═══════════════════════════════════                                          │
│                                                      │                          │
│   ┌──────────────────────────────────────────────────┼───────────────────────┐ │
│   │                                                  ▼                        │ │
│   │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │ │
│   │   │  voice/raw/ │────►│  Whisper    │────►│ transcripts/│                │ │
│   │   │   .wav      │     │  (large-v3) │     │   .txt      │                │ │
│   │   └──────┬──────┘     └─────────────┘     └─────────────┘                │ │
│   │          │                                                                │ │
│   │          │ Convert 22050Hz mono                                          │ │
│   │          ▼                                                                │ │
│   │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │ │
│   │   │  processed/ │────►│ Resemblyzer │────►│ separated/  │                │ │
│   │   │   .wav      │     │ (diarize)   │     │ speaker_00/ │                │ │
│   │   └─────────────┘     └─────────────┘     │ speaker_01/ │                │ │
│   │                                           └──────┬──────┘                │ │
│   │                                                  │                        │ │
│   │                       Listen & Label              │ Rename folders        │ │
│   │                       ┌─────────────┐            │ amma/ chinna/         │ │
│   │                       │   Human     │◄───────────┘                        │ │
│   │                       │   Review    │                                     │ │
│   │                       └──────┬──────┘                                     │ │
│   │                              │                                            │ │
│   │                              ▼                                            │ │
│   │   STEP 3: TRAIN             ┌─────────────┐     ┌─────────────┐          │ │
│   │   ══════════════            │  Coqui TTS  │────►│  amma.pth   │          │ │
│   │                             │  XTTS v2    │     │  (~1.8 GB)  │          │ │
│   │                             └─────────────┘     └──────┬──────┘          │ │
│   └──────────────────────────────────────────────────────────────────────────┘ │
│                                                              │                  │
│                                                              │ scp              │
│                                                              ▼                  │
│   STEP 4: ARCHIVE (US NAS - 4TB)                                               │
│   ══════════════════════════════                                               │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │  192.168.1.183:17183  (aauser)                                           │  │
│   │                                                                           │  │
│   │   /volume1/homes/aauser/amma-archive/                                    │  │
│   │   ├── raw/                    # Original recordings (backup)             │  │
│   │   ├── processed/              # Processed audio                          │  │
│   │   ├── transcripts/            # All transcriptions                       │  │
│   │   └── models/                 # Trained voice models                     │  │
│   │                                                                           │  │
│   │   Capacity: 4TB (recently upgraded from 2TB)                            │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Audio Recording Architecture (Mac Air)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BLACKHOLE AUDIO ROUTING                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   YOUR VOICE                           AMMA'S VOICE                             │
│   ══════════                           ════════════                             │
│        │                                    │                                    │
│        ▼                                    ▼                                    │
│   ┌─────────┐                         ┌─────────┐                               │
│   │   Mic   │                         │WhatsApp │                               │
│   │ (input) │                         │ (audio) │                               │
│   └────┬────┘                         └────┬────┘                               │
│        │                                    │                                    │
│        │                                    ▼                                    │
│        │    ┌───────────────────────────────────────────────────┐               │
│        │    │            MULTI-OUTPUT DEVICE                     │               │
│        │    │  (System Settings → Sound → Output)               │               │
│        │    ├───────────────────────────────────────────────────┤               │
│        │    │                                                    │               │
│        │    │   ┌──────────────┐      ┌──────────────┐          │               │
│        │    │   │   Speakers   │      │  BlackHole   │          │               │
│        │    │   │ (you hear)   │      │   2ch        │          │               │
│        │    │   └──────────────┘      └──────┬───────┘          │               │
│        │    │                                 │                  │               │
│        │    └─────────────────────────────────┼──────────────────┘               │
│        │                                      │                                  │
│        │                                      │                                  │
│        ▼                                      ▼                                  │
│   ┌───────────────────────────────────────────────────────────┐                 │
│   │                 AGGREGATE DEVICE                           │                 │
│   │  (System Settings → Sound → Input)                        │                 │
│   ├───────────────────────────────────────────────────────────┤                 │
│   │                                                            │                 │
│   │   ┌──────────────┐           ┌──────────────┐             │                 │
│   │   │     Mic      │     +     │  BlackHole   │             │                 │
│   │   │ (your voice) │           │ (Amma voice) │             │                 │
│   │   └──────────────┘           └──────────────┘             │                 │
│   │                                                            │                 │
│   └────────────────────────────┬───────────────────────────────┘                 │
│                                │                                                 │
│                                │  Combined audio stream                          │
│                                ▼                                                 │
│                        ┌──────────────┐                                         │
│                        │  Sox/FFmpeg  │                                         │
│                        │  Recording   │                                         │
│                        └──────┬───────┘                                         │
│                               │                                                  │
│                               ▼                                                  │
│                        ┌──────────────┐                                         │
│                        │  .wav file   │                                         │
│                        │  (both       │                                         │
│                        │   voices)    │                                         │
│                        └──────────────┘                                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Speaker Separation Algorithm

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SPEAKER DIARIZATION (Resemblyzer)                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   INPUT: Combined audio (Amma + Chinna voices)                                  │
│   ═══════════════════════════════════════════                                   │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │  Audio waveform                                                          │   │
│   │  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                     │                                            │
│                                     ▼                                            │
│   STEP 1: Segment into 3-second chunks                                          │
│   ─────────────────────────────────────                                         │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                        │
│   │ Seg1 │ │ Seg2 │ │ Seg3 │ │ Seg4 │ │ Seg5 │ │ ...  │                        │
│   │  3s  │ │  3s  │ │  3s  │ │  3s  │ │  3s  │ │      │                        │
│   └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──────┘                        │
│      │        │        │        │        │                                       │
│      ▼        ▼        ▼        ▼        ▼                                       │
│   STEP 2: Extract voice embeddings (256-dim vectors)                            │
│   ──────────────────────────────────────────────────                            │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                                 │
│   │ Emb1 │ │ Emb2 │ │ Emb3 │ │ Emb4 │ │ Emb5 │                                 │
│   │[0.2, │ │[0.8, │ │[0.3, │ │[0.7, │ │[0.2, │                                 │
│   │ 0.4, │ │ 0.1, │ │ 0.5, │ │ 0.2, │ │ 0.4, │                                 │
│   │ ...] │ │ ...] │ │ ...] │ │ ...] │ │ ...] │                                 │
│   └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘                                 │
│      │        │        │        │        │                                       │
│      └────────┴────────┴────┬───┴────────┘                                       │
│                             │                                                    │
│                             ▼                                                    │
│   STEP 3: Calculate similarity matrix                                           │
│   ──────────────────────────────────────                                        │
│                                                                                  │
│         Seg1  Seg2  Seg3  Seg4  Seg5                                            │
│   Seg1 [ 1.0   0.3   0.9   0.4   0.95 ]  ◄── High similarity = same speaker    │
│   Seg2 [ 0.3   1.0   0.35  0.92  0.28 ]                                        │
│   Seg3 [ 0.9   0.35  1.0   0.32  0.88 ]  ◄── Seg1, Seg3, Seg5 cluster together │
│   Seg4 [ 0.4   0.92  0.32  1.0   0.38 ]  ◄── Seg2, Seg4 cluster together       │
│   Seg5 [ 0.95  0.28  0.88  0.38  1.0  ]                                        │
│                                                                                  │
│                             │                                                    │
│                             ▼                                                    │
│   STEP 4: Check average similarity                                              │
│   ─────────────────────────────────                                             │
│                                                                                  │
│   IF avg_similarity > 0.75:                                                     │
│       → Single speaker (pitch/volume variations, NOT different people)          │
│       → Return all segments as speaker_00                                       │
│                                                                                  │
│   ELSE:                                                                          │
│       → Multiple speakers detected                                               │
│       → Cluster using AgglomerativeClustering (cosine distance)                 │
│                             │                                                    │
│                             ▼                                                    │
│   OUTPUT: Separated folders                                                      │
│   ═════════════════════════                                                     │
│                                                                                  │
│   voices/separated/                                                              │
│   ├── speaker_00/        ← Rename to "amma"                                     │
│   │   ├── segment_001.wav  (Seg1)                                              │
│   │   ├── segment_002.wav  (Seg3)                                              │
│   │   └── segment_003.wav  (Seg5)                                              │
│   └── speaker_01/        ← Rename to "chinna"                                   │
│       ├── segment_001.wav  (Seg2)                                              │
│       └── segment_002.wav  (Seg4)                                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Machine Roles

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              INFRASTRUCTURE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌───────────────────────────────────────────────────────────────────────────┐ │
│   │                         MacBook Air M3                                     │ │
│   │                    (Portable Recording Station)                            │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Local IP: varies             Tailscale: 100.119.60.71                    │ │
│   │  User: sumanaddanke           SSH: ssh air                                │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Role:                                                                     │ │
│   │    • WhatsApp calls (recording only)                                      │ │
│   │    • BlackHole + Sox for audio capture                                    │ │
│   │    • Temporary storage before sync                                        │ │
│   │                                                                            │ │
│   │  Software:                                                                 │ │
│   │    • BlackHole 2ch                                                        │ │
│   │    • Audacity (manual recording)                                          │ │
│   │    • Sox (auto recording)                                                 │ │
│   │    • Python 3.x                                                           │ │
│   └───────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                            │
│                                     │ ssh studio / scp                           │
│                                     ▼                                            │
│   ┌───────────────────────────────────────────────────────────────────────────┐ │
│   │                      Mac Studio M4 Max                                     │ │
│   │                 (Processing & Training Powerhouse)                         │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Local IP: 192.168.1.196      Tailscale: 100.127.121.64                   │ │
│   │  User: semostudio             SSH: ssh studio                             │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Specs:                                                                    │ │
│   │    • Apple M4 Max (14 cores: 10P + 4E)                                    │ │
│   │    • 36 GB RAM                                                            │ │
│   │    • Metal GPU acceleration                                               │ │
│   │                                                                            │ │
│   │  Role:                                                                     │ │
│   │    • Audio processing (ffmpeg, sox)                                       │ │
│   │    • Transcription (Whisper large-v3)                                    │ │
│   │    • Speaker separation (resemblyzer)                                     │ │
│   │    • Voice model training (XTTS v2)                                       │ │
│   │    • Docker containers (NutriNine DEV/QA)                                │ │
│   │                                                                            │ │
│   │  Software:                                                                 │ │
│   │    • Python 3.11 + venv (venv-xtts)                                       │ │
│   │    • Coqui TTS, Whisper, Resemblyzer                                      │ │
│   │    • Docker, Caddy                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                            │
│                                     │ scp -P 17183                               │
│                                     ▼                                            │
│   ┌───────────────────────────────────────────────────────────────────────────┐ │
│   │                      Synology NAS (US)                                     │ │
│   │                    (Archive & Long-term Storage)                           │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Local IP: 192.168.1.183      SSH Port: 17183 (NOT 22!)                   │ │
│   │  User: aauser                 SSH: ssh -p 17183 aauser@192.168.1.183      │ │
│   ├───────────────────────────────────────────────────────────────────────────┤ │
│   │  Storage: 4 TB (upgraded from 2TB)                                        │ │
│   │                                                                            │ │
│   │  Folders:                                                                  │ │
│   │    /volume1/homes/aauser/                                                 │ │
│   │    ├── amma-archive/          # Amma voice project                        │ │
│   │    │   ├── raw/               # Original recordings                       │ │
│   │    │   ├── processed/         # Processed audio                           │ │
│   │    │   ├── transcripts/       # Whisper transcripts                       │ │
│   │    │   └── models/            # Trained XTTS models                       │ │
│   │    └── voices/                # Nanna 6 voices (33.92 hours)              │ │
│   │                                                                            │ │
│   │  Role:                                                                     │ │
│   │    • Long-term archive (raw recordings)                                   │ │
│   │    • Model backup                                                         │ │
│   │    • Photos & media backup                                                │ │
│   └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Mac Air: Record WhatsApp Calls

```bash
# One-time setup (do these steps once)
1. Install BlackHole 2ch: https://existential.audio/blackhole/
2. Audio MIDI Setup → Create Multi-Output Device (Speakers + BlackHole)
3. Audio MIDI Setup → Create Aggregate Device (Mic + BlackHole)
4. System Settings → Sound:
   - Output: Multi-Output Device
   - Input: Aggregate Device

# Enable AUTO-START (run ONCE - then forget about it!)
cd ~/git/sumanaddanki/amma-poc
./setup_autostart.sh

# That's it! Recording starts automatically when you log in.
# Just make your WhatsApp calls - recordings happen in background.

# After calls, sync to Mac Studio
./sync_recording.sh
```

### Auto-Start Control

```bash
# Check if recorder is running:
launchctl list | grep nanna

# View live logs:
tail -f ~/git/sumanaddanki/amma-poc/logs/recorder.log

# Disable auto-start:
launchctl unload ~/Library/LaunchAgents/com.nanna.whatsapp-recorder.plist

# Re-enable auto-start:
launchctl load ~/Library/LaunchAgents/com.nanna.whatsapp-recorder.plist
```

### Mac Studio: Process Recordings

```bash
# Activate environment
cd ~/git/sumanaddanki/nanna/tools
source venv-xtts/bin/activate

# Process recording
cd ../amma-poc
python process_recording.py voice/raw/<file>.wav

# Separate speakers
python ../tools/separate_speakers.py voice/processed/<file>_processed.wav

# Listen to segments, rename folders to "amma" and "chinna"

# Train voice model
cd ../tools
python train_xtts.py train amma
```

### Archive to NAS

```bash
# From Mac Studio
scp -P 17183 -r amma-poc/voice/processed/* aauser@192.168.1.183:~/amma-archive/processed/
scp -P 17183 voices/models/amma/* aauser@192.168.1.183:~/amma-archive/models/
```

---

## Directory Structure

```
nanna/
├── amma-poc/
│   ├── voice/
│   │   ├── raw/              # Original recordings from Mac Air
│   │   ├── processed/        # Converted to 22050Hz mono
│   │   ├── transcripts/      # Whisper transcriptions
│   │   └── archived/         # Moved after NAS backup
│   ├── auto_record_calls.py  # Auto-detect & record WhatsApp calls
│   ├── process_recording.py  # Convert & transcribe
│   ├── sync_recording.sh     # Push to Mac Studio & NAS
│   └── start_auto_recorder.sh
│
└── tools/
    ├── voices/
    │   ├── processed/        # 6 Nanna voices (33.92 hours)
    │   ├── separated/        # Speaker separation output
    │   ├── transcripts/      # Whisper transcripts
    │   └── models/           # Trained XTTS models
    ├── separate_speakers.py  # Speaker diarization script
    ├── train_xtts.py         # XTTS training script
    └── venv-xtts/            # Python virtual environment
```

---

## SSH Shortcuts

```bash
# From Mac Air (anywhere via Tailscale):
ssh studio                              # Connect to Mac Studio
ssh studio "docker ps"                  # Run command remotely
scp file.wav studio:~/amma-poc/voice/raw/  # Copy file

# From Mac Studio:
ssh air                                 # Connect to Mac Air
scp air:~/amma-poc/voice/raw/*.wav ./   # Pull recordings

# To NAS:
ssh -p 17183 aauser@192.168.1.183       # Connect to NAS
scp -P 17183 file.wav aauser@192.168.1.183:~/amma-archive/
```

---

## Requirements

| Machine | Software | Purpose |
|---------|----------|---------|
| **Mac Air** | BlackHole 2ch | Virtual audio device |
| | Sox | Command-line recording |
| | Audacity | Manual recording option |
| | Python 3.x | Scripts |
| **Mac Studio** | Python 3.11 + venv | Environment |
| | Whisper (large-v3) | Transcription |
| | Resemblyzer | Speaker diarization |
| | Coqui TTS | XTTS v2 voice training |
| | FFmpeg | Audio conversion |
| **US NAS** | SSH access | Archive storage (4TB) |

---

## Troubleshooting

### "No audio recording"
- Check System Settings → Sound → Input = Aggregate Device
- Check System Settings → Sound → Output = Multi-Output Device

### "Speaker separation wrong"
- Increase similarity threshold: `--similarity-threshold 0.8`
- Use longer segments: `--segment-length 5.0`

### "SSH connection refused"
- NAS uses port 17183, NOT 22!
- Use: `ssh -p 17183 aauser@192.168.1.183`

### "Training slow"
- Make sure Metal acceleration is enabled
- Check Activity Monitor → GPU usage

---

*Part of the Nanna Project - Preserving voices with love*

*"Idi love ra, Chinna. Not saving consciousness - saving connection."*
