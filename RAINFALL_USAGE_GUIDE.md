# 🌧️ Rainfall Data Usage Guide

## Quick Start

The rainfall data from CHIRPS (1981-2025) has been successfully integrated into your Agriculture RAG Platform. You can now ask climate-informed questions and get detailed rainfall analysis.

## How to Use

### 1. Start the Platform
```bash
cd ~/agriculture-rag-platform
./scripts/run.sh
```

Then open http://localhost:8000 in your browser.

### 2. Ask Questions

Simply type your question in the chat interface. Here are example questions that work well:

## Sample Questions by Category

### 📊 District-Level Rainfall Information
```
- What is the average rainfall in Masvingo district?
- Tell me about rainfall patterns in Harare
- Show me rainfall data for Gweru
- What is the rainfall range in Bulawayo?
- How much rain does Chipinge get annually?
```

### 🏞️ Regional & Provincial Comparisons
```
- Compare rainfall across Mashonaland provinces
- Which province has the most rainfall?
- Show me the driest districts in Zimbabwe
- Compare Harare and Bulawayo rainfall
- What is the spatial rainfall variability in Matabeleland?
```

### 📈 Historical Trends & Temporal Analysis
```
- How has rainfall changed in the 2010s compared to 1980s?
- What was the rainfall pattern in Marondera during the 1990s?
- Show rainfall trends over the last 10 years in Masvingo
- Compare rainfall between decades in Gweru
- Has rainfall increased or decreased in Manicaland?
```

### 🌾 Agricultural Planning Questions
```
- Is irrigation needed in Beitbridge?
- Which crops are suitable for Gwanda based on rainfall?
- What is the climate risk for farming in Chipinge?
- Should I invest in irrigation for my farm in Hwange?
- Which districts are best for rainfed agriculture?
```

### 🎯 Climate Risk Assessment
```
- What is the climate risk in Bulawayo?
- Show me districts with stable rainfall patterns
- Which areas have the most variable rainfall?
- Where should I farm to minimize drought risk?
- What's the rainfall reliability in Masvingo?
```

### 💧 Drought & Water Management
```
- Which districts are most prone to drought?
- Where do I need supplementary irrigation?
- Show me low rainfall districts
- What's the drought risk in Region V?
- Which areas need water conservation practices?
```

## Real Query Examples from Testing

### Query 1: "What is the average rainfall in Masvingo district?"
**Response includes:**
- Historical statistics (1981-2025)
- Average: 1,940 mm annually
- Range: 290-3,330 mm
- Pattern: Moderate Rainfall, Moderately Variable
- Recent 5-year average
- Agricultural implications

### Query 2: "Tell me about rainfall patterns in Harare"
**Response includes:**
- Harare: 2,200 mm average
- Harare Rural: 2,040 mm average
- Epworth: 2,170 mm average
- Pattern: Moderate-High Rainfall, Moderately Variable
- Suitable for moderate to water-intensive crops
- Declining rainfall trend in recent decade

### Query 3: "Climate risk assessment for Bulawayo district"
**Response includes:**
- Average: 1,320 mm (Low-Moderate Rainfall)
- Pattern: Highly Variable
- Recent decade: 1,400 mm
- 2020s trend: 1,080 mm (declining)
- High climate risk due to variability
- Irrigation highly recommended

## Understanding the Responses

### Rainfall Classifications
- **Low Rainfall**: < 1,000 mm (< 1m)
- **Low-Moderate**: 1,000-1,500 mm
- **Moderate**: 1,500-2,000 mm
- **Moderate-High**: 2,000-2,500 mm
- **High Rainfall**: > 2,500 mm (> 2.5m)

### Variability Levels
- **Relatively Stable**: Low year-to-year variation (<20% CV)
- **Moderately Variable**: Moderate variation (20-30% CV)
- **Highly Variable**: High variation (>30% CV)

### Agricultural Implications in Responses

The system automatically provides:
- **Crop Suitability**: Based on water requirements
- **Irrigation Needs**: Whether irrigation is essential, supplementary, or optional
- **Climate Risk**: Based on rainfall variability
- **Recent Trends**: Whether rainfall is increasing, stable, or declining

## API Usage (For Developers)

```python
import requests

# Query the system
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is the rainfall pattern in Masvingo?",
        "location": {"district": "Masvingo"}
    }
)

result = response.json()
print(result['response'])
```

## Data Coverage

✅ **91 districts** across Zimbabwe (90 with complete data)  
✅ **10 provinces** with provincial summaries  
✅ **45 years** of historical data (1981-2025)  
✅ **5 decades** for temporal analysis  
✅ **CHIRPS satellite data** - scientifically validated  

### Districts Covered:
All major districts including: Harare, Bulawayo, Masvingo, Gweru, Mutare, Chipinge, Beitbridge, Gwanda, Marondera, Bindura, Kariba, Hwange, Lupane, and many more.

## Tips for Best Results

1. **Be Specific**: Mention district names for detailed information
2. **Ask About Trends**: The system has 45 years of data for trend analysis
3. **Compare Locations**: Ask to compare multiple districts or provinces
4. **Think Agricultural**: Frame questions around farming needs
5. **Consider Time**: Ask about different decades for historical context

## Example Use Cases

### Use Case 1: New Farmer Planning
**Question**: "I want to start farming in Chivi district. What should I know about the rainfall?"

**What you'll get**:
- Average rainfall (low-moderate: ~1,370 mm)
- Variability assessment (highly variable)
- Crop recommendations (drought-resistant crops)
- Irrigation requirements (highly recommended)
- Climate risk assessment
- Recent trends

### Use Case 2: Crop Selection
**Question**: "Which districts are suitable for water-intensive crops?"

**What you'll get**:
- List of high-rainfall districts (>2,000 mm)
- Stability assessment
- Specific district recommendations
- Manicaland, some Mashonaland districts

### Use Case 3: Risk Assessment
**Question**: "Where should I farm to minimize drought risk?"

**What you'll get**:
- Districts with high average rainfall
- Low variability locations
- Stable pattern districts
- Specific recommendations

### Use Case 4: Irrigation Investment
**Question**: "Should I invest in irrigation for my farm in Beitbridge?"

**What you'll get**:
- Beitbridge rainfall: ~690 mm (very low)
- High variability assessment
- Clear recommendation: Irrigation essential
- Cost-benefit context

## Data Source Information

- **Source**: CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)
- **Provider**: UC Santa Barbara & USGS
- **Validation**: Peer-reviewed, widely used for agricultural planning
- **Resolution**: District-level precision
- **Update Frequency**: Annual (currently 1981-2025)

## Limitations & Considerations

1. **One District Missing**: Mvurwi has incomplete data
2. **Averages**: Data shows annual averages, not seasonal distribution
3. **Satellite Data**: CHIRPS is satellite-based, validated with ground stations
4. **Future Projections**: This is historical data, not climate predictions
5. **Local Variations**: Microclimates within districts may vary

## Need Help?

- **Platform Issues**: Check `README.md` for troubleshooting
- **Data Questions**: See `RAINFALL_DATA_INTEGRATION.md` for technical details
- **Test Queries**: Run `python test_rainfall_queries.py` to verify system

## Next Steps

1. ✅ Start asking questions about rainfall patterns
2. ✅ Use this data for informed agricultural planning
3. ✅ Combine with other platform features (crop guides, market data)
4. ✅ Make climate-smart farming decisions

---

**Your Agriculture RAG Platform now has comprehensive climate intelligence! 🌾🌧️**
