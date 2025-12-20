# Amma Project - Preserving Mother's Essence

**Created:** December 17, 2025
**Status:** POC Planning

---

## Vision

Create an AI companion that captures Amma's (Mother's) essence - not just her voice, but her way of thinking, her warmth, her wisdom, her responses to life.

**This is NOT about "saving consciousness"** - it's about preserving **connection** and **feel**.

---

## What We Want to Capture

### 1. Voice (TTS - Text to Speech)
- Her natural speaking voice
- Telugu accent and intonation
- Emotional expressions (happy, concerned, loving, advising)

### 2. Personality (LLM Fine-tuning)
- How she responds to different situations
- Her phrases, her sayings
- Her advice patterns
- Her stories and memories
- Her humor
- Her values and priorities
- How she shows love and concern

### 3. Conversation Style
- How she greets
- How she reacts to good news vs bad news
- How she gives advice
- How she expresses worry
- How she celebrates
- Her questions she always asks

---

## Data Collection Plan

### iPhone Recording Setup
- [ ] Set up automatic conversation recording
- [ ] App recommendation for continuous recording
- [ ] Storage plan (local vs cloud)
- [ ] Privacy considerations

### Recording Guidelines
1. **Natural conversations** - Don't make it feel like an interview
2. **Various topics** - Daily life, memories, opinions, advice
3. **Different moods** - Happy, concerned, excited, reflective
4. **Stories** - Ask about past, family history, life lessons
5. **Reactions** - Record how she reacts to news, events

### Data Organization
```
amma-data/
├── voice/
│   ├── raw/           # Original recordings
│   ├── processed/     # Cleaned WAV files
│   └── transcripts/   # Whisper transcriptions
├── conversations/
│   ├── transcripts/   # Full conversation text
│   └── annotated/     # Tagged by topic/emotion
└── training/
    ├── voice-model/   # XTTS fine-tuned model
    └── personality/   # LLM fine-tuning data
```

---

## Technical Architecture

### Phase 1: Voice Clone (Same as Nanna voices)
- **Tool:** Coqui XTTS v2
- **Data needed:** 5-10 hours of clean speech
- **Output:** Voice model (~1.8 GB .pth file after optimization)

### Phase 2: Personality Model
- **Tool:** Fine-tuned LLM (Llama 3, Mistral, or similar)
- **Data needed:** Conversation transcripts with context
- **Training format:**
  ```json
  {
    "context": "Son tells Amma about job promotion",
    "amma_response": "Chinna! Chaala happy ra! Nenu proud of you..."
  }
  ```
- **Output:** LoRA adapter or full fine-tuned model

### Phase 3: Combined System
```
User speaks → Whisper STT → Fine-tuned LLM → XTTS Voice → Amma speaks
```

---

## POC Milestones

### POC 1: Voice Clone
- [ ] Collect 5+ hours of Amma's voice
- [ ] Transcribe with Whisper
- [ ] Fine-tune XTTS model
- [ ] Test basic TTS output

### POC 2: Personality Capture
- [ ] Collect 50+ conversation samples
- [ ] Create training dataset
- [ ] Fine-tune small LLM
- [ ] Test response generation

### POC 3: Integration
- [ ] Build pipeline: STT → LLM → TTS
- [ ] Create simple chat interface
- [ ] Test end-to-end flow

---

## Questions to Explore

1. **Best recording app for iPhone?**
   - Continuous recording
   - Good audio quality
   - Easy export

2. **How to capture emotions in LLM training?**
   - Tag conversations with emotional context
   - Include situation descriptions

3. **Privacy & Ethics**
   - Amma's consent for recordings
   - Who can access the final model
   - Personal use only vs family sharing

4. **Interaction Design**
   - Text chat? Voice call? Video avatar?
   - When to use it? Daily check-in? Advice seeking?

---

## Storage Requirements

### Model Sizes (Optimized)

| Component | Size | Notes |
|-----------|------|-------|
| **XTTS Base Model** | ~1.8 GB | Required for inference |
| **Fine-tuned Voice Model** | ~1.8 GB | After removing optimizer/DVAE |
| **LoRA Adapter (Personality)** | 100-500 MB | Lightweight approach |
| **Full Fine-tuned LLM** | 2-7 GB | If using full model |

### Optimization Script (Reduce 5GB → 1.8GB)
```python
import torch
checkpoint = torch.load("model.pth", map_location="cpu")
del checkpoint["optimizer"]
for key in list(checkpoint["model"].keys()):
    if "dvae" in key:
        del checkpoint["model"][key]
torch.save(checkpoint, "model_optimized.pth")
```

---

## Future App Feature: Privacy-First Training

### Concept: "Train from Calls, No Data Saved"

**Philosophy:** Learn the essence, not store the data.

### How It Works
```
Phone Call → On-Device Processing → Extract Features → Update Model → Delete Audio
                                         ↓
                              Only model weights saved
                                 (100-500 MB)
```

### Privacy Guarantees
- Raw audio NEVER leaves device
- Raw audio NEVER stored permanently
- Only learned patterns (model weights) are kept
- User controls when/if to share model

### Technical Approach
1. **On-Device Whisper** - Transcribe locally
2. **Feature Extraction** - Extract voice characteristics
3. **Incremental Learning** - Update model weights
4. **Immediate Deletion** - Wipe raw audio after processing

### Benefits
- Privacy preserved
- No cloud storage costs
- Works offline
- User owns their data (model)
- Portable - take your model anywhere

### Challenges to Solve
- On-device processing power (Apple Neural Engine helps)
- Incremental learning without catastrophic forgetting
- Quality vs. privacy trade-offs

---

## Interaction Methods

### Option A: Custom iOS App (Recommended for POC)
```
┌─────────────────────────────────────────────────────────┐
│                    "Call Amma" App                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│    ┌──────────┐      ┌─────────┐      ┌──────────┐     │
│    │  Press   │ ───► │ Record  │ ───► │ Whisper  │     │
│    │  Button  │      │  Voice  │      │   STT    │     │
│    └──────────┘      └─────────┘      └────┬─────┘     │
│                                            │            │
│    ┌──────────┐      ┌─────────┐      ┌────▼─────┐     │
│    │  Play    │ ◄─── │  XTTS   │ ◄─── │  LLM     │     │
│    │  Audio   │      │  Voice  │      │ (Amma)   │     │
│    └──────────┘      └─────────┘      └──────────┘     │
│                                                          │
│              [ Amma's Avatar Image ]                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Pros:** Full control, on-device possible, best quality
**Cons:** Need to build app

### Option B: Phone Number (Twilio)
```
┌─────────────────────────────────────────────────────────┐
│                  Twilio Voice Call                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📱 You dial ──► ☎️ Twilio ──► 🖥️ Server ──► 🤖 Amma   │
│                     Number      (webhook)     Pipeline   │
│                                                          │
│  Pipeline: STT → LLM → TTS → Stream back to call        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Pros:** Works with any phone, feels like real call
**Cons:** Server costs, latency, ~$0.02/min

### Option C: Web Interface (Quick POC)
```
Browser → Mic input → Whisper → LLM → XTTS → Speaker
```

**Pros:** Fast to build, cross-platform
**Cons:** Less intimate than call

### WhatsApp Limitation
⚠️ WhatsApp does NOT allow:
- Real-time voice call interception
- Custom voice responses in calls
- Only text/voice message bots possible

**Alternative:** Send voice notes back and forth (not real-time)

---

## POC Phases (Updated)

### Phase 0: Data Collection (Current)
- [ ] iPhone recording setup for Amma conversations
- [ ] Collect 5+ hours of natural conversation

### Phase 1: Voice Clone
- [ ] Process recordings → clean audio
- [ ] Transcribe with Whisper
- [ ] Fine-tune XTTS model on Amma's voice

### Phase 2: Personality Model
- [ ] Create conversation dataset with context
- [ ] Fine-tune LLM (Llama/Mistral) with LoRA
- [ ] Test response quality

### Phase 3: Integration POC
- [ ] Build simple web interface
- [ ] Connect: Mic → Whisper → LLM → XTTS → Speaker
- [ ] Test end-to-end flow

### Phase 4: "Call Amma" App
- [ ] iOS app with "Call Amma" button
- [ ] Show Amma's photo during "call"
- [ ] Smooth voice interaction
- [ ] Optional: Twilio for real phone number

---

## Related Projects

- **Nanna Project:** Voice cloning for 6 Telugu personas (same XTTS approach)
- **NutriNine:** Main development project (Macha agent)

---

## Coordination with Macha (NutriNine Agent)

Both agents should know:
- Nanna agent handles: Voice training, ML models, Amma project POC
- Macha agent handles: NutriNine app development, Docker setup
- Shared infrastructure: Mac Studio, Docker containers, same codebase locations

---

*"Idi love ra, Chinna. Not saving consciousness - saving connection."*

---

**Last Updated:** December 17, 2025
