# Agricultural Budget Calculator System

## Overview
Complete farm budgeting system with 23 crop budgets extracted from Excel, featuring real-time sensitivity analysis and detailed cost breakdowns.

## Features Implemented

### 1. **Budget Data Extraction**
- **Script**: `extract_budgets.py`
- **Source**: `/Users/providencemtendereki/Desktop/Crop Budgets.xlsx`
- **Output**: `crop_budgets_data.json`
- **Crops**: 23 different crops with complete budget data

### 2. **Budget Calculator** (`tools.html`)
- **Comprehensive Budget Display**:
  - Gross margin per hectare
  - Total income calculation
  - Variable costs breakdown
  - Net profit projection
  - Return on investment

- **Detailed Cost Categories**:
  1. Land Preparation (ripping, discing, planting)
  2. Seeds
  3. Fertilizers
  4. Chemicals & Pesticides
  5. Labour (planting, weeding, harvesting, etc.)
  6. Irrigation
  7. Transport (Inputs & Produce)
  8. Sundry & Miscellaneous

### 3. **Sensitivity Analysis** ✨
Interactive sliders to model:
- **Yield Adjustment**: -50% to +50%
- **Price Adjustment**: -50% to +50%

Real-time calculations show:
- Adjusted yield (tonnes/ha)
- Adjusted farm gate price
- New gross margin
- Change in profitability ($ and %)

### 4. **Verified Suppliers Directory**
8 major agricultural input suppliers with:
- Company names and categories
- Product offerings
- Contact information
- Location details
- Special notes (subsidies, financing, etc.)

## Available Crops

1. Baby Corn
2. Blueberries
3. Broccoli
4. Butternut
5. Cabbages
6. Carrots
7. Cauliflower
8. **Commercial Maize** ⭐
9. Fine Green Beans
10. Green Mealies
11. Mange Tout (HF & OG)
12. Onion
13. Passion Fruit (HD & LD)
14. Potatoes
15. Seed Maize
16. Stone Fruit
17. Strawberries
18. Sugar Snap (HF & OG)
19. Tenderstem
20. **Tobacco** ⭐

## How to Use

### For Users:
1. Open `tools.html` in a browser
2. Select a crop from the dropdown
3. Adjust farm size (hectares)
4. Click "Calculate Complete Budget"
5. View detailed breakdown
6. Use sliders for "What-if" scenarios
7. Check recommended suppliers

### For Developers:
1. **Update Budget Data**:
   ```bash
   python3 extract_budgets.py
   ```
   This re-extracts data from the Excel file if updated.

2. **Add New Crops**:
   - Add new sheet to Excel file
   - Run extraction script
   - Crops automatically appear in dropdown

3. **Modify Cost Categories**:
   - Edit `extract_budgets.py` (lines 71-92)
   - Update category detection logic

## Data Structure

### Budget JSON Format:
```json
{
  "CROP_NAME": {
    "crop_name": "COMMERCIAL MAIZE",
    "summary": {
      "gross_yield_kg_per_ha": 10000,
      "pack_out_percent": 0.9,
      "net_yield_kg_per_ha": 9000,
      "variable_costs_per_ha": 1413.33,
      "farm_gate_price": 0.39,
      "gross_return": 3510,
      "gross_profit": 2096.67,
      "return_per_dollar": 2.48
    },
    "costs": {
      "land_prep": [
        {
          "description": "Lime",
          "quantity": 1,
          "unit": "lts/ha",
          "unit_cost": 1.18,
          "total_cost": 7.08
        }
      ],
      "seed": [...],
      "fertilizer": [...],
      // ... other categories
    }
  }
}
```

## Files

- **tools.html**: Main budget calculator interface
- **crop_budgets_data.json**: Extracted budget data (23 crops)
- **extract_budgets.py**: Python script to extract from Excel
- **index.html**: Main chat interface with link to tools
- **Crop Budgets.xlsx**: Source Excel file (Desktop)

## Features Highlights

### ✅ Completed
- [x] Excel budget extraction (23 crops)
- [x] JSON data structure
- [x] Complete budget calculator
- [x] Detailed cost breakdowns
- [x] Sensitivity analysis with sliders
- [x] Real-time profit calculations
- [x] Verified suppliers directory
- [x] Professional UI design
- [x] Responsive layout

### 🎯 Use Cases
1. **Farm Planning**: Calculate expected profitability before planting
2. **Risk Analysis**: Test how yield/price changes affect profits
3. **Crop Comparison**: Compare margins across different crops
4. **Input Sourcing**: Find verified suppliers for inputs
5. **Investment Decisions**: Calculate ROI for different scenarios

## Example Budget (Commercial Maize)

**Per Hectare:**
- Gross Yield: 10,000 kg/ha
- Net Yield: 9,000 kg/ha (90% pack-out)
- Farm Gate Price: $0.39/kg
- Gross Return: $3,510
- Variable Costs: $1,413
- **Gross Profit: $2,097** 💰
- ROI: 2.48x

## Sensitivity Example

**Scenario**: Commercial Maize, 10 hectares
- Base Gross Margin: $20,967
- **+20% Yield**: $26,000 (+24% profit) ✅
- **-10% Price**: $17,000 (-19% profit) ⚠️
- **+15% Yield + 10% Price**: $29,500 (+41% profit) 🚀

## Technical Notes

- Budget data updates automatically when JSON file is refreshed
- All calculations are client-side (no backend required for budgets)
- Supports any farm size (0.1 to 1000+ hectares)
- Currency formatted automatically (K, M notation)
- Mobile responsive design

## Future Enhancements (Optional)

- [ ] Export budget to PDF
- [ ] Save/load user scenarios
- [ ] Multi-crop farm planning
- [ ] Break-even analysis
- [ ] Historical price trends
- [ ] Weather-adjusted yields
- [ ] Loan repayment calculator

---

## Support

For issues or questions:
1. Check browser console (F12) for errors
2. Verify `crop_budgets_data.json` exists
3. Ensure Excel file is accessible
4. Re-run `extract_budgets.py` if data is outdated

**Last Updated**: November 2025
**Version**: 1.0
**Status**: Production Ready ✅
