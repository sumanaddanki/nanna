/**
 * Nanna Avatar - Main Application Logic
 * Handles chat, avatar expressions, and voice interactions
 */

class NannaAvatar {
    constructor() {
        // Elements
        this.avatar = document.getElementById('avatar');
        this.expressionBadge = document.getElementById('expression-badge');
        this.speakingIndicator = document.getElementById('speaking-indicator');
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.voiceBtn = document.getElementById('voice-btn');
        this.voiceEnabled = document.getElementById('voice-enabled');
        this.voiceSpeed = document.getElementById('voice-speed');
        this.topicSelector = document.getElementById('topic-selector');

        // State
        this.currentMode = null; // 'learn', 'quiz', 'explore'
        this.currentTopic = null;
        this.isListening = false;
        this.recognition = null;

        // Voice
        this.voice = new NannaVoice();

        // Initialize
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.greet();
    }

    setupEventListeners() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Voice button
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceInput());

        // Voice speed
        this.voiceSpeed.addEventListener('input', (e) => {
            this.voice.updateSettings({ rate: parseFloat(e.target.value) });
        });

        // Quick actions
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleAction(e.target.dataset.action);
            });
        });

        // Topic buttons
        document.querySelectorAll('.topic-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectTopic(e.target.dataset.topic);
            });
        });
    }

    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-IN'; // Indian English

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.userInput.value = transcript;
                this.sendMessage();
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.voiceBtn.classList.remove('recording');
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
                this.voiceBtn.classList.remove('recording');
            };
        }
    }

    toggleVoiceInput() {
        if (!this.recognition) {
            this.addMessage('nanna', 'Voice input not supported in this browser, Chinna. Please type instead.');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            this.voiceBtn.classList.remove('recording');
        } else {
            this.recognition.start();
            this.isListening = true;
            this.voiceBtn.classList.add('recording');
        }
    }

    greet() {
        const greetings = [
            "Ra Chinna, ela unnav? Nanna here! Ready to learn something new today?",
            "Chinna babu! Welcome! What would you like to explore - AI, Finance, Insurance, or Math?",
            "Hello Chinna! Nenu ready, nuvvu ready? Let's learn together!"
        ];
        const greeting = greetings[Math.floor(Math.random() * greetings.length)];

        setTimeout(() => {
            this.addMessage('nanna', greeting);
            this.speak(greeting);
        }, 500);
    }

    sendMessage() {
        const text = this.userInput.value.trim();
        if (!text) return;

        this.addMessage('user', text);
        this.userInput.value = '';

        // Process the message
        this.processMessage(text);
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const senderLabel = document.createElement('div');
        senderLabel.className = 'sender';
        senderLabel.textContent = sender === 'nanna' ? 'నాన్న Nanna' : 'Chinna';

        const textDiv = document.createElement('div');
        textDiv.className = 'text';
        textDiv.textContent = text;

        messageDiv.appendChild(senderLabel);
        messageDiv.appendChild(textDiv);
        this.chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    processMessage(text) {
        const lowerText = text.toLowerCase();

        // Set thinking expression while processing
        this.setExpression('thinking');

        // Simulate processing delay
        setTimeout(() => {
            let response;

            // Check for keywords
            if (lowerText.includes('learn') || lowerText.includes('teach')) {
                this.handleAction('learn');
                return;
            } else if (lowerText.includes('quiz') || lowerText.includes('test')) {
                this.handleAction('quiz');
                return;
            } else if (lowerText.includes('progress')) {
                response = this.getProgressResponse();
            } else if (this.currentMode === 'quiz') {
                response = this.handleQuizAnswer(text);
            } else {
                response = this.getGeneralResponse(text);
            }

            this.addMessage('nanna', response);
            this.speak(response);
            this.setExpression('happy');
        }, 500);
    }

    handleAction(action) {
        this.currentMode = action;

        switch (action) {
            case 'learn':
                this.topicSelector.style.display = 'block';
                this.addMessage('nanna', 'Edi nerchukovalanukuntunnav, Chinna? Select a topic below!');
                this.speak('What would you like to learn, Chinna?');
                break;

            case 'quiz':
                this.topicSelector.style.display = 'block';
                this.addMessage('nanna', 'Quiz time, Chinna! Select a topic and let\'s test your knowledge!');
                this.speak('Quiz time! Select a topic, Chinna!');
                break;

            case 'explore':
                this.topicSelector.style.display = 'none';
                const exploreResponse = this.getExploreContent();
                this.addMessage('nanna', exploreResponse);
                this.speak(exploreResponse);
                break;

            case 'progress':
                this.topicSelector.style.display = 'none';
                const progressResponse = this.getProgressResponse();
                this.addMessage('nanna', progressResponse);
                this.speak(progressResponse);
                break;
        }
    }

    selectTopic(topic) {
        this.currentTopic = topic;
        this.topicSelector.style.display = 'none';

        const topicNames = {
            ai: 'AI & Machine Learning',
            finance: 'Finance & Trading',
            insurance: 'Insurance',
            math: 'Mathematics'
        };

        if (this.currentMode === 'learn') {
            const response = `Okay Chinna, let's learn about ${topicNames[topic]}! ${this.getLearningContent(topic)}`;
            this.addMessage('nanna', response);
            this.speak(response);
        } else if (this.currentMode === 'quiz') {
            const response = `Quiz on ${topicNames[topic]}! Here's your first question, Chinna: ${this.getQuizQuestion(topic)}`;
            this.addMessage('nanna', response);
            this.speak(response);
        }

        this.setExpression('teaching');
    }

    getLearningContent(topic) {
        const content = {
            ai: `Let's start with the basics ra. AI, Artificial Intelligence, simply means making computers think like humans. Machine Learning is teaching computers through examples instead of rules. Like how you learned to recognize mangoes - not from a definition, but from seeing many mangoes. Same concept, Chinna!`,

            finance: `Chinna, finance basics are important ra. Let me teach you about securities identifiers. ISIN is like Aadhaar for stocks - a unique 12-character code that identifies any security globally. First two letters are country code, then 9 characters for the security, and one check digit. US0378331005 is Apple's ISIN. Ardam ayyinda?`,

            insurance: `Insurance is about risk transfer, Chinna. You pay a small amount regularly, the premium, and in return the company promises to pay large amounts if something bad happens. It's like everyone putting money in a pot, and whoever faces problems gets help from that pot. Simple concept, powerful protection!`,

            math: `Math is the language of the universe, Chinna. Let's start with linear algebra - it's all about vectors and matrices. Think of a vector as a list of numbers that describes something - like location coordinates. Matrix is a table of numbers. These are building blocks for AI and finance models!`
        };

        return content[topic] || "Let me prepare this topic for you, Chinna!";
    }

    getQuizQuestion(topic) {
        const questions = {
            ai: `What does ML stand for and what's the basic idea behind it?`,
            finance: `How many characters are in an ISIN code, and what do the first two characters represent?`,
            insurance: `What is the regular payment made by an insured person to maintain coverage called?`,
            math: `What's a vector in simple terms? Give an everyday example.`
        };

        return questions[topic] || "Tell me what you've learned about this topic, Chinna!";
    }

    handleQuizAnswer(answer) {
        // Simple keyword-based validation (in real app, would use AI)
        const lowerAnswer = answer.toLowerCase();

        if (lowerAnswer.includes('machine learning') ||
            lowerAnswer.includes('12') ||
            lowerAnswer.includes('premium') ||
            lowerAnswer.includes('list') || lowerAnswer.includes('direction')) {

            this.setExpression('proud');
            return `Baaga cheppav, Chinna! Correct answer! ${NANNA_PHRASES.encouragement[Math.floor(Math.random() * NANNA_PHRASES.encouragement.length)]} Want another question or shall we learn more?`;
        } else {
            this.setExpression('teaching');
            return `${NANNA_PHRASES.wrong_answer[Math.floor(Math.random() * NANNA_PHRASES.wrong_answer.length)]} Let me explain the correct answer... Want to try another question or learn more about this topic?`;
        }
    }

    getExploreContent() {
        const topics = [
            `Chinna, did you know about AI Agents? They're autonomous programs that can plan and execute tasks! Like having a digital assistant that doesn't just answer questions but actually does work. This is the future of AI ra!`,

            `Interesting topic ra, Chinna - T+1 Settlement! Stock markets are moving from T+2 to T+1, meaning trades settle next day instead of two days later. Faster settlement, less risk. India already did this!`,

            `Let me tell you about InsurTech, Chinna. Insurance plus Technology! Companies are using AI to assess risk, process claims instantly, and personalize premiums. The industry is changing fast!`,

            `Chinna, have you heard of Transformers? Not the robots ra! It's an AI architecture that changed everything. ChatGPT, Claude - all based on this. The key idea? 'Attention' - focusing on what's important.`
        ];

        return topics[Math.floor(Math.random() * topics.length)];
    }

    getProgressResponse() {
        return `Chinna, you're making good progress ra! Keep learning consistently - that's the key. Every day koncham koncham, one day expert avuthav. I'm tracking your journey. Come back tomorrow and we'll continue!`;
    }

    getGeneralResponse(text) {
        // Simple response for general queries
        const responses = [
            `Good question, Chinna! Let me think about this... Would you like me to explain more about any specific topic?`,

            `Hmm, interesting ra. Tell me more about what you want to know. I'm here to help!`,

            `Chinna, that's a thoughtful point. Shall we explore this in our learning session? Use the Learn or Quiz buttons below!`,

            `Ra Chinna, I understand. Let's take this step by step. What topic interests you most - AI, Finance, Insurance, or Math?`
        ];

        return responses[Math.floor(Math.random() * responses.length)];
    }

    setExpression(expression) {
        // Remove all expression classes
        this.avatar.classList.remove('happy', 'thinking', 'teaching', 'proud', 'encouraging');

        // Add new expression
        this.avatar.classList.add(expression);

        // Update badge
        const badges = {
            happy: '😊',
            thinking: '🤔',
            teaching: '👨‍🏫',
            proud: '🥲',
            encouraging: '💪',
            neutral: '😊'
        };

        this.expressionBadge.textContent = badges[expression] || badges.neutral;
    }

    speak(text) {
        if (!this.voiceEnabled.checked) return;

        this.speakingIndicator.classList.add('active');
        this.setExpression('teaching');

        this.voice.speak(
            text,
            () => {
                // On start
                this.speakingIndicator.classList.add('active');
            },
            () => {
                // On end
                this.speakingIndicator.classList.remove('active');
                this.setExpression('happy');
            }
        );
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.nanna = new NannaAvatar();
});
