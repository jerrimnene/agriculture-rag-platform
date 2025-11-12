# 🌧️ Rainfall Data - Quick Reference Card

## 📊 Data Overview
- **Coverage**: 91 districts, 10 provinces
- **Time Period**: 1981-2025 (45 years)
- **Source**: CHIRPS satellite data
- **Documents**: 551 added to vector database
- **Total DB**: 15,943 documents

## 🚀 Quick Start
```bash
cd ~/agriculture-rag-platform
./scripts/run.sh
# Open: http://localhost:8000
```

## 💬 Top 10 Questions to Try

1. **"What is the rainfall in Masvingo?"**
2. **"Which districts need irrigation?"**
3. **"Compare Harare and Bulawayo rainfall"**
4. **"Show me the driest districts"**
5. **"Rainfall trends in the 2010s"**
6. **"Is irrigation needed in Beitbridge?"**
7. **"Which crops suit Chipinge rainfall?"**
8. **"Climate risk for Gweru district"**
9. **"Most stable rainfall patterns"**
10. **"Manicaland rainfall changes"**

## 📈 Data Classifications

### Rainfall Levels (Annual)
| Level | Range | Districts |
|-------|-------|-----------|
| Low | < 1,000 mm | Beitbridge, Mwenezi |
| Low-Moderate | 1,000-1,500 mm | Bulawayo, Gwanda |
| Moderate | 1,500-2,000 mm | Masvingo, Gweru |
| Moderate-High | 2,000-2,500 mm | Harare, Mutare |
| High | > 2,500 mm | Chimanimani, Nyanga |

### Variability Classification
- **Stable**: <20% variation (Reliable)
- **Moderate**: 20-30% variation (Manageable)
- **High**: >30% variation (Risky)

## 🌾 Agricultural Recommendations

| Rainfall | Suitable Crops | Irrigation |
|----------|---------------|------------|
| < 1,500 mm | Drought-resistant | Essential |
| 1,500-2,000 mm | Moderate water needs | Supplementary |
| > 2,000 mm | Water-intensive | Optional |

## 📍 Notable Districts

### Wettest
- Chimanimani: 2,630 mm
- Chipinge Urban: 2,780 mm
- Nyanga: High rainfall

### Driest
- Beitbridge Urban: 540 mm
- Beitbridge: 690 mm
- Mwenezi: Low rainfall

### Most Stable
- Districts in Mashonaland East
- Some Manicaland districts
- Parts of Midlands

## 🔧 Maintenance Commands

### Test System
```bash
python test_rainfall_queries.py
```

### Re-ingest Data
```bash
python scripts/ingest_rainfall_data.py
```

### Check Database
```bash
python scripts/check_db.py
```

## 📚 Documentation Files

1. **RAINFALL_INTEGRATION_SUMMARY.md** - Executive overview
2. **RAINFALL_DATA_INTEGRATION.md** - Technical details
3. **RAINFALL_USAGE_GUIDE.md** - User guide with examples
4. **This file** - Quick reference

## ⚡ Key Features

✅ 45 years of historical data  
✅ District-level precision  
✅ Statistical analysis included  
✅ Trend identification  
✅ Agricultural context  
✅ Decade comparisons  
✅ Provincial summaries  
✅ Natural language queries  

## 🎯 Use Cases

1. **Farm Planning**: "Should I farm in District X?"
2. **Crop Selection**: "What grows well with this rainfall?"
3. **Irrigation**: "Do I need to invest in irrigation?"
4. **Risk Assessment**: "What's the climate risk here?"
5. **Comparison**: "Which district is better?"
6. **Trends**: "Is rainfall decreasing?"

## 📞 Quick Help

- **No results?** Be more specific with district names
- **Wrong results?** Try rephrasing your question
- **System down?** Check if platform is running
- **Need more info?** See detailed documentation files

---

**🌾 Your agriculture platform now has comprehensive rainfall intelligence! 🌧️**

*Last updated: November 11, 2025*
