# 🌍 Multilingual Support Guide

## 🎉 Languages Ready

Your platform now supports **3 languages**:
1. **English** (en)
2. **Shona** (sn)
3. **Ndebele** (nd)

---

## 📁 Files Created

### `translations.js`
Complete translation system with:
- 80+ translated phrases per language
- LanguageManager for switching languages
- Auto-detection of browser language
- LocalStorage persistence

---

## 🚀 Quick Implementation

### Step 1: Add translations.js to your HTML

```html
<script src="translations.js"></script>
```

### Step 2: Add language selector to header

```html
<div class="language-selector" style="position: absolute; top: 20px; right: 20px; display: flex; gap: 8px;">
    <button class="lang-btn active" data-lang="en" onclick="LanguageManager.setLanguage('en')" 
            style="padding: 8px 16px; border-radius: 8px; border: 2px solid rgba(16, 185, 129, 0.3); background: transparent; color: var(--text-primary); cursor: pointer; font-weight: 600;">
        English
    </button>
    <button class="lang-btn" data-lang="sn" onclick="LanguageManager.setLanguage('sn')" 
            style="padding: 8px 16px; border-radius: 8px; border: 2px solid rgba(16, 185, 129, 0.3); background: transparent; color: var(--text-primary); cursor: pointer; font-weight: 600;">
        Shona
    </button>
    <button class="lang-btn" data-lang="nd" onclick="LanguageManager.setLanguage('nd')" 
            style="padding: 8px 16px; border-radius: 8px; border: 2px solid rgba(16, 185, 129, 0.3); background: transparent; color: var(--text-primary); cursor: pointer; font-weight: 600;">
        Ndebele
    </button>
</div>
```

### Step 3: Add data-i18n attributes to your HTML

```html
<!-- Before -->
<h1>Agricultural Tools</h1>
<p>Complete farm budget calculator</p>
<button>Calculate Budget</button>

<!-- After -->
<h1 data-i18n="tools">Agricultural Tools</h1>
<p data-i18n="crop_budgets">Complete farm budget calculator</p>
<button data-i18n="calculate">Calculate Budget</button>
```

### Step 4: Initialize on page load

```html
<script>
    window.onload = function() {
        // Initialize language system
        LanguageManager.init();
        
        // ... rest of your code
    };
</script>
```

---

## 📖 Translation Keys

### Common UI Elements

| Key | English | Shona | Ndebele |
|-----|---------|-------|---------|
| `welcome` | Welcome! | Mauya! | Siyakwamukela! |
| `calculate` | Calculate | Verenga | Bala |
| `send` | Send | Tumira | Thumela |
| `loading` | Loading... | Kuverenga... | Iyalayisha... |

### Budget Elements

| Key | English | Shona | Ndebele |
|-----|---------|-------|---------|
| `gross_margin` | Gross Margin | Gross Margin | Inzuzo Enkulu |
| `total_income` | Total Income | Mari Yakapinda Yose | Imali Yonke Engenayo |
| `net_profit` | Net Profit | Purofiti Yakachena | Inzuzo Ehlanzekileyo |

### Cost Categories

| Key | English | Shona | Ndebele |
|-----|---------|-------|---------|
| `feed` | Feed | Chikafu | Ukudla |
| `veterinary` | Veterinary | Chiremba Wezvipfuwo | Udokotela Wezilwane |
| `water` | Water | Mvura | Amanzi |
| `labour` | Labour | Vashandi | Abasebenzi |

---

## 🎨 Styling Language Buttons

Add to your CSS:

```css
.lang-btn {
    padding: 8px 16px;
    border-radius: 8px;
    border: 2px solid rgba(16, 185, 129, 0.3);
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.lang-btn:hover {
    background: rgba(16, 185, 129, 0.1);
    transform: translateY(-2px);
}

.lang-btn.active {
    background: var(--gradient-primary);
    border-color: var(--primary-light);
    color: white;
}
```

---

## 🎤 Voice Integration with Languages

### Update voice_intelligence.js

```javascript
// In speakChatResponse function
VoiceIntelligence.speakChatResponse = function(response, sources, confidence) {
    // Get current language
    const currentLang = LanguageManager.getCurrentLang();
    
    // Translate response if needed
    let spokenText = response;
    if (currentLang === 'sn') {
        spokenText = "Mauya! " + response; // Add Shona greeting
    } else if (currentLang === 'nd') {
        spokenText = "Siyakwamukela! " + response; // Add Ndebele greeting
    }
    
    this.speak(spokenText, {
        confidence: confidence,
        context: 'answer'
    });
};
```

### Voice Cloning for Shona & Ndebele

**Option 1: ElevenLabs Voice Cloning**
1. Record 2 minutes of clear speech in Shona
2. Upload to ElevenLabs voice cloning
3. Get new voice ID
4. Update `voice_intelligence.js`:

```javascript
const voiceLanguageMap = {
    en: '21m00Tcm4TlvDq8ikWAM', // Rachel (English)
    sn: 'YOUR_SHONA_VOICE_ID',   // Custom Shona voice
    nd: 'YOUR_NDEBELE_VOICE_ID'  // Custom Ndebele voice
};
```

**Option 2: Use English voice for now**
```javascript
// Default - English voice for all (until clones ready)
const voiceLanguageMap = {
    en: '21m00Tcm4TlvDq8ikWAM',
    sn: '21m00Tcm4TlvDq8ikWAM', // Same as English
    nd: '21m00Tcm4TlvDq8ikWAM'  // Same as English
};
```

---

## 📱 Complete Example

### index.html with multilingual support

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hupfumi.Africa</title>
    <!-- ... your styles ... -->
</head>
<body>
    <header>
        <!-- Language Selector -->
        <div class="language-selector">
            <button class="lang-btn active" data-lang="en" onclick="LanguageManager.setLanguage('en')">
                English
            </button>
            <button class="lang-btn" data-lang="sn" onclick="LanguageManager.setLanguage('sn')">
                Shona
            </button>
            <button class="lang-btn" data-lang="nd" onclick="LanguageManager.setLanguage('nd')">
                Ndebele
            </button>
        </div>
        
        <!-- Translatable content -->
        <h1 data-i18n="brand_name">Hupfumi.Africa's Earth Evidence AI</h1>
        <p data-i18n="tagline" class="subtitle">Where the land speaks, data listens, and wisdom decides</p>
    </header>
    
    <div class="chat-container">
        <div class="chat-header">
            <span data-i18n="chat_title">💬 Ask Your Agricultural Questions</span>
        </div>
        
        <input type="text" 
               id="queryInput" 
               data-i18n="voice_input"
               placeholder="🎤 Speak your question">
        
        <button id="sendButton" 
                data-i18n="send" 
                onclick="sendQuery()">
            Send
        </button>
    </div>
    
    <script src="translations.js"></script>
    <script src="voice_intelligence.js"></script>
    <script>
        window.onload = function() {
            // Initialize language system
            LanguageManager.init();
            
            // Initialize voice with current language
            VoiceIntelligence.init('YOUR_API_KEY');
            
            // ... rest of your code
        };
    </script>
</body>
</html>
```

---

## 🧪 Testing

### Test Language Switching

1. Open your platform
2. Click "Shona" button
3. Verify all text changes to Shona
4. Click "Ndebele" button
5. Verify all text changes to Ndebele
6. Refresh page - language should persist (LocalStorage)

### Test Voice in Different Languages

```javascript
// English
LanguageManager.setLanguage('en');
VoiceIntelligence.speak("Welcome to Earth Evidence AI", {context: 'greeting'});

// Shona
LanguageManager.setLanguage('sn');
VoiceIntelligence.speak("Mauya! Tichakubatsira nekurima", {context: 'greeting'});

// Ndebele
LanguageManager.setLanguage('nd');
VoiceIntelligence.speak("Siyakwamukela! Sizakusiza ngezolimo", {context: 'greeting'});
```

---

## 🌍 Adding More Languages (SADC Expansion)

### For Zambia (Add Bemba & Nyanja):

```javascript
// In translations.js
translations.bem = {
    brand_name: "Hupfumi.Africa's Earth Evidence AI",
    tagline: "Uko ifyalo filandula, data yeumfwa, no bwengele bulanda",
    welcome: "Mwaiseni!",
    // ... rest of translations
};

translations.ny = {
    brand_name: "Hupfumi.Africa's Earth Evidence AI",
    tagline: "Pamene dziko limalankhula, data limamva, ndi nzeru zimasankha",
    welcome: "Muli bwanji!",
    // ... rest of translations
};
```

### For South Africa (Add Zulu, Xhosa, Afrikaans):

```javascript
translations.zu = {
    welcome: "Sawubona!",
    // ... Zulu translations
};

translations.xh = {
    welcome: "Molo!",
    // ... Xhosa translations
};

translations.af = {
    welcome: "Welkom!",
    // ... Afrikaans translations
};
```

---

## 📊 Language Coverage

### Zimbabwe (Current)
✅ English  
✅ Shona  
✅ Ndebele  

### Coming Soon - SADC
🔜 **South Africa:** Zulu, Xhosa, Afrikaans, Sotho, Tswana  
🔜 **Zambia:** Bemba, Nyanja, Tonga  
🔜 **Mozambique:** Portuguese  
🔜 **Botswana:** Setswana  
🔜 **Malawi:** Chichewa  
🔜 **Tanzania:** Swahili  
🔜 **Namibia:** Oshiwambo, Afrikaans, German  

---

## 🎯 Implementation Checklist

- [ ] Add `translations.js` to all HTML pages
- [ ] Add language selector to header
- [ ] Add `data-i18n` attributes to all translatable text
- [ ] Initialize `LanguageManager.init()` on page load
- [ ] Test switching between English, Shona, Ndebele
- [ ] Test language persistence (refresh page)
- [ ] Record voice samples for Shona & Ndebele
- [ ] Upload to ElevenLabs for voice cloning
- [ ] Update voice IDs in `voice_intelligence.js`
- [ ] Test voice output in all languages
- [ ] Deploy!

---

## 🌟 Result

Your farmers can now:
1. **Switch languages** with one click
2. **See everything** in their language (Shona/Ndebele)
3. **Hear AI responses** in their language (with voice cloning)
4. **Language persists** across sessions
5. **Auto-detects** browser language on first visit

**"Zimbabwe speaks in three voices - all powered by one intelligence"** 🇿🇼🎤✨

---

**Ready to add Shona & Ndebele to your platform?** 

Just add the language selector and `translations.js` to your pages! 🌍
