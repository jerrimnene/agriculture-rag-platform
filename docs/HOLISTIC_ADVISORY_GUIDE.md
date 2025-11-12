# 🌾 Holistic Agricultural Advisory System

## Overview

The Holistic Advisory System is a comprehensive platform for providing district-specific, profit-focused agricultural recommendations that integrate:

- **District Context**: Climate, soil, rainfall, agro-zones, and farming difficulties
- **Gross Margin Analysis**: Profitability calculations based on yields and costs
- **Market Intelligence**: Local markets, buyers, transport costs, and nearby urban opportunities
- **Adaptive Recommendations**: Context-aware strategies for challenging farming scenarios
- **Supply Chain Optimization**: Alternative sourcing and value-addition strategies

## Key Features

### 1. District Context Engine
Provides comprehensive district-specific data:
- Geographic and agro-ecological information
- Primary crops and livestock
- Market access and trading centers
- Farming difficulty assessments
- Seasonal farming calendars
- Nearby urban market opportunities

### 2. Gross Margin Calculator
Calculates profitability for agricultural enterprises:
- Income = Yield (tonnes/ha) × Price (ZWL/tonne)
- Variable costs: labor, seeds, fertilizer, water, transport, etc.
- **Gross Margin = Income - Variable Costs**
- Profit margin percentage and per-tonne analysis
- Breakeven analysis (yield and price)
- Scenario analysis for different yield/price combinations

### 3. Adaptive Recommendation Engine
Generates intelligent recommendations:
- What to plant based on district conditions
- Why specific crops are recommended
- Costs, margins, and profitability insights
- Market opportunities and challenges
- Mitigation strategies for difficult conditions
- Alternative crops if primary choice fails
- Supply chain options (cooperatives, urban markets, value addition)

### 4. Holistic Advisory
Integrates all systems for comprehensive guidance covering:
- Viability scoring (0-100)
- Profitability assessment
- Market outlook
- Risk assessment
- Investment requirements
- Implementation timeline

## API Endpoints

### Districts

```bash
# List all available districts
GET /advisory/districts

# Get comprehensive district overview
GET /advisory/district/{district}

# Get viable crops for a district
GET /advisory/district/{district}/viable-crops

# Get difficulty assessment
GET /advisory/difficulty/{district}

# Get seasonal farming calendar
GET /advisory/seasonal-calendar/{district}

# Get nearby districts for supply chains
GET /advisory/nearby-districts/{district}
```

### Gross Margin Analysis

```bash
# Get margin analysis for a crop in a district
GET /advisory/margin/{crop}/{district}
?yield_per_ha=8.0&price_per_tonne=200000

# Compare crops in a district
POST /advisory/compare-crops/{district}
Body: ["maize", "sorghum", "groundnuts"]

# Get breakeven analysis
GET /advisory/breakeven/{crop}/{district}

# Get cost breakdown for a crop
GET /advisory/costs/{crop}

# Scenario analysis
POST /advisory/scenarios/{crop}/{district}
Body: [
  {"name": "Optimistic", "yield": 8.0, "price": 220000},
  {"name": "Expected", "yield": 7.0, "price": 200000},
  {"name": "Pessimistic", "yield": 5.0, "price": 180000}
]
```

### Holistic Advisory

```bash
# Get comprehensive advisory
GET /advisory/holistic/{crop}/{district}

# Get brief advisory summary
GET /advisory/advisory-summary/{crop}/{district}

# Get market strategy
GET /advisory/market/{district}/{crop}

# Batch advisory for multiple crops/districts
POST /advisory/batch-advisory
Body: [
  {"crop": "maize", "district": "Harare"},
  {"crop": "millet", "district": "Binga"}
]
```

## Example Use Cases

### Case 1: Farmer in Binga Wants to Plant Maize

```bash
# Get holistic advisory
curl "http://localhost:8000/advisory/holistic/maize/Binga"
```

**Response includes:**
```json
{
  "holistic_assessment": "❌ MAIZE IN BINGA IS NOT RECOMMENDED. 450mm rainfall is below maize's 600mm minimum requirement. Expected yield: 1.5 tonnes/ha (vs 8 tonnes in Harare)...",
  "viability_score": 20,
  "costs_and_profitability": {
    "gross_income": "300,000 ZWL/ha",
    "variable_costs": "450,000 ZWL/ha",
    "gross_margin": "-150,000 ZWL/ha",
    "recommendation": "🔴 NOT PROFITABLE - Do NOT invest in this crop in this district"
  },
  "alternative_strategies": [
    {
      "crop": "Millet",
      "why": "Better drought tolerance than maize",
      "expected_yield": "2-3 tonnes/ha",
      "margin": "400,000-600,000 ZWL/ha"
    },
    {
      "crop": "Goat farming",
      "why": "Drought-proof income",
      "margin": "500,000-1,000,000 ZWL per animal"
    }
  ],
  "supply_chain_options": [
    {
      "option": "Direct sourcing from Hwange traders",
      "description": "Buy grains wholesale (150km), transport cost 150 ZWL/bag, sell for 30% markup",
      "estimated_profit": "30-50 ZWL per bag"
    }
  ],
  "nearby_opportunities": {
    "hwange": {
      "distance": "150km",
      "market_demand": "High - mining town 15,000+",
      "margin_opportunity": "15-30% markup on bulk purchases"
    }
  }
}
```

### Case 2: Compare Crops in Harare

```bash
curl -X POST "http://localhost:8000/advisory/compare-crops/Harare" \
  -H "Content-Type: application/json" \
  -d '["maize", "sorghum", "groundnuts", "vegetables"]'
```

**Response shows:**
- Maize: 1,100,000 ZWL/ha gross margin ✅ Best
- Vegetables: 8,000,000 ZWL/ha gross margin 🌟 Excellent
- Sorghum: 420,000 ZWL/ha gross margin 🟢 Good
- Groundnuts: 650,000 ZWL/ha gross margin 🟢 Good

### Case 3: Breakeven Analysis

```bash
curl "http://localhost:8000/advisory/breakeven/maize/Harare"
```

**Response shows:**
```json
{
  "crop": "maize",
  "district": "Harare",
  "total_variable_costs": 3500000,
  "current_market_price": 200000,
  "breakeven_yield_tonnes_per_ha": 1.75,
  "breakeven_price_per_tonne": 437500,
  "typical_yield": 8.0,
  "risk_assessment": "low_risk"
}
```

*Interpretation: Farmer only needs 1.75 tonnes/ha to break even, but can achieve 8 tonnes - very safe margin!*

## Data Structure

### District Model
```json
{
  "district": "Binga",
  "province": "Matabeleland North",
  "agro_zone": "IV",
  "rainfall_mm": 450,
  "soil_type": "Sandy, shallow",
  "elevation": 700,
  "primary_crops": ["millet", "sorghum", "groundnuts"],
  "primary_livestock": ["goats", "cattle", "poultry"],
  "challenges": ["drought", "low_rainfall", "sandy_soils"]
}
```

### Margin Model
```json
{
  "crop": "maize",
  "district": "Harare",
  "yield_tonnes_per_ha": 8.0,
  "price_per_tonne": 200000,
  "gross_income": 1600000,
  "variable_costs": {
    "labor": 2250000,
    "seeds": 212500,
    "fertilizer_base": 1500000,
    "fertilizer_top": 600000,
    "herbicide": 1700000,
    "insecticide": 2500000,
    "land_preparation": 1500000,
    "transport": 500000
  },
  "total_variable_costs": 10662500,
  "gross_margin": 1100000,
  "gross_margin_per_tonne": 137500,
  "profit_margin_percentage": 68.8
}
```

## Difficulty Levels

### Low Difficulty (Harare, Chitungwiza)
- Adequate rainfall (750mm+)
- Good soils
- Excellent market access
- Standard farming practices sufficient

### Medium Difficulty (Bulawayo)
- Moderate rainfall (550mm)
- Variable soils
- Good market access
- Requires water conservation

### High Difficulty (Binga)
- Low rainfall (450mm)
- Poor soils (sandy, shallow)
- Limited market access
- Requires adaptive strategies:
  - Drought-resistant crops
  - Water harvesting
  - Value addition
  - Supply chain alternatives

## Key Recommendations for Difficult Districts (Binga)

### 1. Crop Selection
- ✅ **Millet**: 2-3 tonnes/ha, 400mm rainfall minimum
- ✅ **Sorghum**: 2 tonnes/ha, deep roots, drought-resistant
- ✅ **Groundnuts**: 1.5 tonnes/ha, nitrogen-fixing, drought-tolerant
- ✅ **Goat Farming**: Drought-proof, high value (800,000-1,000,000 ZWL/animal)
- ❌ **Maize**: Requires 600mm+ rainfall, only 1.5 tonnes/ha in Binga

### 2. Water Management
- Build water harvesting ponds (3-5 per hectare)
- Implement zai pits for tree planting
- Use contour ridges to reduce runoff
- Practice conservation agriculture with mulching

### 3. Market Strategy
- **Option A**: Direct production + local markets (limited buyers)
- **Option B**: Source from Hwange (150km), add 30% markup locally
- **Option C**: Join cooperatives for bulk transport discount
- **Option D**: Supply urban centers (Victoria Falls, Hwange) for 50-100% markup

### 4. Income Diversification
- Process grains (milling, flour production)
- Livestock rearing (small ruminants, poultry)
- Honey production from bees
- Value-added products for urban markets

## Cost Breakdown (Per Hectare in ZWL)

### Maize (Harare)
- Labor: 2,250,000 (35%)
- Fertilizers: 2,100,000 (33%)
- Seeds: 212,500 (3%)
- Chemicals (herbicides, insecticides): 4,200,000 (24%)
- Land prep + transport: 2,000,000 (5%)
- **Total: 10,662,500 ZWL/ha**

### Sorghum (Binga)
- Labor: 1,800,000 (40%)
- Fertilizer: 900,000 (20%)
- Seeds: 1,000,000 (22%)
- Chemicals: 800,000 (18%)
- **Total: 4,500,000 ZWL/ha** (Lower costs in difficult areas)

## Integration with RAG System

You can also combine holistic advisory with RAG queries:

```python
# Get holistic advisory for Binga+Maize
advisor_response = requests.get(
    "http://localhost:8000/advisory/holistic/maize/Binga"
)

# Then query RAG for detailed practices
rag_response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What are drought-resistant crop varieties for sandy soils?",
        "district": "Binga"
    }
)

# Combine responses for comprehensive guidance
```

## Future Enhancements

1. **Weather Integration**: Real-time drought warnings and seasonal forecasts
2. **Price Forecasting**: Predict market prices to optimize sales timing
3. **Farmer Profiles**: Personalized recommendations based on farm size, family size, resources
4. **Mobile App**: WhatsApp/SMS interface for farmers without smartphones
5. **Government Programs**: Integration with subsidy and support programs
6. **Cooperative Network**: Connect farmers for bulk inputs and marketing
7. **Extension Officer Dashboard**: Track farmer progress and outcomes

## Support & Troubleshooting

### Common Questions

**Q: Why is maize not recommended in Binga?**
A: Binga has 450mm rainfall annually, but maize needs 600mm+. Yield drops to 1.5 tonnes/ha (vs 8 in Harare), making it unprofitable even if market prices rise.

**Q: What's a good margin percentage?**
A: 30%+ is good, 50%+ is excellent. Below 10% is risky.

**Q: How can I access Victoria Falls market from Binga?**
A: 200km distance, 4-5 hours drive. Join cooperatives to share transport, or supply processed goods with higher margins (50-100% markup on specialty items).

**Q: What if I insist on growing maize in Binga?**
A: You'd need irrigation (expensive), and even then margins would be thin. Consider contract farming with commodity traders for guaranteed prices.

---

**For API Documentation**: Visit http://localhost:8000/docs
**For Support**: Check adjacent documentation files or contact system administrator
