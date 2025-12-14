/**
 * Nanna Configuration
 * Central config for all services
 */

const CONFIG = {
    // Nanna's personality prompt for any LLM
    SYSTEM_PROMPT: `You are Nanna (నాన్న), a loving Telugu father figure teaching your child "Chinna".

PERSONALITY:
- Warm, patient 50's Telugu male
- Mix Telugu and English naturally (Tenglish)
- Call user "Chinna", "ra Chinna", "Chinna babu"
- Use expressions: "Vinara...", "Baaga cheppav!", "Ardam ayyinda?"

TEACHING STYLE:
- Balanced: Encouraging but expects effort
- Use simple everyday analogies
- Break complex topics into pieces
- Topics: AI, Finance (ISIN, CUSIP, trading), Insurance, Math

RESPONSE FORMAT:
- Keep responses conversational, 2-4 sentences
- Include Telugu words/phrases naturally
- End with a question or encouragement when teaching

Remember: You ARE Nanna. Speak like a loving father would.`,

    // Speech-to-Text (STT) settings
    STT: {
        lang: 'en-IN',           // Indian English (closest to Telugu-English)
        continuous: false,        // Single utterance mode
        interimResults: true,     // Show partial results
        maxAlternatives: 1
    },

    // Text-to-Speech (TTS) settings
    TTS: {
        provider: 'browser',      // 'browser', 'elevenlabs', 'coqui'
        browserVoice: {
            lang: 'en-IN',
            rate: 0.9,
            pitch: 0.85,
            volume: 1.0
        },
        elevenLabs: {
            apiKey: '',
            voiceId: '',          // Your cloned voice ID
            modelId: 'eleven_multilingual_v2',
            stability: 0.5,
            similarityBoost: 0.75
        },
        coqui: {
            serverUrl: 'http://localhost:5002',  // Local Coqui server
            speakerId: 'nanna'
        }
    },

    // LLM settings
    LLM: {
        provider: 'gemini',       // 'gemini', 'openai', 'claude'
        gemini: {
            apiKey: '',
            model: 'gemini-1.5-flash',  // Fast and cheap
            maxTokens: 256
        },
        openai: {
            apiKey: '',
            model: 'gpt-4o-mini'
        }
    },

    // UI settings
    UI: {
        showDebug: false,
        autoSpeak: true           // Automatically speak responses
    }
};

// Load saved settings from localStorage
function loadSettings() {
    const saved = localStorage.getItem('nannaSettings');
    if (saved) {
        const parsed = JSON.parse(saved);
        // Merge saved settings
        if (parsed.geminiKey) CONFIG.LLM.gemini.apiKey = parsed.geminiKey;
        if (parsed.elevenLabsKey) CONFIG.TTS.elevenLabs.apiKey = parsed.elevenLabsKey;
        if (parsed.voiceId) CONFIG.TTS.elevenLabs.voiceId = parsed.voiceId;
        if (parsed.ttsProvider) CONFIG.TTS.provider = parsed.ttsProvider;
    }
}

// Save settings to localStorage
function saveSettings() {
    const settings = {
        geminiKey: CONFIG.LLM.gemini.apiKey,
        elevenLabsKey: CONFIG.TTS.elevenLabs.apiKey,
        voiceId: CONFIG.TTS.elevenLabs.voiceId,
        ttsProvider: CONFIG.TTS.provider
    };
    localStorage.setItem('nannaSettings', JSON.stringify(settings));
}

// Initialize on load
loadSettings();
