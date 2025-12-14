# Nanna Avatar POC

## Overview
Progressive avatar system for Nanna - starts with voice-enabled animation, evolves to AI-generated video.

## Evolution Roadmap

### Phase 1: Static Avatar + Text-to-Speech (Current)
- Simple animated avatar (CSS/SVG)
- Web Speech API for voice
- Telugu-accented English TTS
- Expression states (happy, thinking, teaching)

### Phase 2: Animated Avatar
- Lip-sync animation
- More expression variety
- Gesture animations
- Better voice synthesis (ElevenLabs/Azure)

### Phase 3: AI Video Avatar
- HeyGen / D-ID / Synthesia integration
- Real-time video generation
- Natural expressions and movements

## Tech Stack (Phase 1)

### Frontend
- HTML5 + CSS3 (animations)
- Vanilla JS (keep it simple)
- Web Speech API (SpeechSynthesis)
- Optional: Three.js for 3D avatar

### Backend (for future phases)
- Node.js / Python
- WebSocket for real-time
- Claude API for responses
- Voice synthesis API

## Files
- `index.html` - Main avatar interface
- `styles.css` - Avatar styling and animations
- `avatar.js` - Avatar logic and voice
- `nanna-voice.js` - Voice synthesis config

## Voice Configuration
```javascript
// Telugu-accented English voice settings
const nannaVoice = {
  lang: 'en-IN',  // Indian English (closest to Telugu accent)
  rate: 0.9,      // Slightly slower, fatherly pace
  pitch: 0.9,     // Deeper, male voice
  volume: 1.0
};
```

## Expression States
- `neutral` - Default, listening
- `happy` - When Chinna answers correctly
- `thinking` - Processing, formulating response
- `teaching` - Explaining concepts
- `proud` - When Chinna makes progress
- `encouraging` - When Chinna struggles

## Getting Started
1. Open `index.html` in browser
2. Allow microphone (for future voice input)
3. Interact with Nanna!

## Future Integrations
- Synology NAS deployment
- Email notification system
- Progress tracking database
- Spaced repetition scheduler
