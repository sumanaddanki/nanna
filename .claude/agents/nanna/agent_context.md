# Nanna Agent Context

## Current State
- **Status:** Active
- **Last Updated:** 2025-12-14
- **Version:** 1.0

## User Profile
- **Name:** Chinna (Suman Addanke)
- **Relationship:** Son (figuratively)
- **Learning Style:** Hands-on, practical

## Project Context

### Voice Training (Phase 1 Complete)
| Voice | Region | Hours | Status |
|-------|--------|-------|--------|
| Arjun | Urban/Hyderabad | 6.47h | Ready |
| Ravi | Rayalaseema | 5.38h | Ready |
| Lakshmi | Rayalaseema | 5.03h | Ready |
| Kiran | Krishna/Godavari | 5.35h | Ready |
| Priya | Krishna/Godavari | 5.55h | Ready |
| Ananya | Urban/Hyderabad | 6.14h | Ready |

**Total:** 33.92 hours collected

### Hardware
- **MacBook Air M2:** Voice collection (current)
- **Mac Studio M4 Max:** Training (arriving tomorrow)
- **NAS US:** DS225+ (home)
- **NAS India:** DS923+ (dev/QA)

### Architecture
- Multi-region: US + India
- Data residency: +91 → India, +1 → US
- TTS served from regional NAS

## Learning Progress
- Topics covered: TBD
- Quiz scores: TBD
- Current streak: TBD

## Session Memory
- Last session: 2025-12-14
- Topics discussed: Voice training, NAS architecture, Mac Studio, DS923+ NAS
- Next planned: Mac Studio setup, voice model training

---

## Next Session TODO (IMPORTANT - READ FIRST!)

**When user returns, IMMEDIATELY ask:**
1. "Mac Studio arrive ayyinda, Chinna?" (Did Mac Studio arrive?)
2. Get Mac Studio details (hostname, username, IP)
3. Help copy 5.2GB voice files from MacBook Air to Mac Studio

---

## Source Machine (MacBook Air - CURRENT)

| Property | Value |
|----------|-------|
| **Model** | MacBook Air M2 (Mac14,2) |
| **Serial** | XQVFY6V256 |
| **Hostname** | Mac |
| **Username** | sumanaddanke |
| **Location** | US (Home) |
| **OS** | macOS (Darwin 25.1.0) |
| **RAM** | 8GB |
| **Git Repo** | `/Users/sumanaddanke/git/nanna/` |
| **Voice Data** | `/Users/sumanaddanke/git/nanna/tools/voices/processed/` |
| **Voice Size** | 5.2GB (6 voices, 33.92 hours) |

### Voice Files on MacBook:
```
/Users/sumanaddanke/git/nanna/tools/voices/processed/
├── arjun/    (6.47h)
├── ravi/     (5.38h)
├── lakshmi/  (5.03h)
├── kiran/    (5.35h)
├── priya/    (5.55h)
└── ananya/   (6.14h)
```

---

## Target Machine (Mac Studio - ARRIVING TOMORROW)

| Property | Value |
|----------|-------|
| **Model** | Mac Studio M4 Max |
| **RAM** | 36GB |
| **GPU** | 32-core |
| **Storage** | 512GB SSD |
| **Price** | $1,999 |
| **Hostname** | TBD (ask user) |
| **Username** | TBD (ask user) |
| **IP Address** | TBD (find on same network) |

---

## Transfer Plan

### Step 1: Get Mac Studio Details
```bash
# On Mac Studio, run:
hostname
whoami
ipconfig getifaddr en0
```

### Step 2: Transfer Voice Files (5.2GB)
```bash
# Option A: AirDrop (easiest)
# Open Finder → AirDrop → drag voices/processed/

# Option B: scp (if same WiFi)
scp -r /Users/sumanaddanke/git/nanna/tools/voices/processed/ [user]@[mac-studio-ip]:~/nanna/voices/

# Option C: USB Drive
# Copy to USB → plug into Mac Studio
```

### Step 3: Setup Mac Studio
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Clone repo
git clone [repo-url] ~/nanna

# Install TTS
pip3.11 install TTS torch torchaudio

# Copy voice files to repo
cp -r ~/nanna/voices/ ~/nanna/tools/voices/processed/
```

### Step 4: Start Training
```bash
cd ~/nanna/tools
# Training commands TBD
```

---

## Network Discovery Commands
```bash
# Find Mac Studio on network (run from MacBook):
ping mac-studio.local
arp -a | grep -i "mac"
dns-sd -B _afpovertcp._tcp
```
