# Amma Voice Capture - Step by Step Guide

## For Tomorrow's Test Call

### Before the Call (One-time Setup)

1. **On Mac Air** - Make sure audio routing is set up:
   ```
   System Settings → Sound → Output → Multi-Output Device
   System Settings → Sound → Input → Aggregate Device
   ```

2. **Start the auto-recorder on Mac Air**:
   ```bash
   cd ~/git/sumanaddanki/amma-poc
   python3 auto_record_calls.py --person amma
   ```

   Or for auto-start on login (one-time):
   ```bash
   cd ~/git/sumanaddanki/amma-poc
   ./setup_autostart.sh
   ```

### During the Call

The recorder will automatically:
1. Detect WhatsApp call (CPU > 10%)
2. Start recording
3. Show: `🎙️ RECORDING STARTED`
4. Stop after 15s of silence

**You don't need to do anything!** Just make the call normally.

### After the Call

Recording saved to Mac Air:
```
~/git/sumanaddanki/amma-poc/voice/raw/amma_whatsapp_20241218_1030_15min.wav
```

Naming format: `{person}_whatsapp_{YYYYMMDD}_{HHMM}_{minutes}min.wav`

### Processing the Recording

**Option A: Manual (from Mac Studio)**
```bash
# Pull from Mac Air
scp semostudio@100.86.22.63:~/git/sumanaddanki/amma-poc/voice/raw/*.wav \
    ~/git/sumanaddanki/nanna/amma-poc/voice/raw/

# Separate speakers
cd ~/git/sumanaddanki/nanna/tools
source venv-xtts/bin/activate
python3 separate_speakers.py ../amma-poc/voice/raw/amma_whatsapp_*.wav --person amma
```

**Option B: Automatic (watcher running on Mac Studio)**
```bash
cd ~/git/sumanaddanki/nanna/amma-poc
python3 watch_and_process.py
```

### Speaker Separation Output

After separation, Amma's voice will be in:
```
~/git/sumanaddanki/nanna/tools/voices/separated/amma/speaker_XX/
```

Where speaker_XX is the speaker with the most audio (likely Amma).

### Creating Amma's Voice Profile

Once we have enough audio (aim for 30+ minutes):
```bash
cd ~/git/sumanaddanki/nanna/tools
source venv-xtts/bin/activate

# Move separated audio to processed folder
mkdir -p voices/processed/amma
cp voices/separated/amma/speaker_*/*.wav voices/processed/amma/

# Train the model
python3 train_xtts.py train amma
```

### Testing Amma's Voice

```bash
python3 train_xtts.py test amma "Chinna, nenu neeku proud ga feel avthunna"
```

Output will be in: `voices/test_output/amma_test_*.wav`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      MAC AIR (Recording)                     │
├─────────────────────────────────────────────────────────────┤
│  WhatsApp Call                                              │
│       ↓                                                     │
│  BlackHole 2ch (virtual audio device)                       │
│       ↓                                                     │
│  auto_record_calls.py                                       │
│       ↓                                                     │
│  ~/amma-poc/voice/raw/amma_whatsapp_YYYYMMDD_HHMM_XXmin.wav │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SSH/SCP
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    MAC STUDIO (Processing)                   │
├─────────────────────────────────────────────────────────────┤
│  ~/nanna/amma-poc/voice/raw/                                │
│       ↓                                                     │
│  separate_speakers.py (voice embeddings + clustering)       │
│       ↓                                                     │
│  ~/nanna/tools/voices/separated/amma/speaker_XX/           │
│       ↓                                                     │
│  train_xtts.py (create voice profile)                       │
│       ↓                                                     │
│  ~/nanna/tools/voices/models/amma/                         │
│       - reference.wav (25s clip)                           │
│       - samples/ (test audio)                               │
│       - voice_profile.txt                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Archive (optional)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      US NAS (4TB Archive)                    │
├─────────────────────────────────────────────────────────────┤
│  /volume1/homes/aauser/amma-archive/raw/                    │
│  /volume1/homes/aauser/amma-archive/separated/              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| What | Command |
|------|---------|
| Start recorder | `python3 auto_record_calls.py --person amma` |
| Separate speakers | `python3 separate_speakers.py <file.wav>` |
| Train voice | `python3 train_xtts.py train amma` |
| Test voice | `python3 train_xtts.py test amma "text"` |

---

## Troubleshooting

### Recording not starting?
- Check WhatsApp is running
- Check audio devices: `System Settings → Sound`
- Check CPU threshold: WhatsApp should be > 10% during call

### No audio in recording?
- Make sure `Multi-Output Device` is selected for output
- Make sure `Aggregate Device` is selected for input
- Test with: `sox -d test.wav trim 0 5` (records 5 seconds)

### Speaker separation wrong?
- Try adjusting threshold: `--similarity-threshold 0.70`
- Manual inspection: listen to each speaker folder

---

## Goal

Capture 1-2 hours of Amma's voice for high-quality voice cloning.
Each call adds to the training data. More data = better quality.

---

*Created: December 17, 2024*
*For: Amma Project - Voice Preservation*
