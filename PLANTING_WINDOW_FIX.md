# Fix: Incorrect Maize Planting Recommendations

## Problem Identified

The AgriEvidence system was generating incorrect recommendations about maize planting in Chimanimani District, stating:
> "maize can be planted year-round due to its high rainfall (1000-2000mm)"

This is **incorrect** because:
1. Maize is an **annual crop** that follows seasonal planting patterns, even in high-rainfall regions
2. In Zimbabwe, maize planting aligns with the **rainy season** (typically October/November - March/April)
3. "Year-round planting" would require continuous irrigation infrastructure, which is not typical practice
4. Even in Region I (highest rainfall), maize has **specific planting windows**

## Root Cause

The issue was in `src/geo/provinces.json`:

**Original Data:**
```json
"Region I": {
  "rainfall": "1000mm+",
  "description": "Specialized and diversified farming (tea, coffee, fruits, forestry)",
  "growing_season": "Year-round with irrigation",
  "recommended_crops": ["tea", "coffee", "macadamia", "timber", "horticulture"]
}
```

The "Year-round with irrigation" growing season was meant for **perennial crops** (tea, coffee, timber), not annual crops like maize. The LLM was misinterpreting this as applying to all crops.

## Solution Implemented

### 1. Updated Natural Region Definitions
Added specific `maize_planting_window` field for all regions in `provinces.json`:

**Region I (Chimanimani):**
```json
"Region I": {
  "rainfall": "1000mm+",
  "description": "Specialized and diversified farming (tea, coffee, fruits, forestry)",
  "growing_season": "Main season: Nov-Apr; Perennial crops year-round",
  "maize_planting_window": "November-December (main); February-March (possible second season)",
  "recommended_crops": ["tea", "coffee", "macadamia", "timber", "horticulture"]
}
```

**Other Regions:**
- **Region IIa:** "November-December (optimal planting window)"
- **Region IIb:** "November-December (with first rains)"
- **Region III:** "November-December (short-season varieties recommended)"
- **Region IV:** "December-early January (early maturing varieties only)"
- **Region V:** "Not recommended without irrigation; if irrigated, plant Nov-Dec"

### 2. Enhanced Context Enricher
Updated `src/geo/enrich_context.py` to:
- Include maize planting windows in location context
- Add explicit instruction: "For planting times, ALWAYS use the specific 'Maize Planting Window' provided"
- Prevent year-round planting suggestions for annual crops

### 3. Updated Geo Context Module
Modified `src/geo/geo_context.py` to include `maize_planting_window` in formatted context output.

## Expected Behavior Now

When asked "When should I plant maize in Chimanimani District?", the system should now respond with:

> "In the Chimanimani District of Manicaland Province, which falls under Region I, maize should be planted during the **main planting season in November-December** to coincide with the start of the rainy season. A **possible second planting window** exists in **February-March** if conditions permit. 
>
> While Region I has high rainfall (1000-2000mm annually), maize planting still follows Zimbabwe's seasonal patterns. The 'year-round' classification for Region I refers to perennial crops like tea, coffee, and timber—not annual crops like maize."

## Verification

Run this test to verify:
```bash
cd /Users/providencemtendereki/agriculture-rag-platform
python3 -c "
from src.geo.geo_context import GeoContext

geo = GeoContext()
district_info = geo.get_district_by_name('Chimanimani')
context = geo.format_context(district_info)

print('Maize Planting Window:', context['maize_planting_window'])
print('Growing Season:', context['growing_season'])
"
```

Expected output:
```
Maize Planting Window: November-December (main); February-March (possible second season)
Growing Season: Main season: Nov-Apr; Perennial crops year-round
```

## Files Modified

1. `src/geo/provinces.json` - Added maize planting windows to all natural regions
2. `src/geo/enrich_context.py` - Enhanced prompt instructions and location context formatting
3. `src/geo/geo_context.py` - Updated format_context to include maize planting windows

## Impact

This fix ensures that:
- ✅ Maize planting recommendations are **seasonally accurate**
- ✅ High-rainfall regions don't get misleading "year-round" advice for annual crops
- ✅ Users receive **specific planting windows** tailored to their district and region
- ✅ The distinction between perennial and annual crops is clear
- ✅ Recommendations follow Zimbabwe's established agricultural practices

## Testing Recommendation

Test the full RAG pipeline with queries like:
- "When should I plant maize in Chimanimani?"
- "Can I plant maize year-round in Region I?"
- "What is the best time to plant maize in [any district]?"

The system should now provide accurate, season-specific guidance.
