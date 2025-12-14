/**
 * Nanna Voice Configuration
 * Text-to-Speech settings for Telugu-accented English
 */

class NannaVoice {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voice = null;
        this.settings = {
            rate: 0.9,      // Slightly slower, thoughtful pace
            pitch: 0.85,    // Deeper, fatherly voice
            volume: 1.0
        };
        this.isReady = false;
        this.init();
    }

    init() {
        // Wait for voices to load
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.loadVoices();
        }
        // Try loading immediately as well
        this.loadVoices();
    }

    loadVoices() {
        const voices = this.synth.getVoices();

        // Priority order for voice selection (Telugu-like accent)
        const preferredVoices = [
            'hi-IN',    // Hindi (closest to Telugu accent available)
            'en-IN',    // Indian English
            'en-GB',    // British (fallback)
            'en-US'     // American (last resort)
        ];

        // Try to find the best matching voice
        for (const langPref of preferredVoices) {
            const found = voices.find(v =>
                v.lang.startsWith(langPref) &&
                v.name.toLowerCase().includes('male')
            );
            if (found) {
                this.voice = found;
                break;
            }
        }

        // Fallback to any Indian voice
        if (!this.voice) {
            this.voice = voices.find(v => v.lang.includes('IN')) ||
                         voices.find(v => v.lang.startsWith('en')) ||
                         voices[0];
        }

        this.isReady = true;
        console.log('Nanna voice loaded:', this.voice?.name || 'default');
    }

    /**
     * Speak text with Nanna's voice
     * @param {string} text - Text to speak
     * @param {function} onStart - Callback when speech starts
     * @param {function} onEnd - Callback when speech ends
     */
    speak(text, onStart, onEnd) {
        if (!this.synth || !text) return;

        // Cancel any ongoing speech
        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        if (this.voice) {
            utterance.voice = this.voice;
        }

        utterance.rate = this.settings.rate;
        utterance.pitch = this.settings.pitch;
        utterance.volume = this.settings.volume;

        // Add natural pauses for Telugu-style speech
        // Replace common pauses
        utterance.text = this.addNaturalPauses(text);

        utterance.onstart = () => {
            if (onStart) onStart();
        };

        utterance.onend = () => {
            if (onEnd) onEnd();
        };

        utterance.onerror = (event) => {
            console.error('Speech error:', event);
            if (onEnd) onEnd();
        };

        this.synth.speak(utterance);
    }

    /**
     * Add natural pauses for more authentic speech
     */
    addNaturalPauses(text) {
        // Add pauses after Telugu words/phrases
        const teluguPhrases = [
            'Chinna',
            'ra',
            'babu',
            'Ardam ayyinda',
            'Baaga',
            'Correct',
            'Nanna'
        ];

        let processed = text;
        teluguPhrases.forEach(phrase => {
            processed = processed.replace(
                new RegExp(`(${phrase}[,.]?)`, 'gi'),
                '$1 '
            );
        });

        return processed;
    }

    /**
     * Stop speaking
     */
    stop() {
        if (this.synth) {
            this.synth.cancel();
        }
    }

    /**
     * Check if currently speaking
     */
    isSpeaking() {
        return this.synth?.speaking || false;
    }

    /**
     * Update voice settings
     */
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
    }

    /**
     * Get available voices for debugging
     */
    getAvailableVoices() {
        return this.synth.getVoices().map(v => ({
            name: v.name,
            lang: v.lang
        }));
    }
}

// Telugu phrases Nanna uses
const NANNA_PHRASES = {
    greetings: [
        "Chinna, ela unnav?",
        "Ra Chinna, welcome back!",
        "Babu, ready for learning?"
    ],
    encouragement: [
        "Baaga cheppav, Chinna!",
        "Excellent ra!",
        "Nenu proud ga feel avthunna!",
        "Keep going, babu!"
    ],
    wrong_answer: [
        "Close, but not quite ra.",
        "Malli try chey, Chinna.",
        "Koncham more think chey.",
        "Not correct, but no problem!"
    ],
    transitions: [
        "Now, Chinna, next topic...",
        "Okay ra, moving on...",
        "Idi chaala important...",
        "Listen carefully ra..."
    ],
    farewells: [
        "Good job today, Chinna!",
        "Baaga nerchukunnav ra!",
        "See you next time, babu.",
        "Keep learning, proud of you!"
    ]
};

// Export for use in avatar.js
window.NannaVoice = NannaVoice;
window.NANNA_PHRASES = NANNA_PHRASES;
