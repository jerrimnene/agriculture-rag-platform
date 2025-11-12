/**
 * VOICE INTELLIGENCE SYSTEM
 * 
 * Integrates ElevenLabs TTS and Web Speech API for full voice interaction
 * Works across the entire platform - chat, budgets, comparisons, everything
 */

const VoiceIntelligence = {
    
    // Configuration
    config: {
        elevenLabsApiKey: '', // Set your ElevenLabs API key
        voiceId: '21m00Tcm4TlvDq8ikWAM', // Rachel voice (or choose your own)
        model: 'eleven_multilingual_v2', // Supports multiple languages
        
        // Voice settings for different confidence levels
        voiceSettings: {
            high: { stability: 0.75, similarity_boost: 0.75, style: 0.5 },      // Confident
            medium: { stability: 0.60, similarity_boost: 0.70, style: 0.4 },    // Thoughtful
            low: { stability: 0.50, similarity_boost: 0.65, style: 0.3 }        // Careful
        }
    },
    
    // Speech recognition
    recognition: null,
    isListening: false,
    
    // Audio playback
    audioContext: null,
    currentAudio: null,
    isPlaying: false,
    
    /**
     * Initialize voice system
     */
    init: function(apiKey) {
        this.config.elevenLabsApiKey = apiKey;
        this.setupSpeechRecognition();
        this.setupAudioContext();
        console.log('Voice Intelligence initialized');
    },
    
    /**
     * Setup speech recognition (voice input)
     */
    setupSpeechRecognition: function() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US'; // Can support other languages
        
        this.recognition.onstart = () => {
            this.isListening = true;
            console.log('Voice recognition started');
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            console.log('Voice recognition ended');
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
        };
    },
    
    /**
     * Setup audio context for playback
     */
    setupAudioContext: function() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    },
    
    /**
     * Start listening for voice input
     */
    startListening: function(onResult, onInterim = null) {
        if (!this.recognition) {
            alert('Voice recognition not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
            return;
        }
        
        this.recognition.onresult = (event) => {
            const results = event.results;
            const transcript = results[results.length - 1][0].transcript;
            const isFinal = results[results.length - 1].isFinal;
            
            if (isFinal && onResult) {
                onResult(transcript);
            } else if (!isFinal && onInterim) {
                onInterim(transcript);
            }
        };
        
        this.recognition.start();
    },
    
    /**
     * Stop listening
     */
    stopListening: function() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    },
    
    /**
     * Speak text using ElevenLabs
     * Automatically adjusts tone based on confidence and context
     */
    speak: async function(text, options = {}) {
        const {
            confidence = 1.0,
            context = 'answer',  // 'answer', 'budget', 'warning', 'greeting'
            onStart = null,
            onEnd = null
        } = options;
        
        // Stop current playback if any
        if (this.isPlaying) {
            this.stopSpeaking();
        }
        
        // Determine voice settings based on confidence
        let voiceSettings;
        if (confidence >= 0.8) {
            voiceSettings = this.config.voiceSettings.high;
        } else if (confidence >= 0.5) {
            voiceSettings = this.config.voiceSettings.medium;
        } else {
            voiceSettings = this.config.voiceSettings.low;
        }
        
        // Add contextual prefix for emotional tone
        let spokenText = this.addEmotionalContext(text, context, confidence);
        
        try {
            if (onStart) onStart();
            this.isPlaying = true;
            
            // Call ElevenLabs API
            const audioBlob = await this.callElevenLabsAPI(spokenText, voiceSettings);
            
            // Play audio
            await this.playAudio(audioBlob);
            
            this.isPlaying = false;
            if (onEnd) onEnd();
            
        } catch (error) {
            console.error('Error generating speech:', error);
            this.isPlaying = false;
            
            // Fallback to browser TTS
            this.fallbackSpeak(text);
        }
    },
    
    /**
     * Add emotional context to spoken text
     */
    addEmotionalContext: function(text, context, confidence) {
        // Don't modify the text, but this could be used for SSML in the future
        // ElevenLabs will naturally adjust tone based on punctuation and content
        
        if (context === 'warning' && confidence < 0.7) {
            return `Please note: ${text}`;
        }
        
        if (context === 'greeting') {
            return `Mauya! ${text}`; // Shona greeting
        }
        
        return text;
    },
    
    /**
     * Call ElevenLabs API
     */
    callElevenLabsAPI: async function(text, voiceSettings) {
        const response = await fetch(
            `https://api.elevenlabs.io/v1/text-to-speech/${this.config.voiceId}`,
            {
                method: 'POST',
                headers: {
                    'Accept': 'audio/mpeg',
                    'Content-Type': 'application/json',
                    'xi-api-key': this.config.elevenLabsApiKey
                },
                body: JSON.stringify({
                    text: text,
                    model_id: this.config.model,
                    voice_settings: voiceSettings
                })
            }
        );
        
        if (!response.ok) {
            throw new Error(`ElevenLabs API error: ${response.status}`);
        }
        
        return await response.blob();
    },
    
    /**
     * Play audio blob
     */
    playAudio: async function(audioBlob) {
        return new Promise((resolve, reject) => {
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            this.currentAudio = audio;
            
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
                resolve();
            };
            
            audio.onerror = (error) => {
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
                reject(error);
            };
            
            audio.play();
        });
    },
    
    /**
     * Stop current speech
     */
    stopSpeaking: function() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
        }
        this.isPlaying = false;
    },
    
    /**
     * Fallback to browser's built-in TTS
     */
    fallbackSpeak: function(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    },
    
    /**
     * Speak budget results with structured information
     */
    speakBudget: function(cropName, district, budget, adjustments = null) {
        const formatCurrency = (num) => {
            if (num >= 1000000) return `${(num/1000000).toFixed(1)} million dollars`;
            if (num >= 1000) return `${(num/1000).toFixed(1)} thousand dollars`;
            return `${num.toFixed(0)} dollars`;
        };
        
        let text = `Budget analysis for ${cropName}`;
        
        if (district) {
            text += ` in ${district} district`;
        }
        
        text += `. Gross margin: ${formatCurrency(budget.summary.gross_profit)} per hectare. `;
        text += `Total income: ${formatCurrency(budget.summary.gross_return)}. `;
        text += `Variable costs: ${formatCurrency(budget.summary.variable_costs_per_ha)}. `;
        
        if (adjustments && adjustments.explanation.length > 0) {
            text += `This budget has been adjusted for local conditions. `;
            text += adjustments.explanation.slice(0, 3).join('. ') + '. ';
        }
        
        const confidence = adjustments ? adjustments.confidence : 1.0;
        
        this.speak(text, {
            confidence: confidence,
            context: 'budget'
        });
    },
    
    /**
     * Speak crop comparison results
     */
    speakCropComparison: function(district, topCrops) {
        let text = `Based on ${district} conditions, here are the top three most profitable crops. `;
        
        topCrops.slice(0, 3).forEach((crop, index) => {
            const rank = ['First', 'Second', 'Third'][index];
            const formatCurrency = (num) => {
                if (num >= 1000) return `${(num/1000).toFixed(1)} thousand dollars`;
                return `${num.toFixed(0)} dollars`;
            };
            
            text += `${rank}: ${crop.crop} with a gross margin of ${formatCurrency(crop.grossMargin)} per hectare. `;
        });
        
        this.speak(text, {
            confidence: 0.9,
            context: 'answer'
        });
    },
    
    /**
     * Speak district intelligence adjustments
     */
    speakAdjustments: function(district, adjustments) {
        let text = `The budget has been adjusted for ${district} with ${(adjustments.confidence * 100).toFixed(0)} percent confidence. `;
        
        const majorFactors = adjustments.explanation.slice(0, 2);
        if (majorFactors.length > 0) {
            text += 'Key factors include: ' + majorFactors.join(', and ') + '. ';
        }
        
        this.speak(text, {
            confidence: adjustments.confidence,
            context: 'answer'
        });
    },
    
    /**
     * Speak chat response with citations
     */
    speakChatResponse: function(response, sources = [], confidence = 1.0) {
        let text = response;
        
        if (sources.length > 0) {
            text += ` This information is based on ${sources.length} agricultural source${sources.length > 1 ? 's' : ''}.`;
        }
        
        this.speak(text, {
            confidence: confidence,
            context: 'answer'
        });
    }
};

// Export for use in HTML pages
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceIntelligence;
}
