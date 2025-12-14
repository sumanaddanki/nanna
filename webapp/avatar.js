/**
 * Avatar Animation Engine
 * Swaps expression images based on audio analysis and text emotion
 * Low-bandwidth solution - no video API needed!
 */

class AvatarAnimator {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        this.currentExpression = 'neutral';
        this.isAnimating = false;
        this.animationInterval = null;

        // Expression images - preload for smooth animation
        this.expressions = {
            neutral: 'expressions/neutral.jpg',
            slight_open: 'expressions/slight_open.jpg',
            mouth_closed: 'expressions/mouth_closed_mm.jpg',
            mouth_round: 'expressions/mouth_round_oh.jpg',
            mouth_open: 'expressions/mouth_open_ah.jpg',
            smile: 'expressions/big_smile.jpg'
        };

        // Phoneme to expression mapping
        this.phonemeMap = {
            // Closed mouth sounds
            'M': 'mouth_closed', 'B': 'mouth_closed', 'P': 'mouth_closed',
            // Round sounds
            'O': 'mouth_round', 'U': 'mouth_round', 'W': 'mouth_round',
            // Open sounds
            'A': 'mouth_open', 'E': 'mouth_open', 'I': 'slight_open',
            // Default
            'default': 'slight_open'
        };

        // Emotion keywords for expression selection
        this.emotionKeywords = {
            smile: ['happy', 'great', 'wonderful', 'excellent', 'proud', 'good job', 'well done', 'chinna', 'haha', 'nice', 'correct', 'right', 'bagundi', 'super'],
            mouth_open: ['wow', 'amazing', 'incredible', 'surprised', 'really', 'arre']
        };

        this.preloadedImages = {};
        this.init();
    }

    async init() {
        // Create image element
        this.imgElement = document.createElement('img');
        this.imgElement.className = 'avatar-image';
        this.imgElement.alt = 'Nanna Avatar';
        this.container.appendChild(this.imgElement);

        // Preload all expressions
        await this.preloadImages();

        // Set initial expression
        this.setExpression('neutral');

        console.log('Avatar initialized with', Object.keys(this.expressions).length, 'expressions');
    }

    async preloadImages() {
        const promises = Object.entries(this.expressions).map(([name, src]) => {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    this.preloadedImages[name] = img;
                    resolve();
                };
                img.onerror = () => {
                    console.warn(`Failed to load: ${src}`);
                    resolve();
                };
                img.src = src;
            });
        });

        await Promise.all(promises);
        console.log('Preloaded', Object.keys(this.preloadedImages).length, 'images');
    }

    setExpression(expression) {
        if (this.expressions[expression] && this.currentExpression !== expression) {
            this.currentExpression = expression;
            this.imgElement.src = this.expressions[expression];
        }
    }

    /**
     * Detect emotion from text and return appropriate expression
     */
    detectEmotion(text) {
        const lowerText = text.toLowerCase();

        for (const [emotion, keywords] of Object.entries(this.emotionKeywords)) {
            for (const keyword of keywords) {
                if (lowerText.includes(keyword)) {
                    return emotion;
                }
            }
        }

        return null; // No specific emotion detected
    }

    /**
     * Simple phoneme detection from text
     * Maps characters to mouth shapes
     */
    getPhonemeSequence(text) {
        const sequence = [];
        const vowels = 'AEIOU';
        const upperText = text.toUpperCase();

        for (let i = 0; i < upperText.length; i++) {
            const char = upperText[i];

            if (this.phonemeMap[char]) {
                sequence.push(this.phonemeMap[char]);
            } else if (vowels.includes(char)) {
                sequence.push('slight_open');
            } else if (char === ' ') {
                sequence.push('neutral');
            }
        }

        return sequence;
    }

    /**
     * Animate avatar while speaking
     * @param {string} text - The text being spoken
     * @param {number} duration - Total duration in ms
     */
    animateSpeaking(text, duration) {
        if (this.isAnimating) {
            this.stopAnimation();
        }

        this.isAnimating = true;

        // Detect overall emotion
        const emotion = this.detectEmotion(text);

        // Get phoneme sequence
        const phonemes = this.getPhonemeSequence(text);

        if (phonemes.length === 0) {
            // No phonemes, just show emotion or slight talking
            this.setExpression(emotion || 'slight_open');
            setTimeout(() => {
                this.setExpression(emotion || 'neutral');
                this.isAnimating = false;
            }, duration);
            return;
        }

        // Calculate timing
        const frameTime = Math.max(80, duration / phonemes.length); // Min 80ms per frame
        let frameIndex = 0;

        // Start animation loop
        this.animationInterval = setInterval(() => {
            if (frameIndex >= phonemes.length) {
                this.stopAnimation();
                // End with emotion or neutral
                this.setExpression(emotion || 'neutral');
                return;
            }

            // Occasionally show emotion expression
            if (emotion && Math.random() < 0.15) {
                this.setExpression(emotion);
            } else {
                this.setExpression(phonemes[frameIndex]);
            }

            frameIndex++;
        }, frameTime);
    }

    /**
     * Animate with audio analysis (Web Audio API)
     * More accurate lip-sync based on actual audio
     */
    animateWithAudio(audioElement) {
        if (!window.AudioContext) {
            console.warn('Web Audio API not supported');
            return;
        }

        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaElementSource(audioElement);

        source.connect(analyser);
        analyser.connect(audioContext.destination);

        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        this.isAnimating = true;

        const animate = () => {
            if (!this.isAnimating) return;

            analyser.getByteFrequencyData(dataArray);

            // Calculate average volume
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;

            // Map volume to expression
            if (average < 10) {
                this.setExpression('neutral');
            } else if (average < 40) {
                this.setExpression('mouth_closed');
            } else if (average < 80) {
                this.setExpression('slight_open');
            } else if (average < 120) {
                this.setExpression('mouth_round');
            } else {
                this.setExpression('mouth_open');
            }

            requestAnimationFrame(animate);
        };

        animate();

        // Stop when audio ends
        audioElement.addEventListener('ended', () => {
            this.stopAnimation();
            this.setExpression('neutral');
        });
    }

    /**
     * Simple talking animation without text analysis
     * Good for TTS where we don't have timing info
     */
    startTalkingAnimation(emotion = null) {
        if (this.isAnimating) return;

        this.isAnimating = true;
        const talkingExpressions = ['slight_open', 'mouth_closed', 'mouth_round', 'slight_open', 'mouth_open'];
        let index = 0;

        this.animationInterval = setInterval(() => {
            // Mix in emotion occasionally
            if (emotion && Math.random() < 0.2) {
                this.setExpression(emotion);
            } else {
                this.setExpression(talkingExpressions[index % talkingExpressions.length]);
            }
            index++;
        }, 120); // ~8 fps for natural look
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
            this.animationInterval = null;
        }
    }

    /**
     * Set expression based on text emotion (for responses)
     */
    showEmotion(text) {
        const emotion = this.detectEmotion(text);
        if (emotion) {
            this.setExpression(emotion);
        }
    }

    /**
     * Thinking animation while waiting for response
     */
    startThinking() {
        this.setExpression('thinking');
    }

    /**
     * Return to neutral
     */
    reset() {
        this.stopAnimation();
        this.setExpression('neutral');
    }
}

// Export for use in app.js
window.AvatarAnimator = AvatarAnimator;
