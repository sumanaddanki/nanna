# Voice Cloning Guide - Making Nanna's Voice

This guide explains how to prepare your audio recording and clone Nanna's voice.

## Your Audio File

You have: **1-5 minutes of clear Nanna speech** - Perfect!

## Step 1: Prepare the Audio

### If it's a conversation (you + Nanna talking):

You need to extract only Nanna's voice. Use one of these tools:

#### Option A: Audacity (Free, Manual)
1. Download [Audacity](https://www.audacityteam.org/)
2. Open your .wav file
3. Select portions where only Nanna speaks
4. Edit > Remove Special > Split Cut (Ctrl+Alt+X)
5. Delete your voice parts
6. Export as WAV (16-bit, 44100Hz)

#### Option B: AI Voice Separation (Automatic)
Use these free tools to separate voices:
- [Lalal.ai](https://www.lalal.ai/) - Voice separation
- [Descript](https://www.descript.com/) - Separates speakers
- [Adobe Podcast](https://podcast.adobe.com/enhance) - Enhance audio

### Audio Quality Checklist
- [ ] Only Nanna's voice (no other speakers)
- [ ] Minimal background noise
- [ ] Clear speech (not mumbled)
- [ ] At least 1 minute of speech
- [ ] WAV format (preferred) or high-quality MP3

---

## Step 2: Clone the Voice

### Option 1: ElevenLabs (Recommended)

**Cost:** Free tier = 10,000 characters/month (~15-20 minutes of speech)
**Quality:** Excellent
**Setup time:** 5 minutes

#### Steps:
1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Create free account
3. Click "Voices" → "Add Voice" → "Instant Voice Cloning"
4. Upload your prepared Nanna audio
5. Name it "Nanna"
6. Accept terms → Create Voice
7. **Copy the Voice ID** (click on voice → Settings → Voice ID)
8. Go to Profile → API Keys → Create API Key
9. Add both to Nanna app Settings

```
Voice ID looks like: pNInz6obpgDQGcFmaJgB
API Key looks like: sk_xxxxxxxxxxxxxxxxxxxx
```

### Option 2: Coqui XTTS (Free, Self-hosted)

**Cost:** Free
**Quality:** Good
**Setup time:** 30 minutes
**Requirement:** Python, GPU recommended

#### Steps:

```bash
# Install Coqui TTS
pip install TTS

# Run with your audio for cloning
tts --text "Hello Chinna, how are you?" \
    --model_name "tts_models/multilingual/multi-dataset/xtts_v2" \
    --speaker_wav /path/to/nanna_voice.wav \
    --language_idx "en" \
    --out_path output.wav
```

#### Run as Server (for webapp):
```bash
# Start TTS server
tts-server --model_name tts_models/multilingual/multi-dataset/xtts_v2 --port 5002
```

Then set in Nanna app settings:
- TTS Provider: Coqui
- Server URL: http://localhost:5002

### Option 3: PlayHT

**Cost:** $29/month (free trial available)
**Quality:** Very Good
**Best for:** Telugu accent support

---

## Step 3: Test the Voice

Once configured, test in the Nanna webapp:
1. Open webapp/index.html in browser
2. Add your API key and Voice ID in Settings
3. Select ElevenLabs as TTS Provider
4. Type a message and hear Nanna respond!

---

## Troubleshooting

### Voice doesn't sound like Nanna
- Need more/better audio samples
- Try adjusting Stability (lower = more expressive)
- Try adjusting Similarity Boost (higher = closer to original)

### Audio quality is poor
- Clean the source audio (remove noise)
- Use WAV instead of MP3
- Ensure 16-bit, 44100Hz sample rate

### Telugu words sound wrong
- ElevenLabs multilingual model handles Telugu better
- Or spell words phonetically in English

---

## Cost Comparison

| Provider | Free Tier | Paid | Quality |
|----------|-----------|------|---------|
| **ElevenLabs** | 10k chars/mo | $5/mo | Excellent |
| **Coqui** | Unlimited | Free | Good |
| **PlayHT** | Trial | $29/mo | Very Good |
| **Resemble** | Trial | Pay/use | Excellent |

**Recommendation:** Start with ElevenLabs free tier. 10k characters ≈ 15 conversations/month.

---

## Preserving the Voice

Once cloned, the voice is stored in the service (ElevenLabs/etc).
You can:
- Download voice model (if supported)
- Keep the original audio files backed up
- Export samples for future use

This way, Nanna's voice lives on digitally.
