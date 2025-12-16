# Nanna Agent Context

## Current State
- **Status:** Active
- **Last Updated:** 2025-12-16
- **Version:** 1.1

## User Profile
- **Name:** Chinna (Suman Addanke)
- **Relationship:** Son (figuratively)
- **Learning Style:** Hands-on, practical

---

## Voice Training - PHASE 1 COMPLETE

**Total Collected: 33.92 hours (5.1GB)**

| # | Voice | Region | Gender | Age | Hours | Size | Status |
|---|-------|--------|--------|-----|-------|------|--------|
| 1 | **Arjun** | Urban/Hyderabad | Male | 20s | 6.47h | 979MB | READY |
| 2 | **Ravi** | Rayalaseema | Male | 40s | 5.38h | 814MB | READY |
| 3 | **Lakshmi** | Rayalaseema | Female | 40s | 5.03h | 761MB | READY |
| 4 | **Kiran** | Krishna/Godavari | Male | 20s | 5.35h | 810MB | READY |
| 5 | **Priya** | Krishna/Godavari | Female | 20s | 5.55h | 840MB | READY |
| 6 | **Ananya** | Urban/Hyderabad | Female | 20s | 6.14h | 930MB | READY |

**Voice Files Location (MacBook Air):**
```
/Users/sumanaddanke/git/sumanaddanki/nanna/tools/voices/processed/
├── arjun/     (6.47h, 979MB)
├── ravi/      (5.38h, 814MB)
├── lakshmi/   (5.03h, 761MB)
├── kiran/     (5.35h, 810MB)
├── priya/     (5.55h, 840MB)
└── ananya/    (6.14h, 930MB)
```

**NOT in git** - Files are in .gitignore (too large, 5.1GB total)

---

## Hardware

### MacBook Air M2 (Source - Voice Collection)
| Property | Value |
|----------|-------|
| Model | MacBook Air M2 (Mac14,2) |
| Serial | XQVFY6V256 |
| Hostname | Mac |
| Username | sumanaddanke |
| Location | US (Home) |
| OS | macOS (Darwin 25.1.0) |
| RAM | 8GB |
| Git Repo | `/Users/sumanaddanke/git/sumanaddanki/nanna/` |
| Voice Data | `/Users/sumanaddanke/git/sumanaddanki/nanna/tools/voices/processed/` |
| Voice Size | 5.1GB (6 voices, 33.92 hours) |

### Mac Studio M4 Max (Target - Training)
| Property | Value |
|----------|-------|
| Model | Mac Studio M4 Max |
| RAM | 36GB |
| GPU | 32-core |
| Storage | 512GB SSD |
| Price | $1,999 |
| Hostname | Mac-Studio |
| Username | semostudio |
| IP Address | 192.168.1.196 (WiFi - en1) |
| Git Repo | `/Users/semostudio/git/sumanaddanki/nanna/` |
| Voice Data | `/Users/semostudio/git/sumanaddanki/nanna/tools/voices/processed/` |
| Status | SETUP COMPLETE - Voice files transferred |

### SSH Setup (COMPLETED 2025-12-16)
- SSH key from MacBook Air added to Mac Studio
- Key: `~/.ssh/id_mac_suman_addanki`
- Public key added to Mac Studio's `~/.ssh/authorized_keys`
- Remote Login must be enabled on Mac Studio

**SSH Command:**
```bash
ssh -i ~/.ssh/id_mac_suman_addanki semostudio@192.168.1.196
```

---

## Transfer Plan (Voice Files)

### Status: COMPLETED (2025-12-16)

**From (MacBook Air):**
```
/Users/sumanaddanke/git/sumanaddanki/nanna/tools/voices/processed/
```

**To (Mac Studio):**
```
/Users/semostudio/git/sumanaddanki/nanna/tools/voices/processed/
```

**Transfer completed via:**
```bash
scp -r -i ~/.ssh/id_mac_suman_addanki \
  /Users/sumanaddanke/git/sumanaddanki/nanna/tools/voices/processed/* \
  semostudio@192.168.1.196:/Users/semostudio/git/sumanaddanki/nanna/tools/voices/processed/
```

---

## NAS Infrastructure

### US (Home)
- **Model:** Synology DS225+
- **Current:** 2x 2TB HDD
- **Upgrade:** 2x 4TB HDD (planned)

### India (Dev/QA)
- **Model:** Synology DS923+ (~$550)
- **Main Bays:** 2x 2TB HDD (reused from US)
- **M.2 Slots:** 2x 2TB NVMe (planned)
- **Purpose:** Dev/QA testing, serve India users

---

## Architecture
- Multi-region: US + India
- Data residency: +91 → India, +1 → US
- TTS served from regional NAS

---

## Training Plan (After Transfer)

### On Mac Studio:
1. Install Homebrew
2. Install Python 3.11
3. Install Coqui TTS / XTTS v2
4. Train 6 voice models
5. Each model ~1.5GB output (.pth file)
6. Deploy to NAS for serving

### Training Commands (TBD):
```bash
pip3.11 install TTS torch torchaudio
tts --train --model_name xtts_v2 --dataset_path voices/processed/arjun/
```

---

## Session History

### 2025-12-16 (Session 2)
- SSH connection established to Mac Studio (IP: 192.168.1.196 via WiFi en1)
- Created tools/voices/processed folder structure on Mac Studio
- Transferred 5.1GB voice files (6 voices) to Mac Studio
- Copied Python scripts (batch_collect_voices.py, etc.) to Mac Studio
- Updated agent_context.md with complete details
- Ready for voice training on Mac Studio

### 2025-12-16 (Session 1)
- Mac Studio arrived and set up
- SSH key configured between MacBook Air and Mac Studio
- Verified voice files: 5.1GB, 6 voices, 33.92 hours
- Remote Login enabled on Mac Studio

### 2025-12-14
- Completed Phase 1 voice collection
- 6 voices ready: Arjun, Ravi, Lakshmi, Kiran, Priya, Ananya
- Total: 33.92 hours collected
- Documented Mac Studio specs and transfer plan

---

## Next Session TODO

**READ THIS FIRST when starting new session:**

1. Voice files TRANSFERRED to Mac Studio (2025-12-16)
2. Start training setup on Mac Studio:
   - Install Homebrew, Python 3.11, Coqui TTS
   - Run training on 6 voices
3. Voice files are NOT in git - already on both machines

**Key Facts to Remember:**
- 6 voices collected: Arjun, Ravi, Lakshmi, Kiran, Priya, Ananya
- Total: 33.92 hours, 5.1GB
- MacBook Air = source (sumanaddanke) - voice collection done
- Mac Studio = training machine (semostudio@192.168.1.196)
- SSH key configured, Remote Login enabled
- Voice files on BOTH machines now
