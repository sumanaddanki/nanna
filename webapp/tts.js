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
        console.log('TTS PROVIDER:', provider);
        console.log('TTS CONFIG:', CONFIG.TTS);
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
                case 'resemble':
                    await this.speakResemble(text);
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
            console.log('TTS: Starting browser speech...');
            console.log('TTS: Text:', text);

            // Cancel any ongoing speech
            this.synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Apply settings
            const settings = CONFIG.TTS.browserVoice;
            console.log('TTS: Settings:', settings);

            utterance.rate = settings.rate;
            utterance.pitch = settings.pitch;
            utterance.volume = settings.volume;
            utterance.lang = settings.lang;

            // Try to find a male voice or Indian English voice
            const voices = this.synth.getVoices();
            console.log('TTS: Available voices:', voices.length);

            // Prefer male voices
            let selectedVoice = voices.find(v => v.name.toLowerCase().includes('male') && v.lang.startsWith('en'));
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang.includes('IN'));
            }
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang.startsWith('en'));
            }

            if (selectedVoice) {
                utterance.voice = selectedVoice;
                console.log('TTS: Selected voice:', selectedVoice.name, selectedVoice.lang);
            } else {
                console.log('TTS: Using default voice');
            }

            utterance.onstart = () => {
                console.log('TTS: Speech started');
            };

            utterance.onend = () => {
                console.log('TTS: Speech ended');
                this.isSpeaking = false;
                if (this.onEnd) this.onEnd();
                resolve();
            };

            utterance.onerror = (event) => {
                console.error('TTS Error:', event.error);
                this.isSpeaking = false;
                if (this.onEnd) this.onEnd();
                reject(new Error(event.error));
            };

            console.log('TTS: Calling synth.speak()');
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
     * Resemble.ai TTS (Voice Cloning)
     * Creates a clip and plays it
     */
    async speakResemble(text) {
        const settings = CONFIG.TTS.resemble;

        if (!settings.apiKey) {
            throw new Error('Resemble API key not set');
        }

        if (!settings.voiceUuid || !settings.projectUuid) {
            throw new Error('Resemble Voice/Project UUID not set');
        }

        // Use local proxy to bypass CORS
        const url = '/api/resemble';

        console.log('Resemble: Creating clip via proxy...');

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Resemble error:', errorText);
            throw new Error('Resemble API error: ' + response.status);
        }

        const data = await response.json();
        console.log('Resemble response:', data);

        // Check if audio URL is available
        if (data.item && data.item.audio_src) {
            return this.playAudio(data.item.audio_src);
        } else if (data.item && data.item.uuid) {
            // Audio not ready yet, need to poll
            return this.pollResembleClip(data.item.uuid);
        } else {
            throw new Error('No audio returned from Resemble');
        }
    }

    /**
     * Poll for Resemble clip to be ready
     */
    async pollResembleClip(clipUuid, maxAttempts = 30) {
        const settings = CONFIG.TTS.resemble;
        const url = `https://app.resemble.ai/api/v2/projects/${settings.projectUuid}/clips/${clipUuid}`;

        for (let i = 0; i < maxAttempts; i++) {
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Token token=${settings.apiKey}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.item && data.item.audio_src) {
                    console.log('Resemble: Audio ready!');
                    return this.playAudio(data.item.audio_src);
                }
            }
        }

        throw new Error('Resemble audio generation timed out');
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
                voice: settings.speakerId,
                language: 'hi'  // Hindi closest to Telugu
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
