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

        // Avatar animator
        this.avatarAnimator = null;

        this.init();
    }

    init() {
        this.setupSTT();
        this.setupTTS();
        this.setupAvatar();
        this.setupEventListeners();
        this.loadSettings();
        this.updateSTTStatus();

        debug('App: Initialized');
    }

    setupAvatar() {
        // Initialize avatar animator with expression images
        if (window.AvatarAnimator) {
            this.avatarAnimator = new AvatarAnimator('#avatar');
            debug('Avatar: Animator initialized');
        } else {
            debug('Avatar: AvatarAnimator not loaded');
        }
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

            // Start avatar talking animation
            if (this.avatarAnimator && this.currentResponse) {
                const emotion = this.avatarAnimator.detectEmotion(this.currentResponse);
                this.avatarAnimator.startTalkingAnimation(emotion);
            }
        };

        tts.onEnd = () => {
            this.speakingRing.classList.remove('active');
            this.isProcessing = false;
            this.setStatus('Click mic or type to talk');

            // Stop avatar animation and return to neutral/smile
            if (this.avatarAnimator) {
                this.avatarAnimator.stopAnimation();
                // Show smile briefly if response was positive
                if (this.currentResponse && this.avatarAnimator.detectEmotion(this.currentResponse) === 'smile') {
                    this.avatarAnimator.setExpression('smile');
                    setTimeout(() => this.avatarAnimator.setExpression('neutral'), 2000);
                } else {
                    this.avatarAnimator.setExpression('neutral');
                }
            }
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

        // Test voice button
        document.getElementById('test-voice-btn').addEventListener('click', () => {
            tts.speak("Ra Chinna, nenu Nanna. Test successful!");
        });

        // Voice pitch slider
        const pitchSlider = document.getElementById('voice-pitch');
        const pitchValue = document.getElementById('pitch-value');
        pitchSlider.addEventListener('input', () => {
            const val = parseFloat(pitchSlider.value);
            pitchValue.textContent = val;
            CONFIG.TTS.browserVoice.pitch = val;
        });

        // Voice rate slider
        const rateSlider = document.getElementById('voice-rate');
        const rateValue = document.getElementById('rate-value');
        rateSlider.addEventListener('input', () => {
            const val = parseFloat(rateSlider.value);
            rateValue.textContent = val;
            CONFIG.TTS.browserVoice.rate = val;
        });

        // Voice file upload
        const voiceUpload = document.getElementById('voice-upload');
        const uploadStatus = document.getElementById('upload-status');
        const voicePreview = document.getElementById('voice-preview');
        const cloneBtn = document.getElementById('clone-voice-btn');

        voiceUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                uploadStatus.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;

                // Create preview
                const url = URL.createObjectURL(file);
                voicePreview.src = url;
                voicePreview.style.display = 'block';

                // Enable clone button if ElevenLabs key exists
                cloneBtn.disabled = !CONFIG.TTS.elevenLabs.apiKey;

                // Store file for later
                window.nannaVoiceFile = file;
            }
        });

        // Clone voice button
        cloneBtn.addEventListener('click', async () => {
            if (!window.nannaVoiceFile) {
                alert('Please upload a voice file first');
                return;
            }
            if (!CONFIG.TTS.elevenLabs.apiKey) {
                alert('Please add your ElevenLabs API key in Settings first');
                return;
            }

            cloneBtn.textContent = 'Cloning... Please wait';
            cloneBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('name', 'Nanna');
                formData.append('files', window.nannaVoiceFile);
                formData.append('description', 'Voice of Nanna - Telugu father figure');

                const response = await fetch('https://api.elevenlabs.io/v1/voices/add', {
                    method: 'POST',
                    headers: {
                        'xi-api-key': CONFIG.TTS.elevenLabs.apiKey
                    },
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail?.message || 'Clone failed');
                }

                const data = await response.json();

                // Save voice ID
                CONFIG.TTS.elevenLabs.voiceId = data.voice_id;
                document.getElementById('voice-id').value = data.voice_id;
                saveSettings();

                alert(`Voice cloned successfully! Voice ID: ${data.voice_id}`);
                cloneBtn.textContent = '✓ Voice Cloned!';

                // Switch to ElevenLabs
                document.getElementById('tts-provider').value = 'elevenlabs';
                CONFIG.TTS.provider = 'elevenlabs';
                saveSettings();

            } catch (error) {
                alert(`Error: ${error.message}`);
                cloneBtn.textContent = 'Clone Voice with ElevenLabs';
                cloneBtn.disabled = false;
            }
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

        console.log('handleUserInput called with:', text);
        console.log('Gemini API key:', CONFIG.LLM.gemini.apiKey ? 'SET' : 'NOT SET');

        this.isProcessing = true;
        this.textInput.value = '';

        // Add user message to chat
        this.addMessage('user', text);

        // Show thinking status
        this.setStatus('Nanna thinking...', 'thinking');

        // Show neutral expression while thinking
        if (this.avatarAnimator) {
            this.avatarAnimator.setExpression('neutral');
        }

        try {
            // Get response from LLM
            console.log('Calling LLM...');
            const response = await llm.chat(text);
            console.log('LLM response:', response);

            // Store response for avatar animation
            this.currentResponse = response;

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
