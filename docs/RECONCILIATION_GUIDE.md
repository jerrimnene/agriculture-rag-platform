# Multi-Source Reconciliation System - Quick Reference Guide

## What is it?

The reconciliation system **automatically detects when different expert sources disagree** and provides balanced, transparent recommendations to farmers.

---

## When Does It Activate?

The system runs automatically when:
- A query retrieves **2 or more source documents**
- The sources contain **actionable recommendations**
- The recommendations are **on the same topic**

---

## What Gets Reconciled?

### 8 Topic Categories

1. **Planting Time** - When to plant crops
2. **Fertilizer** - Nutrient application rates and timing
3. **Pest Control** - Disease and pest management
4. **Irrigation** - Water management practices
5. **Variety** - Seed/cultivar selection
6. **Spacing** - Plant density and layout
7. **Harvest** - Harvest timing and methods
8. **Storage** - Post-harvest handling

---

## Authority Scoring (0-100)

### Organization Tiers

| Organization | Base Score | With Zimbabwe Bonus | With Recency Bonus |
|--------------|------------|---------------------|-------------------|
| **AGRITEX** | 85 | 105 → **100** | Up to **100** |
| **ICRISAT** | 95 | 115 → **100** | Up to **100** |
| **FAO** | 90 | 110 → **100** | Up to **100** |
| **AMA/TIMB** | 80 | 100 | Up to **100** |
| **Universities** | 75 | 95 | Up to 100 |
| **USAID** | 70 | 90 | Up to 95 |

### Bonuses Applied

- **Zimbabwe-specific**: +20 points
- **Southern Africa/SADC**: +15 points  
- **Current year data**: +15 points
- **1 year old**: +12 points
- **2 years old**: +8 points

---

## Conflict Types Detected

### 1. Timing Conflicts 
**Example**: "Plant in October" vs "Plant in November"

### 2. Quantity Conflicts
**Example**: "Apply 200kg/ha" vs "Apply 150kg/ha"

### 3. Method Conflicts
**Example**: "Broadcast fertilizer" vs "Band application"

### 4. Recommendation vs Warning ⚠️
**Example**: "Use pesticide X" vs "Avoid pesticide X"  
**Note**: Safety warnings are ALWAYS prioritized

### 5. General Conflicts
Semantic disagreements not fitting other categories

---

## Reading Reconciliation Results

### API Response Structure

```json
{
  "reconciliation": {
    "has_conflicts": true,
    "total_sources": 3,
    "conflicts_found": 1,
    "summary": "⚠️ Found 1 disagreement...",
    
    "conflicts": [
      {
        "topic": "planting_time",
        "conflict_type": "timing",
        "severity": "high",
        "source_1": {
          "organization": "AGRITEX",
          "recommendation": "Plant in October",
          "authority": 100
        },
        "source_2": {
          "organization": "FAO", 
          "recommendation": "Plant in November",
          "authority": 90
        },
        "display": "Human-readable conflict explanation"
      }
    ],
    
    "consensus_recommendations": [
      {
        "topic": "planting_time",
        "recommendation": "Follow AGRITEX timing...",
        "confidence": "moderate",
        "authority_score": 95,
        "supporting_sources": 3
      }
    ]
  }
}
```

---

## Interpreting Confidence Levels

### HIGH Confidence ✅
- All sources agree
- No conflicts detected
- Strong consensus
- **Action**: Follow recommendation with confidence

### MODERATE Confidence ⚠️
- Sources disagree, but reconciled
- Weighted by authority and relevance
- Balanced recommendation provided
- **Action**: Follow highest authority source, consult local extension

### LOW Confidence ❌
- Significant disagreement
- Multiple high-severity conflicts
- Insufficient data
- **Action**: Consult AGRITEX before proceeding

---

## Common Scenarios

### Scenario 1: No Conflicts ✅

```json
{
  "has_conflicts": false,
  "summary": "✅ All 5 sources are in agreement."
}
```

**What it means**: All expert sources agree. Follow the recommendation confidently.

---

### Scenario 2: Timing Disagreement ⚠️

```
⚠️ Source Disagreement on Planting Time

AGRITEX (authority: 100) - Zimbabwe Expert:
  "Plant maize in October to early November"

FAO (authority: 90) - Regional Expert:
  "Plant from mid-November to December"

Recommendation: Prioritize AGRITEX guidance as it has 
higher authority for Zimbabwe. Consult local extension 
officer for your specific Natural Region.
```

**What to do**: 
1. Recognize both sources are reputable
2. Follow AGRITEX (higher Zimbabwe authority)
3. Consider your specific location and rainfall pattern
4. Consult local extension if uncertain

---

### Scenario 3: Safety Conflict 🚨

```
CRITICAL: Pesticide Recommendation vs Warning

Commercial Guide (authority: 40):
  "Use chlorpyrifos for armyworm control"

AGRITEX (authority: 100):
  "AVOID chlorpyrifos - health and environmental concerns"

Recommendation: ALWAYS follow current government advisories.
Do NOT use banned substances. Consult AGRITEX for approved 
alternatives.
```

**What to do**:
1. **NEVER** ignore safety warnings
2. Always prioritize current government guidance
3. Use approved alternatives only
4. Contact AGRITEX for approved pesticide list

---

## Using the System

### Via API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "When should I plant tobacco in Bindura?",
    "district": "Bindura"
  }'
```

### Via Python

```python
from src.agents.rag_agent import AgricultureRAGAgent
from src.embeddings.vector_store import VectorStore

# Initialize
vector_store = VectorStore(...)
agent = AgricultureRAGAgent(vector_store)

# Query with reconciliation
result = agent.query(
    user_query="What fertilizer rate for maize?",
    district="Harare"
)

# Check reconciliation
if result['reconciliation'] and result['reconciliation']['has_conflicts']:
    print("⚠️ Experts disagree!")
    print(result['reconciliation']['summary'])
    
    for conflict in result['reconciliation']['conflicts']:
        print(conflict['display'])
else:
    print("✅ All sources agree")
```

---

## Best Practices

### For Farmers

1. **Trust the system** - It weighs sources intelligently
2. **Check authority scores** - Higher = more reliable for Zimbabwe
3. **When in doubt** - Consult local AGRITEX extension officer
4. **Consider your context** - Natural Region, soil type, rainfall
5. **Never ignore warnings** - Safety first always

### For Developers

1. **Ensure metadata is complete** - organization, geographic_scope, year
2. **Use consistent organization names** - "AGRITEX" not "Agritex Zimbabwe Dept"
3. **Keep data current** - Recency bonus rewards fresh data
4. **Test with real queries** - Use `test_reconciliation.py`
5. **Monitor conflict rates** - High rates may indicate data quality issues

---

## Troubleshooting

### "No reconciliation field in response"

**Cause**: Query returned <2 sources  
**Solution**: Normal behavior - reconciliation only runs with multiple sources

### "Reconciliation is null"

**Cause**: Reconciliation failed (logged as warning)  
**Solution**: Query still succeeds, check logs for details

### "No recommendations extracted"

**Cause**: Sources don't contain actionable text patterns  
**Solution**: Review recommendation extraction patterns in code

### "All sources have low authority"

**Cause**: Using secondary sources without primary research  
**Solution**: Add more authoritative sources (AGRITEX, ICRISAT, FAO)

---

## Testing

### Run Test Suite

```bash
cd /Users/providencemtendereki/agriculture-rag-platform
python test_reconciliation.py
```

### Expected Tests

1. ✅ Conflicting planting dates
2. ✅ Fertilizer application rates  
3. ✅ Sources in agreement
4. ✅ Recommendation vs warning

---

## Key Metrics

- **Reconciliation speed**: ~50-100ms for 5 sources
- **Pattern accuracy**: High for structured recommendations
- **Authority calculation**: Instant (lookup-based)
- **Conflict detection**: Semantic + keyword-based

---

## Advanced Features

### Custom Authority Weights

Modify `SourceAuthority.AUTHORITY_SCORES` to adjust organizational rankings:

```python
AUTHORITY_SCORES = {
    'icrisat': 95,
    'agritex': 85,
    'my_research_station': 70,  # Add custom
    ...
}
```

### Custom Topic Categories

Add new topics in `RecommendationExtractor.TOPIC_KEYWORDS`:

```python
TOPIC_KEYWORDS = {
    'planting_time': [...],
    'livestock_feeding': ['feed', 'fodder', 'nutrition'],  # New
    ...
}
```

---

## Support

- **Documentation**: `PHASE3_RECONCILIATION_SUMMARY.md`
- **Source code**: `src/reconciliation/source_reconciler.py`
- **Tests**: `test_reconciliation.py`
- **Issues**: Check logs for detailed error messages

---

## Summary

The Multi-Source Reconciliation System:

✅ Detects when experts disagree  
✅ Weights sources by authority and relevance  
✅ Provides transparent, balanced recommendations  
✅ Prioritizes safety warnings  
✅ Handles edge cases gracefully  
✅ Runs automatically with zero configuration  

**Trust the system. Follow the guidance. Consult extension when uncertain.**

---

*Version 1.0.0 | January 2025 | AgriRAG Development Team*
