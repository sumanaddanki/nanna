# Nutrinine Telugu Voice Library Plan

## Base Voices (6 Pre-built, FREE for users)

| ID | Default Name | Region | Age | Gender | Style |
|----|--------------|--------|-----|--------|-------|
| 1 | **Ravi** | Rayalaseema | 40s | Male | Wise elder, patient teacher |
| 2 | **Lakshmi** | Rayalaseema | 40s | Female | Caring mother, gentle guide |
| 3 | **Kiran** | Krishna/Godavari | 20s | Male | Friendly brother, casual mentor |
| 4 | **Priya** | Krishna/Godavari | 20s | Female | Supportive sister, energetic |
| 5 | **Arjun** | Urban/Hyderabad | 20s | Male | Modern tech buddy, cool |
| 6 | **Ananya** | Urban/Hyderabad | 20s | Female | Modern peer, professional |

## User Customization

- Users can **rename** any voice (e.g., "Ravi" → "Nanna", "Dad", "తాత")
- Users can **upload photo** for avatar
- Users can **record voice** for personalization (premium)

## Regional Accent Characteristics

### Rayalaseema (Tirupati, Kadapa, Anantapur)
- Softer consonants
- Distinctive "aa" sounds
- Common expressions: "enti ra", "bagundi", "ardam ayyinda"
- Slower, more deliberate speech

### Krishna/Godavari (Vijayawada, Guntur, Rajahmundry)
- Clearer pronunciation
- Slightly faster speech
- Common expressions: "em chestunnav", "super ra"
- Mix of formal and casual

### Urban/Hyderabad
- Heavy English mixing (Tenglish)
- Faster speech
- Common expressions: "chill bro", "cool ga"
- Modern slang

## Voice Training Pipeline

```
Source Data:
├── YouTube Telugu channels (news, vlogs)
├── Regional movie dialogues
├── User recordings (with consent)
└── Text-to-speech datasets

Processing:
├── Audio extraction (ffmpeg)
├── Transcription (Whisper)
├── Emotion labeling
└── Quality filtering

Training:
├── Base model: Coqui XTTS v2
├── Fine-tuning per region
└── ~5-10 hours audio per voice
```

## Expression → Emotion Database

| Telugu Expression | Emotion | Context |
|-------------------|---------|---------|
| "deni talli" | frustrated/surprised | Exclamation |
| "bagundi ra" | happy/approval | Praise |
| "enti ra" | curious/casual | Question |
| "arey babu" | concern/affection | Calling |
| "super" | excited/impressed | Approval |
| "correct eh" | agreement | Confirmation |

## Pricing Model

| Tier | Voice Features | Price |
|------|----------------|-------|
| FREE | 6 pre-built voices, browser TTS backup | ₹0 |
| BASIC | Voice selection + custom name | ₹99/month |
| PREMIUM | Record & train personal voice | ₹299/month |
| FAMILY | Clone loved one's voice | ₹499 setup + ₹199/month |

## Technical Stack

- **TTS Engine**: Coqui XTTS v2 (local, free)
- **Training**: PyTorch on Mac (GPU optional)
- **Storage**: Local → Synology NAS (future)
- **API**: Flask/FastAPI for voice generation
- **Frontend**: React Native (mobile app)
