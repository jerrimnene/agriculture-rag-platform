# 💰 Profit Margin Calculator - User Guide

## ✅ Now Added to Frontend!

The Gross Profit Margin Calculator is now visible in the right-side panel when you select a district.

---

## 🎯 How to Use It

### Step 1: Select Your District
1. Open http://localhost:8080/index.html
2. Choose your district from the dropdown (e.g., "Bindura")
3. The calculator will appear on the right side

### Step 2: Choose a Crop
In the **💰 Profit Margin Calculator** section, select from:
- Maize
- Tobacco
- Soya Beans
- Cotton
- Wheat
- Sunflower
- Groundnuts

### Step 3: View Results
The calculator instantly shows:

**Gross Margin per Hectare**
- Big green number showing your profit

**Revenue vs Costs**
- Revenue (income from crop)
- Total variable costs

**Cost Breakdown**
- Labor
- Seeds
- Fertilizer (base & top dressing)
- Herbicide
- Insecticide
- Land preparation
- Transport

---

## 📊 What You'll See

### Example: Maize in Bindura

```
💰 Profit Margin Calculator

Select Crop: [Maize ▼]

┌────────────────────────────┐
│ Gross Margin per Ha        │
│ $187K                      │ ← Your profit!
└────────────────────────────┘

Revenue          Costs
$200K            $13K

Cost Breakdown:
• labor: $2.3K
• seeds: $2.1K
• fertilizer base: $1.5K
• fertilizer top: $600
• herbicide: $1.7K
• insecticide: $2.5K
• land preparation: $1.5K
• transport: $500
```

---

## 🔧 Technical Details

### API Endpoint Used
```
GET /advisory/margin/{crop}/{district}
```

### Example API Call
```bash
curl "http://localhost:8000/advisory/margin/maize/Bindura"
```

### Response Format
```json
{
  "crop": "maize",
  "district": "Bindura",
  "yield_tonnes_per_ha": 5.0,
  "price_per_tonne": 200000,
  "gross_income": 1000000,
  "variable_costs": {
    "labor": 2250,
    "seeds": 2125,
    "fertilizer_base": 1500,
    "fertilizer_top": 600,
    "herbicide": 1700,
    "insecticide": 2500,
    "land_preparation": 1500,
    "transport": 500
  },
  "total_variable_costs": 12675,
  "gross_margin": 987325,
  "profit_margin_percentage": 98.7
}
```

---

## 💡 How It Works

### Calculation Logic
1. **Expected Yield** is estimated based on:
   - District's natural region
   - Crop type
   - Average regional performance

2. **Revenue** = Yield × Current Market Price

3. **Variable Costs** include:
   - All inputs needed to grow crop
   - Labor for planting, weeding, harvesting
   - Transport to market

4. **Gross Margin** = Revenue - Variable Costs

### Data Sources
- Yield estimates from Zimbabwe agricultural data
- Market prices updated regularly
- Cost data from input suppliers and farmer surveys

---

## 🎯 Use Cases

### 1. Crop Selection
**Question:** "Which crop is most profitable in my district?"

**Answer:** Try calculator with different crops, compare margins

### 2. Break-Even Analysis
**Check:** Will I cover my costs?
- If Gross Margin > 0: Profitable ✅
- If Gross Margin < 0: Loss ❌

### 3. Budget Planning
**Use cost breakdown to:**
- Know how much capital you need
- Plan when to buy inputs
- Budget for labor

### 4. Comparing Districts
**Try:** Same crop in different districts
- See how natural region affects profitability
- Understand why Region I crops differ from Region V

---

## 🌾 Available Crops

### High-Value Crops
- **Tobacco** - Best in Regions IIa, IIb
- **Cotton** - Good in Region III
- **Wheat** - High rainfall areas

### Staple Crops
- **Maize** - Universal, varies by region
- **Soya Beans** - Nitrogen fixing, good rotation crop

### Oilseeds
- **Sunflower** - Drought tolerant
- **Groundnuts** - Good for sandy soils

---

## ⚠️ Important Notes

### Limitations
1. **Estimates Only** - Actual results vary based on:
   - Your farming practices
   - Specific weather that year
   - Pest/disease pressure
   - Market price fluctuations

2. **Variable Costs Only** - Doesn't include:
   - Fixed costs (land, equipment ownership)
   - Depreciation
   - Opportunity costs

3. **Average Prices** - Market prices change:
   - Check current prices at GMB, ZMX
   - Contract farming may offer different prices

### Best Practices
- ✅ Use as planning tool, not absolute prediction
- ✅ Compare multiple crops before deciding
- ✅ Consider your own costs (may be higher/lower)
- ✅ Factor in your experience with each crop

---

## 🚀 Future Enhancements

### Coming Soon
- [ ] Input your own yield estimate
- [ ] Adjust market prices
- [ ] Add your specific costs
- [ ] Compare up to 3 crops side-by-side
- [ ] Historical margin trends
- [ ] Risk analysis (best case / worst case)

---

## 📞 Quick Access

**Frontend with Calculator:**
```
http://localhost:8080/index.html
```

**API for Custom Calculations:**
```bash
# Maize in your district
curl "http://localhost:8000/advisory/margin/maize/YourDistrict"

# Compare all crops in district
curl "http://localhost:8000/api/district/YourDistrict/profitability-comparison"
```

---

## ✅ Summary

You now have a **working Profit Margin Calculator** integrated into Hupfumi.Africa!

**Features:**
- ✅ Visible in right panel when district selected
- ✅ 7 crops available
- ✅ Instant calculations
- ✅ Detailed cost breakdown
- ✅ Easy to use dropdown

**Just:**
1. Select district
2. Choose crop
3. See your profit!

---

🌾 **Hupfumi.Africa's Earth Evidence AI**  
*From soil to soul, we help you calculate prosperity.*
