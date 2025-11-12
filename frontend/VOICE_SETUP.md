# 🎤 Voice Intelligence Setup Guide

## What You Get

Your agricultural AI will be able to:
- ✅ **Listen** to farmers speaking (any language supported by browser)
- ✅ **Understand** complex agricultural questions
- ✅ **Access** ALL your data (districts, budgets, RAG knowledge)
- ✅ **Speak** answers with emotional intelligence
- ✅ **Adapt tone** based on confidence (certain vs uncertain)
- ✅ **Work everywhere** (chat, budgets, comparisons)

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get ElevenLabs API Key

1. Go to: https://elevenlabs.io
2. Sign up (free tier available)
3. Go to Profile → API Keys
4. Copy your API key

### Step 2: Choose Your Voice

Browse voices at: https://elevenlabs.io/voice-library

Recommended voices:
- **Rachel** (default): Clear, professional English
- **Matilda**: Warm, friendly
- **Antoni**: Male, authoritative
- **Custom**: Clone any voice (Shona speaker!)

Copy the Voice ID (e.g., `21m00Tcm4TlvDq8ikWAM`)

### Step 3: Initialize in Your HTML

Add to `index.html` and `tools.html`:

```html
<!-- Add before closing </body> tag -->
<script src="voice_intelligence.js"></script>
<script>
    // Initialize voice system
    window.onload = function() {
        VoiceIntelligence.init('YOUR_ELEVENLABS_API_KEY');
        
        // ... rest of your onload code
    };
</script>
```

---

## 💡 Usage Examples

### 1. Voice-Enable Chat (index.html)

```javascript
// Add microphone button
<button id="voiceButton" onclick="toggleVoiceInput()">
    🎤 Hold to Speak
</button>

// Voice input function
function toggleVoiceInput() {
    VoiceIntelligence.startListening(
        // Final result
        (transcript) => {
            document.getElementById('queryInput').value = transcript;
            sendQuery(); // Your existing function
        },
        // Interim results (optional - shows what's being said)
        (interim) => {
            document.getElementById('queryInput').value = interim;
        }
    );
}

// Voice output when AI responds
// Modify your existing sendQuery() function:
async function sendQuery() {
    // ... your existing code to get response ...
    
    // After getting response, speak it:
    VoiceIntelligence.speakChatResponse(
        data.answer,
        data.sources,
        0.9 // confidence
    );
}
```

### 2. Voice-Enable Budget Calculator (tools.html)

```javascript
// After calculating budget, speak results:
async function calculateBudget() {
    // ... your existing code ...
    
    // Speak the budget
    VoiceIntelligence.speakBudget(
        cropName,
        selectedDistrict,
        adjustedBudget,
        adjustedBudget.adjustments
    );
}

// Add a "Read Budget" button:
<button onclick="readBudgetAloud()">🔊 Read Budget Aloud</button>

function readBudgetAloud() {
    if (adjustedBudgetForSensitivity) {
        VoiceIntelligence.speakBudget(
            document.getElementById('cropSelect').value,
            selectedDistrict,
            adjustedBudgetForSensitivity,
            adjustedBudgetForSensitivity.adjustments
        );
    }
}
```

### 3. Voice-Enable Crop Comparison

```javascript
// In loadCropComparison(), after displaying results:
function speakComparison() {
    VoiceIntelligence.speakCropComparison(
        selectedDistrict,
        cropComparisons // Your sorted crop array
    );
}

// Add button:
<button onclick="speakComparison()">🔊 Hear Top Crops</button>
```

---

## 🎯 Smart Features

### 1. Confidence-Based Tone

The system automatically adjusts voice based on confidence:

```javascript
// High confidence (80%+)
// → Stable, authoritative voice

// Medium confidence (50-80%)
// → Thoughtful, careful voice

// Low confidence (<50%)
// → Cautious, uncertain tone
```

**Example:**
- "Tobacco is the best crop for Buhera" (confident, 90%)
- vs
- "Based on limited data, you might consider tobacco" (cautious, 40%)

### 2. Context-Aware Speaking

Different contexts get different emotional tones:

```javascript
VoiceIntelligence.speak(text, {
    confidence: 0.9,
    context: 'budget'      // or 'answer', 'warning', 'greeting'
});
```

### 3. Multilingual Support

```javascript
// ElevenLabs model supports:
// - English
// - Spanish
// - French
// - German
// - Polish
// - Italian
// - Portuguese
// - Hindi
// And more!

// For Shona: use custom voice cloning
```

### 4. Emotional Greetings

```javascript
VoiceIntelligence.speak(
    "Welcome to Earth Evidence AI",
    { context: 'greeting' }
);
// Outputs: "Mauya! Welcome to Earth Evidence AI"
```

---

## 🌍 Real-World Use Cases

### Scenario 1: Farmer in the Field

```
Farmer: [Presses mic] "What should I plant in Buhera this season?"

System: 
→ Listens via Web Speech API
→ Sends to your RAG system
→ Gets district-aware answer
→ Speaks via ElevenLabs:
    "Based on Buhera's conditions with 500-700mm rainfall 
     and sandy soils, I recommend tobacco as your most 
     profitable crop with a gross margin of 5,200 dollars 
     per hectare..."
```

### Scenario 2: Extension Officer Training

```
Officer: "Show me the budget for cabbages in Harare"

System:
→ Loads budget
→ Applies district intelligence
→ Speaks: "Budget analysis for cabbages in Harare district. 
           Gross margin: 7 thousand dollars per hectare..."
```

### Scenario 3: Market Day Information

```
Farmer: "Which crops should I compare for my district?"

System:
→ Runs comparison
→ Speaks: "Based on Buhera conditions, here are the top 
           three most profitable crops. First: Tobacco 
           with 5,200 dollars per hectare. Second: 
           Butternut with 4,800 dollars..."
```

---

## 📱 Mobile Integration

Works perfectly on:
- ✅ Chrome (Android)
- ✅ Safari (iOS)
- ✅ Edge (Windows Mobile)

**Progressive Web App (PWA)** ready:
- Add to home screen
- Works offline (after first load)
- Native app feel
- Voice works everywhere

---

## 🔧 Advanced Features

### Custom Voice Cloning (Shona Speaker)

```javascript
// Clone a native Shona speaker's voice:
// 1. Record 1-2 minutes of clear speech
// 2. Upload to ElevenLabs
// 3. Get new voice ID
// 4. Update config:

VoiceIntelligence.config.voiceId = 'YOUR_CUSTOM_VOICE_ID';
```

### Voice Controls

```javascript
// Pause/Resume
VoiceIntelligence.stopSpeaking();

// Check if speaking
if (VoiceIntelligence.isPlaying) {
    // Show visual indicator
}

// Check if listening
if (VoiceIntelligence.isListening) {
    // Show mic animation
}
```

### Fallback System

If ElevenLabs fails:
→ Automatically uses browser's built-in TTS
→ No disruption to user experience

---

## 💰 Cost Estimate

ElevenLabs pricing (as of 2024):
- **Free**: 10,000 characters/month (~100 responses)
- **Starter**: $5/month = 30,000 characters (~300 responses)
- **Creator**: $22/month = 100,000 characters (~1,000 responses)
- **Pro**: $99/month = 500,000 characters (~5,000 responses)

**Optimization tips:**
- Cache common responses
- Use shorter summaries for voice
- Only speak on user request (button click)

---

## 🎨 UI Enhancements

### Voice Button Styles

```css
#voiceButton {
    background: var(--gradient-primary);
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-lg);
}

#voiceButton.listening {
    animation: pulse 1.5s infinite;
    background: var(--gradient-accent);
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

#voiceButton.speaking {
    animation: speaking 0.5s infinite;
}

@keyframes speaking {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
```

### Status Indicators

```html
<div id="voiceStatus" style="display: none;">
    🎤 Listening... <span id="interim"></span>
</div>

<div id="speakingStatus" style="display: none;">
    🔊 Speaking...
</div>
```

---

## ✅ Testing Checklist

- [ ] API key configured
- [ ] Voice input works (mic button)
- [ ] Voice output works (speaks answers)
- [ ] Confidence levels adjust tone
- [ ] Works in chat interface
- [ ] Works in budget calculator
- [ ] Works in crop comparison
- [ ] Mobile responsive
- [ ] Fallback TTS works
- [ ] Stop/pause works

---

## 🚀 Go Live Checklist

1. **Get ElevenLabs account**
2. **Choose/clone voice**
3. **Add voice_intelligence.js to both HTML files**
4. **Initialize with API key**
5. **Add voice buttons to UI**
6. **Test on desktop & mobile**
7. **Deploy!**

---

## 🌟 Result

You'll have the **first voice-enabled, district-intelligent agricultural AI in Africa**:

- Farmers can TALK to their fields' data
- AI SPEAKS with emotion and confidence
- Works in ANY language (via voice cloning)
- Understands EVERYTHING in your system
- Accessible to non-literate farmers

**"Where the land speaks, data listens, and wisdom decides"** - now literally! 🌾🎤✨
