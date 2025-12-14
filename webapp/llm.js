/**
 * LLM Module - Gemini / OpenAI / Claude Integration
 *
 * Handles text-to-text processing with any LLM backend.
 * Receives text from STT, sends to LLM, returns response for TTS.
 */

class LLMService {
    constructor() {
        this.conversationHistory = [];
        this.maxHistory = 10; // Keep last 10 exchanges for context
    }

    /**
     * Send message to LLM and get response
     * @param {string} userMessage - Text from STT
     * @returns {Promise<string>} - LLM response text
     */
    async chat(userMessage) {
        const provider = CONFIG.LLM.provider;

        debug(`LLM: Sending to ${provider}: "${userMessage}"`);

        // Add to history
        this.conversationHistory.push({
            role: 'user',
            content: userMessage
        });

        // Trim history if too long
        if (this.conversationHistory.length > this.maxHistory * 2) {
            this.conversationHistory = this.conversationHistory.slice(-this.maxHistory * 2);
        }

        let response;

        try {
            switch (provider) {
                case 'gemini':
                    response = await this.callGemini(userMessage);
                    break;
                case 'openai':
                    response = await this.callOpenAI(userMessage);
                    break;
                default:
                    throw new Error(`Unknown provider: ${provider}`);
            }

            // Add response to history
            this.conversationHistory.push({
                role: 'assistant',
                content: response
            });

            debug(`LLM: Response: "${response}"`);
            return response;

        } catch (error) {
            debug(`LLM Error: ${error.message}`);
            throw error;
        }
    }

    /**
     * Call Gemini API
     */
    async callGemini(userMessage) {
        const apiKey = CONFIG.LLM.gemini.apiKey;
        const model = CONFIG.LLM.gemini.model;

        if (!apiKey) {
            throw new Error('Gemini API key not set. Add it in Settings.');
        }

        // Build conversation for Gemini format
        const contents = [];

        // Add system instruction as first user message (Gemini style)
        contents.push({
            role: 'user',
            parts: [{ text: `System: ${CONFIG.SYSTEM_PROMPT}\n\nNow respond as Nanna to: ${userMessage}` }]
        });

        // For ongoing conversation, we'd structure differently, but for simplicity:
        // Each exchange is treated fresh with context

        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: contents,
                generationConfig: {
                    maxOutputTokens: CONFIG.LLM.gemini.maxTokens,
                    temperature: 0.8
                },
                safetySettings: [
                    { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_NONE" },
                    { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_NONE" }
                ]
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Gemini API error');
        }

        const data = await response.json();

        // Extract text from Gemini response
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!text) {
            throw new Error('No response from Gemini');
        }

        return text.trim();
    }

    /**
     * Call OpenAI API (alternative backend)
     */
    async callOpenAI(userMessage) {
        const apiKey = CONFIG.LLM.openai.apiKey;
        const model = CONFIG.LLM.openai.model;

        if (!apiKey) {
            throw new Error('OpenAI API key not set');
        }

        const messages = [
            { role: 'system', content: CONFIG.SYSTEM_PROMPT },
            ...this.conversationHistory
        ];

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                max_tokens: 256,
                temperature: 0.8
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'OpenAI API error');
        }

        const data = await response.json();
        return data.choices[0].message.content.trim();
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
        debug('LLM: History cleared');
    }
}

// Create global instance
const llm = new LLMService();
