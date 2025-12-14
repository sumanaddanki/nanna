/**
 * Speech-to-Text Module
 * Uses Web Speech API (FREE - powered by Google)
 *
 * This code works with ANY backend (Gemini, OpenAI, Claude, etc.)
 * It just converts your voice to text locally in the browser.
 */

class SpeechToText {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.onResult = null;      // Callback when speech is recognized
        this.onInterim = null;     // Callback for partial results
        this.onStart = null;       // Callback when listening starts
        this.onEnd = null;         // Callback when listening ends
        this.onError = null;       // Callback for errors

        this.init();
    }

    init() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error('Speech Recognition not supported in this browser');
            this.isSupported = false;
            return;
        }

        this.isSupported = true;
        this.recognition = new SpeechRecognition();

        // Configure from settings
        this.recognition.lang = CONFIG.STT.lang;
        this.recognition.continuous = CONFIG.STT.continuous;
        this.recognition.interimResults = CONFIG.STT.interimResults;
        this.recognition.maxAlternatives = CONFIG.STT.maxAlternatives;

        // Event handlers
        this.recognition.onstart = () => {
            this.isListening = true;
            debug('STT: Started listening');
            if (this.onStart) this.onStart();
        };

        this.recognition.onend = () => {
            this.isListening = false;
            debug('STT: Stopped listening');
            if (this.onEnd) this.onEnd();
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show interim results (what you're saying in real-time)
            if (interimTranscript && this.onInterim) {
                this.onInterim(interimTranscript);
            }

            // Final result - send this to LLM
            if (finalTranscript) {
                debug(`STT: Final transcript: "${finalTranscript}"`);
                if (this.onResult) {
                    this.onResult(finalTranscript.trim());
                }
            }
        };

        this.recognition.onerror = (event) => {
            debug(`STT Error: ${event.error}`);
            this.isListening = false;

            const errorMessages = {
                'no-speech': 'No speech detected. Try again.',
                'audio-capture': 'Microphone not found.',
                'not-allowed': 'Microphone permission denied.',
                'network': 'Network error. Check connection.',
                'aborted': 'Listening stopped.',
                'language-not-supported': 'Language not supported.'
            };

            const message = errorMessages[event.error] || `Error: ${event.error}`;
            if (this.onError) this.onError(message);
        };

        this.recognition.onspeechend = () => {
            debug('STT: Speech ended');
        };

        debug('STT: Initialized successfully');
    }

    /**
     * Start listening for speech
     */
    start() {
        if (!this.isSupported) {
            if (this.onError) this.onError('Speech recognition not supported');
            return false;
        }

        if (this.isListening) {
            debug('STT: Already listening');
            return true;
        }

        try {
            this.recognition.start();
            return true;
        } catch (e) {
            debug(`STT: Start error - ${e.message}`);
            return false;
        }
    }

    /**
     * Stop listening
     */
    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    /**
     * Abort listening (cancel without result)
     */
    abort() {
        if (this.recognition) {
            this.recognition.abort();
        }
    }

    /**
     * Change language
     * @param {string} lang - Language code (e.g., 'en-IN', 'te-IN', 'en-US')
     */
    setLanguage(lang) {
        if (this.recognition) {
            this.recognition.lang = lang;
            debug(`STT: Language set to ${lang}`);
        }
    }

    /**
     * Get supported status
     */
    getStatus() {
        return {
            supported: this.isSupported,
            listening: this.isListening,
            language: this.recognition?.lang
        };
    }
}

// Debug helper
function debug(msg) {
    if (CONFIG.UI.showDebug) {
        console.log(msg);
        const debugEl = document.getElementById('debug');
        if (debugEl) {
            debugEl.innerHTML += msg + '<br>';
            debugEl.scrollTop = debugEl.scrollHeight;
        }
    }
}

// Create global instance
const stt = new SpeechToText();
