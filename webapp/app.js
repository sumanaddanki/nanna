/**
 * Nanna App - Main Controller
 * Connects STT → LLM → TTS
 */

class NannaApp {
    constructor() {
        // Elements
        this.avatar = document.getElementById('avatar');
        this.speakingRing = document.getElementById('speaking-ring');
        this.statusEl = document.getElementById('status');
        this.chatDisplay = document.getElementById('chat-display');
        this.textInput = document.getElementById('text-input');
        this.micBtn = document.getElementById('mic-btn');
        this.debugEl = document.getElementById('debug');

        // Settings elements
        this.geminiKeyInput = document.getElementById('gemini-key');
        this.ttsProviderSelect = document.getElementById('tts-provider');
        this.elevenLabsKeyInput = document.getElementById('elevenlabs-key');
        this.voiceIdInput = document.getElementById('voice-id');
        this.debugToggle = document.getElementById('debug-toggle');
        this.sttStatusIndicator = document.getElementById('stt-status');

        // State
        this.isProcessing = false;

        this.init();
    }

    init() {
        this.setupSTT();
        this.setupTTS();
        this.setupEventListeners();
        this.loadSettings();
        this.updateSTTStatus();

        debug('App: Initialized');
    }

    setupSTT() {
        // When speech is recognized
        stt.onResult = (text) => {
            this.handleUserInput(text);
        };

        // Show interim (partial) results
        stt.onInterim = (text) => {
            this.textInput.value = text;
            this.textInput.style.opacity = '0.6';
        };

        // Listening started
        stt.onStart = () => {
            this.setStatus('Listening...', 'listening');
            this.micBtn.classList.add('recording');
        };

        // Listening ended
        stt.onEnd = () => {
            this.micBtn.classList.remove('recording');
            this.textInput.style.opacity = '1';
            if (!this.isProcessing) {
                this.setStatus('Click mic or type to talk');
            }
        };

        // Error
        stt.onError = (message) => {
            this.setStatus(message);
            this.micBtn.classList.remove('recording');
        };
    }

    setupTTS() {
        tts.onStart = () => {
            this.setStatus('Nanna speaking...', 'speaking');
            this.speakingRing.classList.add('active');
        };

        tts.onEnd = () => {
            this.speakingRing.classList.remove('active');
            this.isProcessing = false;
            this.setStatus('Click mic or type to talk');
        };
    }

    setupEventListeners() {
        // Mic button - push to talk
        this.micBtn.addEventListener('mousedown', () => this.startListening());
        this.micBtn.addEventListener('mouseup', () => this.stopListening());
        this.micBtn.addEventListener('mouseleave', () => this.stopListening());

        // Touch support for mobile
        this.micBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startListening();
        });
        this.micBtn.addEventListener('touchend', () => this.stopListening());

        // Text input
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.textInput.value.trim()) {
                this.handleUserInput(this.textInput.value.trim());
                this.textInput.value = '';
            }
        });

        // Settings
        this.geminiKeyInput.addEventListener('change', () => this.saveSettingsToConfig());
        this.ttsProviderSelect.addEventListener('change', () => this.saveSettingsToConfig());
        this.elevenLabsKeyInput.addEventListener('change', () => this.saveSettingsToConfig());
        this.voiceIdInput.addEventListener('change', () => this.saveSettingsToConfig());

        this.debugToggle.addEventListener('change', () => {
            CONFIG.UI.showDebug = this.debugToggle.checked;
            this.debugEl.classList.toggle('visible', this.debugToggle.checked);
        });
    }

    loadSettings() {
        // Load saved values into inputs
        this.geminiKeyInput.value = CONFIG.LLM.gemini.apiKey || '';
        this.ttsProviderSelect.value = CONFIG.TTS.provider;
        this.elevenLabsKeyInput.value = CONFIG.TTS.elevenLabs.apiKey || '';
        this.voiceIdInput.value = CONFIG.TTS.elevenLabs.voiceId || '';
    }

    saveSettingsToConfig() {
        CONFIG.LLM.gemini.apiKey = this.geminiKeyInput.value;
        CONFIG.TTS.provider = this.ttsProviderSelect.value;
        CONFIG.TTS.elevenLabs.apiKey = this.elevenLabsKeyInput.value;
        CONFIG.TTS.elevenLabs.voiceId = this.voiceIdInput.value;

        saveSettings();
        debug('Settings saved');
    }

    updateSTTStatus() {
        const status = stt.getStatus();
        this.sttStatusIndicator.classList.toggle('connected', status.supported);
        this.sttStatusIndicator.classList.toggle('disconnected', !status.supported);
    }

    startListening() {
        if (this.isProcessing) return;
        stt.start();
    }

    stopListening() {
        stt.stop();
    }

    async handleUserInput(text) {
        if (this.isProcessing || !text) return;

        this.isProcessing = true;
        this.textInput.value = '';

        // Add user message to chat
        this.addMessage('user', text);

        // Show thinking status
        this.setStatus('Nanna thinking...', 'thinking');

        try {
            // Get response from LLM
            const response = await llm.chat(text);

            // Add Nanna's response to chat
            this.addMessage('nanna', response);

            // Speak the response
            if (CONFIG.UI.autoSpeak) {
                await tts.speak(response);
            } else {
                this.isProcessing = false;
                this.setStatus('Click mic or type to talk');
            }

        } catch (error) {
            this.setStatus(`Error: ${error.message}`);
            this.addMessage('nanna', `Chinna, something went wrong ra. ${error.message}`);
            this.isProcessing = false;
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const labelDiv = document.createElement('div');
        labelDiv.className = 'label';
        labelDiv.textContent = sender === 'nanna' ? 'Nanna' : 'Chinna';

        messageDiv.appendChild(labelDiv);
        messageDiv.appendChild(document.createTextNode(text));

        this.chatDisplay.appendChild(messageDiv);
        this.chatDisplay.scrollTop = this.chatDisplay.scrollHeight;
    }

    setStatus(text, type = '') {
        this.statusEl.textContent = text;
        this.statusEl.className = 'status ' + type;
    }
}

// Start app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NannaApp();
});
