/**
 * Text-to-Speech Module
 * Supports multiple providers:
 * 1. Browser (Free) - Web Speech API
 * 2. ElevenLabs - Voice cloning
 * 3. Coqui - Local/Self-hosted voice cloning
 */

class TextToSpeech {
    constructor() {
        this.synth = window.speechSynthesis;
        this.isSpeaking = false;
        this.audioElement = null;
        this.onStart = null;
        this.onEnd = null;

        this.init();
    }

    init() {
        // Create audio element for API-based TTS
        this.audioElement = new Audio();
        this.audioElement.addEventListener('ended', () => {
            this.isSpeaking = false;
            if (this.onEnd) this.onEnd();
        });
        this.audioElement.addEventListener('error', (e) => {
            debug(`TTS Audio Error: ${e.message}`);
            this.isSpeaking = false;
            if (this.onEnd) this.onEnd();
        });

        debug('TTS: Initialized');
    }

    /**
     * Speak text using configured provider
     * @param {string} text - Text to speak
     */
    async speak(text) {
        if (!text) return;

        const provider = CONFIG.TTS.provider;
        debug(`TTS: Speaking with ${provider}: "${text.substring(0, 50)}..."`);

        this.isSpeaking = true;
        if (this.onStart) this.onStart();

        try {
            switch (provider) {
                case 'browser':
                    await this.speakBrowser(text);
                    break;
                case 'elevenlabs':
                    await this.speakElevenLabs(text);
                    break;
                case 'coqui':
                    await this.speakCoqui(text);
                    break;
                default:
                    await this.speakBrowser(text);
            }
        } catch (error) {
            debug(`TTS Error: ${error.message}`);
            this.isSpeaking = false;
            if (this.onEnd) this.onEnd();
            // Fallback to browser
            if (provider !== 'browser') {
                debug('TTS: Falling back to browser');
                await this.speakBrowser(text);
            }
        }
    }

    /**
     * Browser-based TTS (Free)
     */
    speakBrowser(text) {
        return new Promise((resolve, reject) => {
            // Cancel any ongoing speech
            this.synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Apply settings
            const settings = CONFIG.TTS.browserVoice;
            utterance.rate = settings.rate;
            utterance.pitch = settings.pitch;
            utterance.volume = settings.volume;
            utterance.lang = settings.lang;

            // Try to find Indian English voice
            const voices = this.synth.getVoices();
            const indianVoice = voices.find(v => v.lang.includes('IN')) ||
                               voices.find(v => v.lang.startsWith('en'));
            if (indianVoice) {
                utterance.voice = indianVoice;
            }

            utterance.onend = () => {
                this.isSpeaking = false;
                if (this.onEnd) this.onEnd();
                resolve();
            };

            utterance.onerror = (event) => {
                this.isSpeaking = false;
                if (this.onEnd) this.onEnd();
                reject(new Error(event.error));
            };

            this.synth.speak(utterance);
        });
    }

    /**
     * ElevenLabs TTS (Voice Cloning)
     * Uses your cloned Nanna voice
     */
    async speakElevenLabs(text) {
        const settings = CONFIG.TTS.elevenLabs;

        if (!settings.apiKey) {
            throw new Error('ElevenLabs API key not set');
        }

        if (!settings.voiceId) {
            throw new Error('Voice ID not set. Clone your voice first.');
        }

        const url = `https://api.elevenlabs.io/v1/text-to-speech/${settings.voiceId}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'xi-api-key': settings.apiKey
            },
            body: JSON.stringify({
                text: text,
                model_id: settings.modelId,
                voice_settings: {
                    stability: settings.stability,
                    similarity_boost: settings.similarityBoost
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || 'ElevenLabs API error');
        }

        // Get audio blob
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Play audio
        return this.playAudio(audioUrl);
    }

    /**
     * Coqui TTS (Local/Self-hosted)
     * Requires running Coqui server locally
     */
    async speakCoqui(text) {
        const settings = CONFIG.TTS.coqui;
        const url = `${settings.serverUrl}/api/tts`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                speaker_id: settings.speakerId
            })
        });

        if (!response.ok) {
            throw new Error('Coqui TTS server error');
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        return this.playAudio(audioUrl);
    }

    /**
     * Play audio from URL
     */
    playAudio(url) {
        return new Promise((resolve, reject) => {
            this.audioElement.src = url;

            this.audioElement.onended = () => {
                this.isSpeaking = false;
                if (this.onEnd) this.onEnd();
                URL.revokeObjectURL(url);
                resolve();
            };

            this.audioElement.onerror = (e) => {
                this.isSpeaking = false;
                URL.revokeObjectURL(url);
                reject(new Error('Audio playback error'));
            };

            this.audioElement.play().catch(reject);
        });
    }

    /**
     * Stop speaking
     */
    stop() {
        // Stop browser TTS
        this.synth.cancel();

        // Stop audio element
        if (this.audioElement) {
            this.audioElement.pause();
            this.audioElement.currentTime = 0;
        }

        this.isSpeaking = false;
        if (this.onEnd) this.onEnd();
    }

    /**
     * Get available browser voices (for debugging)
     */
    getVoices() {
        return this.synth.getVoices().map(v => ({
            name: v.name,
            lang: v.lang
        }));
    }
}

// Create global instance
const tts = new TextToSpeech();

/* ============================================
   VOICE CLONING GUIDE
   ============================================

   To use your Nanna's voice recording:

   OPTION 1: ElevenLabs (Recommended for quality)
   ----------------------------------------------
   1. Go to https://elevenlabs.io
   2. Create account (free tier: 10k chars/month)
   3. Go to "Voice Lab" > "Add Generative or Cloned Voice"
   4. Choose "Instant Voice Cloning"
   5. Upload your nanna.wav file (1-5 min of clear speech)
   6. Name it "Nanna"
   7. Copy the Voice ID
   8. Add API key and Voice ID in Settings

   OPTION 2: Coqui XTTS (Free, Self-hosted)
   ----------------------------------------
   1. Install: pip install TTS
   2. Run server: tts-server --model_name tts_models/multilingual/multi-dataset/xtts_v2
   3. Use API to clone voice with your audio file
   4. Set server URL in settings

   AUDIO PREPARATION TIPS:
   - Extract just Nanna's voice (remove your voice if overlapping)
   - Remove background noise (use Audacity)
   - Normalize audio levels
   - Ideal: 3-5 minutes of clear speech
   - Multiple samples of different emotions help

============================================ */
