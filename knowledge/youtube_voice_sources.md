# Telugu Voice Collection Sources

## Recommended Channels (Clear Audio)

### Telugu Tech Channels (Male Voices - Urban/Modern)
1. **Telugu Tech Office** - @telugutechoffice - Clear tutorials
2. **Telugu Tech Pro** - Tech reviews in Telugu
3. **Tech Vivek Telugu** - 399K subs, since 2015
4. **Telugu Tech Pad** - Tech guides

### Rayalaseema Region (Tirupati, Kadapa, Anantapur)
**For Ravi/Lakshmi voices**

#### News/Talk Channels
1. **TV5 News** - Rayalaseema reporters
2. **Sakshi TV** - Regional coverage
3. **ABN Andhrajyothy** - Tirupati bureau

#### Vlogs/Podcasts
1. **Asha Sudarsan** - Rayalaseema vlogger from Tirupati
2. **Tirupati Darshini** - Temple tours
3. **Rayalaseema Kathalu** - Local stories

### Characteristics to capture:
- Softer consonants
- Extended "aa" sounds
- Slower speech pace
- Expressions: "enti ra", "bagundi", "ardam ayyinda"

---

## Krishna/Godavari Region (Vijayawada, Guntur, Rajahmundry)

### News/Talk Channels
1. **Etv Andhra Pradesh**
2. **NTV Telugu**
3. **iNews**

### Vlogs/Podcasts
1. **Telugu Tech Tuts** - Tech in Telugu
2. **Vennela Kishore** (comedy clips)
3. **Guntur channel local vlogs**

### Characteristics to capture:
- Clearer pronunciation
- Slightly faster speech
- Mix formal/casual
- Expressions: "em chestunnav", "super ra"

---

## Urban/Hyderabad

### News/Talk Channels
1. **T News**
2. **V6 News**

### Vlogs/Podcasts/Creators
1. **My Village Show** (Gangavva clips)
2. **Sumantv** - Interviews
3. **Tech talks in Tenglish**

### Characteristics to capture:
- Heavy English mixing (Tenglish)
- Faster speech
- Modern slang
- Expressions: "chill bro", "cool ga"

---

## Voice Collection Pipeline

```
1. Identify channels with clear audio
2. Download videos (yt-dlp)
3. Extract audio (ffmpeg)
4. Separate speakers (pyannote)
5. Transcribe (Whisper)
6. Label emotions
7. Quality filter (SNR, clarity)
8. Create training dataset

Tools needed:
- yt-dlp: Video download
- ffmpeg: Audio extraction
- whisper: Transcription
- pyannote: Speaker diarization
- librosa: Audio analysis
```

## Target: 5-10 hours per voice

| Voice | Region | Hours Needed | Status |
|-------|--------|--------------|--------|
| Ravi | Rayalaseema | 5h | Pending |
| Lakshmi | Rayalaseema | 5h | Pending |
| Kiran | Krishna | 5h | Pending |
| Priya | Krishna | 5h | Pending |
| Arjun | Urban | 5h | Pending |
| Ananya | Urban | 5h | Pending |

## Next Steps
1. Create YouTube scraping script
2. Set up speaker diarization
3. Build transcription pipeline
4. Start with Rayalaseema male voice (Ravi)
