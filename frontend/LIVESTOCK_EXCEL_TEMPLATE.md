# 🐄 Livestock Budgets Excel Template Structure

## Sheet Structure (Same as Crops)

Each livestock species gets **ONE SHEET** in the Excel file.

### Sheet Names (16 Livestock Budgets):
1. BEEF CATTLE - COMMUNAL
2. BEEF CATTLE - FEEDLOT
3. DAIRY CATTLE - ZERO GRAZING
4. GOATS - MEAT
5. GOATS - MILK
6. SHEEP - WOOL
7. SHEEP - MEAT
8. PIGS - INTENSIVE
9. PIGS - FREE RANGE
10. BROILERS - 100 BIRDS
11. LAYERS - 500 BIRDS
12. INDIGENOUS CHICKENS
13. RABBITS - MEAT
14. QUAIL - EGGS
15. TURKEYS - MEAT
16. DUCKS - MEAT

---

## Excel Layout (Rows & Columns)

### SUMMARY SECTION (Rows 4-15)

| Row | Col A | Col B | Col C | Col D | Col E (VALUE) |
|-----|-------|-------|-------|-------|---------------|
| 4 | | **GROSS MARGIN SUMMARY** | | | |
| 5 | | Herd/Flock Size | | | 10 head/birds |
| 6 | | Gross Liveweight Yield (kg) | | | 2500 |
| 7 | | Mortality Rate (%) | | | 5 |
| 8 | | Net Yield (kg) | | | 2375 |
| 9 | | Farm Gate Price ($/kg) | | | 4.50 |
| 10 | | GROSS RETURN ($) | | | 10687.50 |
| 11 | | Total Variable Costs ($) | | | 6500.00 |
| 12 | | **GROSS PROFIT ($)** | | | **4187.50** |
| 13 | | Gross Profit per Head/Bird ($) | | | 418.75 |
| 14 | | Production Cycle (days) | | | 365 |
| 15 | | Cycles per Year | | | 1 |

---

### COST BREAKDOWN (Rows 17+)

#### Column Headers (Row 17):
| Col A | Col B | Col C | Col D | Col E |
|-------|-------|-------|-------|-------|
| **CATEGORY** | **ITEM DESCRIPTION** | **QUANTITY** | **UNIT** | **TOTAL COST ($)** |

---

#### Cost Categories & Example Items:

### 1. FEED COSTS
```
Row 18: FEED COSTS                                     [TOTAL]
Row 19:         Concentrate feed          500    kg    250.00
Row 20:         Grazing supplement        200    kg    150.00
Row 21:         Minerals & salt blocks     12    units  60.00
Row 22:         Forage (hay/silage)      1000    kg    300.00
```

### 2. VETERINARY COSTS
```
Row 24: VETERINARY
Row 25:         Vaccines                   10    doses  50.00
Row 26:         Deworming                  10    doses  30.00
Row 27:         Dipping (tick control)     24    dips   120.00
Row 28:         Disease treatment          1     lump   200.00
Row 29:         Veterinary consultation    2     visits 100.00
```

### 3. HOUSING & INFRASTRUCTURE
```
Row 31: HOUSING
Row 32:         Kraal/pen maintenance      1     lump   150.00
Row 33:         Fencing repairs            1     lump   200.00
Row 34:         Roofing/shelter           1     lump   100.00
Row 35:         Feeders & waterers        1     lump   80.00
```

### 4. WATER
```
Row 37: WATER
Row 38:         Borehole pumping          365    days   180.00
Row 39:         Water delivery            12     loads  120.00
Row 40:         Trough maintenance        1      lump   50.00
```

### 5. BREEDING
```
Row 42: BREEDING
Row 43:         Bull/Ram/Buck service     10     services 200.00
Row 44:         Artificial insemination   5      AI     150.00
Row 45:         Pregnancy testing         10     tests  50.00
Row 46:         Breeding stock replacement 1     head   500.00
```

### 6. LABOUR
```
Row 48: LABOUR
Row 49:         Herding/supervision       12     months 600.00
Row 50:         Milking (dairy only)      12     months 400.00
Row 51:         Feeding & cleaning        12     months 300.00
Row 52:         General labor             1      lump   200.00
```

### 7. TRANSPORT IN
```
Row 54: TRANSPORT IN
Row 55:         Feed delivery             12     trips  120.00
Row 56:         Medicine delivery         4      trips  40.00
Row 57:         Stock purchase transport  1      trip   80.00
```

### 8. TRANSPORT OUT
```
Row 59: TRANSPORT OUT
Row 60:         To dip tank              24     trips  120.00
Row 61:         To market/abattoir       2      trips  200.00
Row 62:         Livestock movement       2      trips  100.00
```

### 9. SUNDRY
```
Row 64: SUNDRY
Row 65:         Ear tags & identification 10     units  20.00
Row 66:         Record keeping           1      lump   30.00
Row 67:         Insurance                1      lump   150.00
Row 68:         Mortality buffer         1      lump   250.00
Row 69:         Miscellaneous            1      lump   100.00
```

---

## Key Differences from Crop Budgets

### Metrics Unique to Livestock:
- **Herd/Flock Size** (not hectares)
- **Mortality Rate** (5-15% depending on species)
- **Net Yield** = Gross Yield × (1 - Mortality Rate)
- **Production Cycle** (days: 365 for beef, 90 for broilers)
- **Cycles per Year** (1 for beef, 4+ for broilers)

### Cost Categories Unique to Livestock:
- **Veterinary** (vaccines, dips, treatment)
- **Breeding** (AI, bulls, pregnancy testing)
- **Water** (critical in dry districts)
- **Mortality Buffer** (expected losses)

---

## Example Budget: BEEF CATTLE - COMMUNAL

```
SUMMARY:
Herd Size:              10 head
Gross Weight Yield:     2500 kg (250 kg per head)
Mortality Rate:         5%
Net Yield:              2375 kg
Farm Gate Price:        $4.50/kg
GROSS RETURN:           $10,687.50

COSTS:
Feed (supplement):      $760
Veterinary:            $500
Housing:               $350
Water:                 $350
Breeding:              $900
Labour:                $1,500
Transport In:          $240
Transport Out:         $420
Sundry:                $550
TOTAL VARIABLE COSTS:  $5,570

GROSS PROFIT:          $5,117.50
Per Head:              $511.75
```

---

## Example Budget: BROILERS - 100 BIRDS

```
SUMMARY:
Flock Size:            100 birds
Gross Weight Yield:    180 kg (1.8 kg per bird)
Mortality Rate:        8%
Net Yield:             165.6 kg
Farm Gate Price:       $4.00/kg
GROSS RETURN:          $662.40

COSTS:
Feed (concentrates):   $320
Veterinary:           $25
Housing:              $30
Water:                $10
Chicks:               $50
Labour:               $40
Transport:            $20
Sundry:               $25
TOTAL VARIABLE COSTS: $520

GROSS PROFIT:         $142.40
Per Bird:             $1.42
Production Cycle:     42 days
Cycles per Year:      8
Annual Profit:        $1,139.20
```

---

## How to Create the Excel File

### Option 1: Manual Creation
1. Open Excel/Google Sheets
2. Create 16 sheets (one per livestock type)
3. Copy the structure above
4. Fill in Zimbabwe-specific values

### Option 2: Template Download
(We'll create a downloadable template if needed)

---

## Extraction Script Will Read:

**From Row 5-15 (Summary):**
- `herd_size`: E5
- `gross_yield_kg`: E6
- `mortality_rate`: E7
- `net_yield_kg`: E8
- `farm_gate_price`: E9
- `gross_return`: E10
- `variable_costs`: E11
- `gross_profit`: E12
- `profit_per_head`: E13
- `cycle_days`: E14
- `cycles_per_year`: E15

**From Row 17+ (Costs):**
- Category detection: Col B contains uppercase text (FEED COSTS, VETERINARY, etc.)
- Items: Col B (description), C (quantity), D (unit), E (total cost)

---

## Next Steps

1. **Create the Excel file** with these 16 sheets
2. **Fill with Zimbabwe data** (research livestock costs)
3. **Save as:** `Livestock Budgets.xlsx`
4. **Place in:** `/Users/providencemtendereki/Desktop/`
5. **Run extraction script** to generate JSON

---

**Ready to populate the Excel?** 📊🐄

Or shall I create sample JSON data first for testing?
