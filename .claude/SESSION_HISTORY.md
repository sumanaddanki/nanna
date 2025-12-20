# Nanna Project - Session History

This file tracks conversation history, plans, and pending tasks so Nanna remembers across sessions.

---

## Session: 2025-12-17 (Continued)

### Completed Today (Session 2):

#### Amma POC Recording Setup on Mac Air - COMPLETE!
Setup WhatsApp call recording environment:

| Component | Status | Details |
|-----------|--------|---------|
| BlackHole 2ch | ✅ Installed | Virtual audio device |
| Audacity | ✅ Installed | Manual recording option |
| Sox | ✅ Installed | Command-line recording |
| Aggregate Device | ✅ Configured | Mic + BlackHole for recording |
| Multi-Output Device | ✅ Configured | Speakers + BlackHole for hearing |
| Auto-Recorder Script | ✅ Created | Detects WhatsApp calls automatically |
| Python venv | ✅ Setup | Whisper + PyAudio + NumPy |

**Files Created on Mac Air (`~/git/sumanaddanki/amma-poc/`):**
- `auto_record_calls.py` - Auto-detects WhatsApp calls and records
- `start_auto_recorder.sh` - Easy launcher script
- `process_recording.py` - Convert + transcribe recordings
- `COMPLETE_SETUP_GUIDE.md` - Full setup documentation
- `SETUP_BLACKHOLE.md` - Audio device configuration

**How Auto-Recording Works:**
1. Monitors WhatsApp CPU usage (call = ~15-30% vs chat = ~2-5%)
2. Detects audio activity (mic + system audio)
3. When both active → starts recording
4. After 15s silence → stops and saves
5. Files saved to `voice/raw/whatsapp_call_YYYYMMDD_HHMMSS.wav`

**Next Steps for Amma POC:**
- [ ] Test auto-recorder with a real WhatsApp call
- [ ] Build speaker diarization script (separate Amma's voice from yours)
- [ ] Label voice folders after separation
- [ ] Train XTTS on Amma's voice only

---

### Completed Today (Session 1):

#### Voice Transcription (Whisper large-v3)
- Transcribed all 6 voices using OpenAI Whisper large-v3 model
- Transcripts saved to `tools/voices/transcripts/`
- Ready for XTTS fine-tuning

#### Mac Studio Docker Setup - COMPLETE!
All containers running on Mac Studio M4 Max:

| Container | Port | Status |
|-----------|------|--------|
| **DEV Environment** | | |
| a2vibecreators-dev | 16000 | Running |
| nutrinine-dev | 16001 | Running |
| postgres-dev | 16200 | Running |
| **QA Environment** | | |
| a2vibecreators-qa | 17000 | Running |
| nutrinine-qa | 17001 | Running |
| postgres-qa | 17200 | Running |
| **PROD Environment** | | |
| a2vibecreators-prod | 18000 | Running |
| nutrinine-prod | 18001 | Running |
| postgres-prod | 18200 | Running |
| **Reverse Proxy** | | |
| caddy | 80/443 | Running |

**Port Allocation Scheme:**
- DEV: 16xxx (websites: 16000-16099, APIs: 16100-16199, DBs: 16200-16299)
- QA: 17xxx (websites: 17000-17099, APIs: 17100-17199, DBs: 17200-17299)
- PROD: 18xxx (websites: 18000-18099, APIs: 18100-18199, DBs: 18200-18299)

**Files Created:**
- `/Users/semostudio/docker/docker-compose.yml` - Main Docker config
- `/Users/semostudio/docker/caddy/Caddyfile` - Reverse proxy config
- Placeholder HTML files for all environments

**Code Pulled:**
- nutrinine repo with all submodules (web, backend, database, android, ios)
- Located at `~/git/a2vibecreators/nutrinine/`

#### NEW: Amma Project Started
- Created `AMMA_PROJECT.md` - POC plan to capture Amma's voice + personality
- Goal: Not just voice clone, but capture her way of thinking and responding
- Phases: Voice Clone (XTTS) → Personality (LLM fine-tune) → Combined System
- Data needed: 5+ hours voice recordings + conversation transcripts

### Pending / To Do Next:

**Voice Training (Nanna Voices):**
1. Complete transcription for remaining voices (Arjun in progress, need Ananya podcast4, Kiran podcast3-4, Ravi, Lakshmi)
2. Fine-tune all 6 voice models with XTTS

**Amma Project POC:**
3. Research iPhone recording apps for continuous conversation capture
4. Start collecting Amma voice data when ready

**Infrastructure:**
5. Update router/DNS - Point domains to Mac Studio
6. Stop Synology containers (LAST step after DNS update)

---

## Agent Coordination

| Agent | Project | Responsibilities |
|-------|---------|------------------|
| **Nanna** | nanna (this repo) | Voice training, ML models, Amma POC |
| **Macha** | nutrinine | App development, Docker, backend |

**Shared Infrastructure:**
- Mac Studio M4 Max (192.168.1.196)
- Docker containers at `/Users/semostudio/docker/`
- NutriNine code at `~/git/a2vibecreators/nutrinine/`

**Communication:** Both agents read each other's SESSION_HISTORY files

---

## Session: 2025-12-16

### Completed:
- Created Nanna agent (`.claude/agents/nanna.md`)
- Renamed all slash commands with `nanna` prefix:
  - `/nanna-init`, `/nannaLearn`, `/nannaQuiz`, `/nannaQuizRandom`
  - `/nannaExplore`, `/nannaRevise`, `/nannaProgress`, `/nannaTopics`
- Deleted old command files

### Previous Tasks:

#### 🎤 6 Voices Training Plan
**Status:** Studio ready! Training can begin.

**Voice Data Collected (33.92 hours total):**
| Voice | Region | Hours | Status |
|-------|--------|-------|--------|
| Arjun | Urban/Hyderabad | 6.47h | Ready |
| Ravi | Rayalaseema | 5.38h | Ready |
| Lakshmi | Rayalaseema | 5.03h | Ready |
| Kiran | Krishna/Godavari | 5.35h | Ready |
| Priya | Krishna/Godavari | 5.55h | Ready |
| Ananya | Urban/Hyderabad | 6.14h | Ready |

**Source:** YouTube audio → converted to WAV → stored on Synology NAS

**Training Plan:**
1. Mac Studio/Mini → Train with Coqui XTTS v2
2. Each model ~1.5GB output (.pth file)
3. Deploy to NAS for serving
4. Phone app streams audio from NAS

**Synology NAS:**
- IP: 192.168.1.183
- SSH Port: 17183 (NOT default 22!)
- User: aauser
- SSH Key: Configured ✅
- Voices folder: `/volume1/homes/aauser/voices/`
- SSH Command: `ssh -p 17183 aauser@192.168.1.183`

**Reference:** See `/Users/semostudio/git/a2vibecreators/nutrinine/.claudeagent/DEPLOYMENT_ARCHITECTURE.md` for full NAS details

---

**Voice Files Location:** `tools/voices/processed/` (in this project!)

| Voice | Size | Path |
|-------|------|------|
| Arjun | 1.0G | `tools/voices/processed/arjun/` |
| Ananya | 962M | `tools/voices/processed/ananya/` |
| Priya | 882M | `tools/voices/processed/priya/` |
| Kiran | 849M | `tools/voices/processed/kiran/` |
| Ravi | 834M | `tools/voices/processed/ravi/` |
| Lakshmi | 800M | `tools/voices/processed/lakshmi/` |

**Total:** ~5.3GB of processed WAV files (23 files)

---

## Previous Sessions:

### Session: [Date Unknown - Before Dec 2024]
- Downloaded 5+ hours of Telugu audio from YouTube
- Converted to WAV format
- Identified 6 voice personas from different Telugu regions
- Was waiting for Mac Studio/Mini to arrive for training

---

## Project Notes:

### Synology NAS Access (IMPORTANT!)
```bash
# SSH into NAS (port 17183, NOT 22!)
ssh -p 17183 aauser@192.168.1.183

# View available shares
ls /volume1/homes/

# Voices folder location
/volume1/homes/aauser/voices/
```

### Voice Cloning Setup
- **Primary:** Coqui XTTS v2 (self-hosted, free, Telugu support)
- **Backup:** ElevenLabs (10k chars/month free)
- **Alternative:** PlayHT (Telugu accent support)

### Current Webapp Features:
- STT (Speech-to-Text) - Web Speech API
- TTS (Text-to-Speech) - Multiple providers
- LLM integration (Gemini/OpenAI)
- Voice cloning guide: `webapp/VOICE_CLONING_GUIDE.md`

### Related Projects:
- NutriNine NAS setup: `/Users/semostudio/git/a2vibecreators/nutrinine/.claudeagent/DEPLOYMENT_ARCHITECTURE.md`
- Same Synology NAS used for both projects

---

### Training Machine Specs
- **Machine:** Mac Studio
- **Chip:** Apple M4 Max (14 cores: 10 performance + 4 efficiency)
- **RAM:** 36 GB
- **Training Plan:** See `tools/VOICE_TRAINING_PLAN.md`

---

*Last updated: 2025-12-17*
