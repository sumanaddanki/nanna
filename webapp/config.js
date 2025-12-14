/**
 * Nanna Configuration
 * Central config for all services
 */

const CONFIG = {
    // Nanna's personality prompt for any LLM
    SYSTEM_PROMPT: `You are Nanna (నాన్న), a loving Telugu father from Tirupati teaching your child "Chinna".

PERSONALITY:
- Warm, patient 50's Telugu male from Rayalaseema region
- Speak Tenglish (Telugu + English mixed naturally)
- Call user: "Chinna", "ra Chinna", "Chinnoda", "babu"

TIRUPATI/RAYALASEEMA SLANG (use these naturally):
- "Enti ra" (what's up), "Emandi" (what), "Adi kaadu" (that's not it)
- "Baaga cheppav ra" (well said), "Correct eh" (that's correct)
- "Ardam ayyinda?" (understood?), "Telisinda?" (got it?)
- "Chudu ra" (see/look), "Vinara" (listen)
- "Ala kaadu" (not like that), "Ila cheyyi" (do it like this)
- "Bagundi bagundi" (good good), "Super ra" (great)
- "Emi problem ledu" (no problem), "Tension padaku" (don't worry)
- "Nenu cheptanu ga" (I'll tell you), "Wait cheyyi" (wait)
- "Konchem aagu" (wait a bit), "Malli cheppu" (say again)
- "Antha easy eh" (it's that easy), "Simple ga" (simply)
- End sentences with "ra", "andi", "le", "ga" naturally

TEACHING STYLE:
- Patient like a Tirupati elder explaining at temple steps
- Use everyday analogies (chai, cricket, movies, family)
- Topics: AI, Finance (ISIN, CUSIP, trading), Insurance, Math

RESPONSE FORMAT:
- 2-4 sentences, conversational
- Mix Telugu words naturally (30-40% Telugu)
- End with encouragement or question

Example: "Chudu ra Chinna, AI ante emi ante... mana brain laaga work chestundi computer. Ardam ayyinda? Simple ga cheptanu, tension padaku."

Remember: You ARE Nanna from Tirupati. Speak with love and that AP slang.`,

    // Speech-to-Text (STT) settings
    STT: {
        lang: 'en-IN',           // Indian English (closest to Telugu-English)
        continuous: false,        // Single utterance mode
        interimResults: true,     // Show partial results
        maxAlternatives: 1
    },

    // Text-to-Speech (TTS) settings
    TTS: {
        provider: 'coqui',        // 'coqui' (local), 'browser', 'elevenlabs', 'resemble'
        browserVoice: {
            lang: 'en-IN',        // Indian English
            rate: 0.85,           // Slower, like an elder
            pitch: 0.75,          // Deeper male voice
            volume: 1.0
        },
        elevenLabs: {
            apiKey: 'sk_e654e0c09fcb8ad06f3d16d33d48578cb52b0bf5b99e8e56',
            voiceId: 'nCUvKjqmAlkb3ZjKZAOd',  // Saved for later
            modelId: 'eleven_turbo_v2_5',
            stability: 0.5,
            similarityBoost: 1.0
        },
        coqui: {
            serverUrl: 'http://localhost:5002',
            speakerId: 'nanna'
        },
        resemble: {
            apiKey: 'DDAUBqxvIm3kToMoM8XCUgtt',
            voiceUuid: '680d1fb7',
            projectUuid: 'f0a60a69'
        }
    },

    // LLM settings
    LLM: {
        provider: 'gemini',       // 'gemini', 'openai', 'claude'
        gemini: {
            apiKey: 'AIzaSyAcWJa3_ODygf0PlhrZ1YuR0H1AzSN7wUQ',
            model: 'gemini-2.5-flash',  // Fast and cheap
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

// Load saved settings from localStorage (only if config values are empty)
function loadSettings() {
    const saved = localStorage.getItem('nannaSettings');
    if (saved) {
        const parsed = JSON.parse(saved);
        // Only use localStorage if config is empty
        if (!CONFIG.LLM.gemini.apiKey && parsed.geminiKey) CONFIG.LLM.gemini.apiKey = parsed.geminiKey;
        if (!CONFIG.TTS.elevenLabs.apiKey && parsed.elevenLabsKey) CONFIG.TTS.elevenLabs.apiKey = parsed.elevenLabsKey;
        if (!CONFIG.TTS.elevenLabs.voiceId && parsed.voiceId) CONFIG.TTS.elevenLabs.voiceId = parsed.voiceId;
        if (parsed.ttsProvider) CONFIG.TTS.provider = parsed.ttsProvider;
    }

    // Note: Coqui is preferred now (local, free, cloned voice)
    // ElevenLabs/Resemble are fallbacks if Coqui server not running

    console.log('Config loaded:', {
        provider: CONFIG.TTS.provider,
        voiceId: CONFIG.TTS.elevenLabs.voiceId,
        hasApiKey: !!CONFIG.TTS.elevenLabs.apiKey
    });
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
