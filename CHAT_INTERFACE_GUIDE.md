# 💬 CHAT INTERFACE INTEGRATION GUIDE

**Date:** November 11, 2024  
**For:** Zimbabwe Agriculture RAG Platform

---

## 🎯 Overview

This guide shows you how to integrate the Agriculture RAG API into a chat interface (web, mobile, WhatsApp, USSD, etc.).

---

## 📱 USER FLOW

### 1. User Opens Chat
```
User: Hello
Bot: 👋 Welcome to Zimbabwe Agriculture Advisory!
     
     I can help you with:
     • Crop advice for your district
     • Market prices & where to sell
     • Profitability calculations
     • Best farming practices
     
     What district are you in?
```

### 2. User Selects District
```
User: I'm in Bindura
Bot: 📍 Great! I'm now set to Bindura District.
     
     [Loads: GET /api/district/Bindura/complete-profile]
     
     Quick facts about Bindura:
     • Natural Region: IIa (good rainfall)
     • Main crops: Tobacco, Maize, Soya beans
     • Best crop for profit: Tobacco
     
     What would you like to know?
```

### 3. User Asks Questions
```
User: What crops can I grow here?
Bot: [Calls: POST /api/district/Bindura/ask?question=What crops can I grow here]
     
     In Bindura District (Natural Region IIa), you can grow:
     
     🌾 Main Crops:
     • Tobacco (most profitable)
     • Maize (8-9 tonnes/ha possible)
     • Soya beans
     • Wheat
     
     🥬 Horticulture:
     • Tomatoes
     • Green beans
     • Baby corn
     
     The district has 750-1000mm rainfall and good soils for intensive farming.
```

```
User: Where can I sell my tobacco?
Bot: [Calls: GET /api/district/Bindura/markets]
     
     🏪 Where to Sell Tobacco in Bindura:
     
     LOCAL (Best for small amounts):
     • Bindura growth point
     • Local contractors
     
     NATIONAL (Best prices):
     • Tobacco auction floors (Harare)
     • Current price: $5.45/kg
     
     CONTRACT FARMING:
     • TSL (Tian-Ze)
     • British American Tobacco (BAT)
     • Alliance One
     
     💡 Tip: Contract farming gives you inputs + guaranteed buyer
```

```
User: Which crop is most profitable?
Bot: [Calls: GET /api/district/Bindura/profitability-comparison]
     
     💰 Most Profitable Crops in Bindura:
     
     1. 🥇 Tobacco
        • Gross margin: $3,500/ha
        • Profit margin: 68%
        • Recommendation: Highly Profitable
     
     2. 🥈 Maize (with good management)
        • Gross margin: $1,589/ha
        • Profit margin: 99%
        • Recommendation: Profitable
     
     3. 🥉 Soya beans
        • Gross margin: $800/ha
        • Profit margin: 55%
        • Recommendation: Moderately Profitable
```

---

## 🔌 API INTEGRATION

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required (add JWT/API keys for production).

---

## 📍 ENDPOINT 1: Complete District Profile

**When to use:** User selects/mentions their district

**Endpoint:**
```
GET /api/district/{district_name}/complete-profile
```

**Example:**
```javascript
// JavaScript/React
const loadDistrictProfile = async (district) => {
  const response = await fetch(
    `http://localhost:8000/api/district/${district}/complete-profile`
  );
  const data = await response.json();
  
  // Store in state
  setCurrentDistrict(data);
  
  // Display quick facts
  displayQuickFacts(data.quick_facts);
};

// Usage
loadDistrictProfile("Bindura");
```

**Response Structure:**
```json
{
  "district": "Bindura",
  "status": "complete_profile",
  "geographic_info": {
    "province": "Mashonaland Central",
    "natural_region": "Region IIa",
    "rainfall_mm": "750-1000mm"
  },
  "agricultural_profile": {
    "profile_text": "[Full district information]",
    "source_count": 10
  },
  "markets": {...},
  "selling_locations": {...},
  "profitability": {...},
  "quick_facts": {
    "best_crop_for_profit": "tobacco",
    "main_crops": ["tobacco", "maize", "soya"],
    "main_challenges": ["fall armyworm", "striga"]
  }
}
```

**What to display:**
- Show quick facts in a card/summary
- Cache the full profile for context
- Use profitability data for recommendations
- Use markets data when user asks about selling

---

## 💬 ENDPOINT 2: District-Specific Q&A

**When to use:** User asks any question about their district

**Endpoint:**
```
POST /api/district/{district_name}/ask?question={question}
```

**Example:**
```javascript
// JavaScript/React
const askDistrictQuestion = async (district, question) => {
  const response = await fetch(
    `http://localhost:8000/api/district/${district}/ask?question=${encodeURIComponent(question)}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }
  );
  const data = await response.json();
  
  return {
    answer: data.answer,
    sources: data.sources,
    source_count: data.source_count
  };
};

// Usage
const result = await askDistrictQuestion("Bindura", "What crops grow here?");
displayBotMessage(result.answer);
```

**Response Structure:**
```json
{
  "district": "Bindura",
  "question": "What crops grow here?",
  "answer": "In Bindura District (Natural Region IIa), main crops include...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "category": "crop",
        "district": "Bindura"
      }
    }
  ],
  "source_count": 5
}
```

**What to display:**
- Show the answer as bot's response
- Optionally show "Based on X sources" for credibility
- Add "Learn more" button to show sources if needed

---

## 🏪 ENDPOINT 3: Markets & Where to Sell

**When to use:** User asks about markets, selling, or prices

**Endpoint:**
```
GET /api/district/{district_name}/markets
```

**Example:**
```javascript
// JavaScript/React
const getMarketInfo = async (district) => {
  const response = await fetch(
    `http://localhost:8000/api/district/${district}/markets`
  );
  const data = await response.json();
  
  return {
    localMarkets: data.local_markets,
    sellingOptions: data.selling_options,
    currentPrices: data.current_prices,
    transportTips: data.transport_tips
  };
};

// Usage
const markets = await getMarketInfo("Bindura");
displayMarkets(markets);
```

**Response Structure:**
```json
{
  "district": "Bindura",
  "local_markets": {
    "growth_points": ["Bindura Growth Point"],
    "service_centres": ["Bindura Service Centre"]
  },
  "current_prices": {
    "maize": 200000,
    "tobacco": 545000
  },
  "selling_options": {
    "local": {...},
    "regional": {...},
    "national": {...},
    "contract_farming": {...}
  },
  "transport_tips": [...]
}
```

**What to display:**
- Show prices in a formatted list
- Present selling options as cards/tabs
- Include transport tips at the bottom

---

## 💰 ENDPOINT 4: Profitability Comparison

**When to use:** User asks about profit, which crop to grow, or economics

**Endpoint:**
```
GET /api/district/{district_name}/profitability-comparison
```

**Example:**
```javascript
// JavaScript/React
const compareProfit = async (district) => {
  const response = await fetch(
    `http://localhost:8000/api/district/${district}/profitability-comparison`
  );
  const data = await response.json();
  
  return data.profitability_ranking;
};

// Usage
const ranking = await compareProfit("Bindura");
displayProfitRanking(ranking);
```

**Response Structure:**
```json
{
  "district": "Bindura",
  "profitability_ranking": [
    {
      "crop": "tobacco",
      "gross_margin_per_ha": 3500,
      "profit_margin_percentage": 68,
      "expected_yield_tonnes_per_ha": 2.5,
      "recommendation": "Highly Profitable"
    }
  ],
  "top_recommendation": {...}
}
```

**What to display:**
- Show as a ranked list with visual indicators (🥇🥈🥉)
- Include profit margins and yields
- Highlight the top recommendation

---

## 🧠 INTELLIGENT ROUTING

The chat interface should intelligently route questions to the right endpoint:

```javascript
const routeQuestion = (district, question) => {
  const lowerQ = question.toLowerCase();
  
  // Market/selling questions
  if (lowerQ.includes('sell') || lowerQ.includes('market') || lowerQ.includes('price')) {
    return getMarketInfo(district);
  }
  
  // Profitability questions
  if (lowerQ.includes('profit') || lowerQ.includes('best crop') || lowerQ.includes('most profitable')) {
    return compareProfit(district);
  }
  
  // General questions - use Q&A endpoint
  return askDistrictQuestion(district, question);
};
```

---

## 📋 SAMPLE CHAT IMPLEMENTATION

### React/JavaScript Example

```javascript
import React, { useState, useEffect } from 'react';

const AgricultureChatbot = () => {
  const [district, setDistrict] = useState(null);
  const [districtProfile, setDistrictProfile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const API_BASE = 'http://localhost:8000';
  
  // Load district profile when selected
  useEffect(() => {
    if (district) {
      loadDistrictProfile(district);
    }
  }, [district]);
  
  const loadDistrictProfile = async (districtName) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/district/${districtName}/complete-profile`
      );
      const data = await response.json();
      setDistrictProfile(data);
      
      // Add welcome message
      addBotMessage(
        `📍 Set to ${districtName} District!\n\n` +
        `Quick facts:\n` +
        `• Natural Region: ${data.geographic_info.natural_region}\n` +
        `• Main crops: ${data.quick_facts.main_crops.join(', ')}\n` +
        `• Best for profit: ${data.quick_facts.best_crop_for_profit}\n\n` +
        `What would you like to know?`
      );
    } catch (error) {
      console.error('Error loading district:', error);
    }
  };
  
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    // Add user message
    addUserMessage(input);
    const question = input;
    setInput('');
    
    // If no district set, prompt for it
    if (!district) {
      addBotMessage('Please tell me which district you are in first.');
      return;
    }
    
    try {
      // Route question to appropriate endpoint
      const response = await routeAndFetchAnswer(district, question);
      addBotMessage(response);
    } catch (error) {
      addBotMessage('Sorry, I encountered an error. Please try again.');
    }
  };
  
  const routeAndFetchAnswer = async (district, question) => {
    const lowerQ = question.toLowerCase();
    
    // Market questions
    if (lowerQ.includes('sell') || lowerQ.includes('market') || lowerQ.includes('price')) {
      const response = await fetch(`${API_BASE}/api/district/${district}/markets`);
      const data = await response.json();
      return formatMarketResponse(data);
    }
    
    // Profitability questions
    if (lowerQ.includes('profit') || lowerQ.includes('best crop')) {
      const response = await fetch(`${API_BASE}/api/district/${district}/profitability-comparison`);
      const data = await response.json();
      return formatProfitResponse(data);
    }
    
    // General Q&A
    const response = await fetch(
      `${API_BASE}/api/district/${district}/ask?question=${encodeURIComponent(question)}`,
      { method: 'POST' }
    );
    const data = await response.json();
    return data.answer;
  };
  
  const formatMarketResponse = (data) => {
    let response = `🏪 Markets in ${data.district}:\n\n`;
    
    // Local markets
    if (data.local_markets.growth_points.length > 0) {
      response += `LOCAL:\n`;
      data.local_markets.growth_points.forEach(m => {
        response += `• ${m}\n`;
      });
      response += `\n`;
    }
    
    // Prices
    response += `💰 Current Prices:\n`;
    Object.entries(data.current_prices).forEach(([crop, price]) => {
      response += `• ${crop}: $${(price / 1000).toFixed(2)}/kg\n`;
    });
    
    return response;
  };
  
  const formatProfitResponse = (data) => {
    let response = `💰 Most Profitable Crops in ${data.district}:\n\n`;
    
    data.profitability_ranking.slice(0, 3).forEach((crop, index) => {
      const medal = ['🥇', '🥈', '🥉'][index];
      response += `${medal} ${crop.crop}\n`;
      response += `   Profit: $${crop.gross_margin_per_ha}/ha (${crop.profit_margin_percentage}%)\n`;
      response += `   ${crop.recommendation}\n\n`;
    });
    
    return response;
  };
  
  const addUserMessage = (text) => {
    setMessages(prev => [...prev, { type: 'user', text }]);
  };
  
  const addBotMessage = (text) => {
    setMessages(prev => [...prev, { type: 'bot', text }]);
  };
  
  return (
    <div className="chatbot">
      {/* District selector */}
      {!district && (
        <div className="district-selector">
          <h3>Select your district:</h3>
          <select onChange={(e) => setDistrict(e.target.value)}>
            <option value="">-- Select --</option>
            <option value="Bindura">Bindura</option>
            <option value="Chivi">Chivi</option>
            <option value="Harare">Harare</option>
            {/* Add all districts */}
          </select>
        </div>
      )}
      
      {/* Messages */}
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
      </div>
      
      {/* Input */}
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask me anything about farming..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default AgricultureChatbot;
```

---

## 📱 MOBILE/WHATSAPP INTEGRATION

### WhatsApp Bot Flow

```python
from twilio.twiml.messaging_response import MessagingResponse
import requests

API_BASE = "http://localhost:8000"
user_sessions = {}  # Store user district

def whatsapp_webhook(request):
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # Check if user has selected district
    if from_number not in user_sessions:
        msg.body("👋 Welcome to Zimbabwe Agriculture Advisory!\n\n"
                "What district are you in?\n\n"
                "Reply with your district name (e.g., Bindura)")
        user_sessions[from_number] = {'district': None}
        return str(resp)
    
    # If no district set, this is the district
    if user_sessions[from_number]['district'] is None:
        district = incoming_msg.title()
        user_sessions[from_number]['district'] = district
        
        # Load district profile
        response = requests.get(f"{API_BASE}/api/district/{district}/complete-profile")
        if response.ok:
            data = response.json()
            msg.body(f"📍 Set to {district} District!\n\n"
                    f"Main crops: {', '.join(data['quick_facts']['main_crops'])}\n"
                    f"Best for profit: {data['quick_facts']['best_crop_for_profit']}\n\n"
                    f"Ask me anything about farming!")
        return str(resp)
    
    # Answer question
    district = user_sessions[from_number]['district']
    response = requests.post(
        f"{API_BASE}/api/district/{district}/ask",
        params={'question': incoming_msg}
    )
    
    if response.ok:
        data = response.json()
        # Truncate for WhatsApp (1600 char limit)
        answer = data['answer'][:1500]
        msg.body(answer)
    
    return str(resp)
```

---

## 🎨 UI/UX RECOMMENDATIONS

### 1. District Selector
- Show all 61 districts in dropdown
- Or use autocomplete search
- Show province grouping

### 2. Quick Actions
After district selected, show buttons:
- 🌾 What can I grow?
- 💰 Most profitable crops?
- 🏪 Where to sell?
- 📈 Market prices?

### 3. Message Formatting
- Use emojis for visual appeal (🌾 💰 🏪 📍 🥇)
- Format lists clearly
- Break long responses into sections
- Show sources count for credibility

### 4. Persistent Context
- Remember user's district throughout session
- Cache district profile to reduce API calls
- Allow user to change district anytime

### 5. Quick Facts Card
When district selected, show persistent card with:
- District name & province
- Natural region
- Main crops
- Best crop for profit

---

## 🔄 ERROR HANDLING

```javascript
const handleAPIError = async (apiCall) => {
  try {
    const response = await apiCall();
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return {
      error: true,
      message: 'Sorry, I encountered an error. Please try again.'
    };
  }
};
```

---

## ✅ TESTING CHECKLIST

- [ ] User can select district
- [ ] Complete profile loads on district selection
- [ ] User can ask general questions
- [ ] Market information displays correctly
- [ ] Profitability comparison works
- [ ] Error handling works (invalid district, network error)
- [ ] Session persists district throughout conversation
- [ ] User can change district mid-conversation
- [ ] Mobile responsive design works
- [ ] WhatsApp integration works (if applicable)

---

## 🚀 DEPLOYMENT TIPS

### Development
```bash
# Start API
cd /Users/providencemtendereki/agriculture-rag-platform
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Use production ASGI server
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment Variables
```bash
# .env file
API_BASE_URL=http://your-domain.com
CHROMADB_PATH=/path/to/chromadb
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 📚 ADDITIONAL RESOURCES

- **API Documentation:** http://localhost:8000/docs
- **System Description:** `COMPLETE_SYSTEM_DESCRIPTION.md`
- **Feature List:** `MISSING_FEATURES_IMPLEMENTED.md`
- **District Profiles:** 357 profiles across 40+ districts
- **Knowledge Base:** 16,311 documents

---

## 💡 EXAMPLE QUESTIONS TO HANDLE

**District Questions:**
- "What crops can I grow in Bindura?"
- "What is the natural region of Chivi?"
- "What are the main challenges in Harare?"

**Market Questions:**
- "Where can I sell my maize?"
- "What is the price of tobacco?"
- "Which markets pay the best?"

**Profitability Questions:**
- "Which crop is most profitable?"
- "How much can I make from tobacco?"
- "What are the costs for maize?"

**Technical Questions:**
- "When should I plant soya beans?"
- "How do I control fall armyworm?"
- "What fertilizer should I use?"

**General Questions:**
- "Tell me about conservation agriculture"
- "What is Pfumvudza?"
- "How do I get farm inputs?"

---

## ✨ SUMMARY

**Integration is Simple:**
1. User selects district → Call `/api/district/{district}/complete-profile`
2. User asks question → Call `/api/district/{district}/ask`
3. User asks about markets → Call `/api/district/{district}/markets`
4. User asks about profit → Call `/api/district/{district}/profitability-comparison`

**All endpoints return JSON that's easy to display in any chat interface! 🎉**
