/**
 * DISTRICT INTELLIGENCE ENGINE
 * 
 * Adjusts crop budgets based on district-specific factors:
 * - Weather patterns (rainfall, temperature)
 * - Soil productivity
 * - Input price variations
 * - Market access and selling prices
 * - Logistics and transport costs
 */

const DistrictIntelligence = {
    
    /**
     * Core adjustment algorithm
     * Returns adjusted budget based on district characteristics
     */
    adjustBudgetForDistrict: function(baseBudget, districtProfile) {
        if (!districtProfile) return baseBudget;
        
        const adjustments = this.calculateAdjustments(districtProfile);
        
        return {
            ...baseBudget,
            summary: this.adjustSummary(baseBudget.summary, adjustments),
            costs: this.adjustCosts(baseBudget.costs, adjustments),
            adjustments: adjustments, // Keep track of what changed
            confidence: adjustments.confidence
        };
    },
    
    /**
     * Calculate all adjustment factors based on district data
     */
    calculateAdjustments: function(district) {
        const factors = {
            // Weather-based adjustments
            rainfall: this.getRainfallFactor(district.geographic_info?.rainfall_mm),
            temperature: this.getTemperatureFactor(district.geographic_info?.natural_region),
            
            // Soil productivity
            soilProductivity: this.getSoilProductivityFactor(district.geographic_info?.soil_type),
            
            // Economic factors
            inputPrices: this.getInputPriceFactor(district.geographic_info?.province),
            marketAccess: this.getMarketAccessFactor(district),
            logisticsCosts: this.getLogisticsCostFactor(district),
            
            // Regional challenges
            challenges: this.getChallengeFactor(district.quick_facts?.main_challenges || [])
        };
        
        // Calculate composite adjustments
        const yieldAdjustment = this.calculateYieldAdjustment(factors);
        const costAdjustment = this.calculateCostAdjustment(factors);
        const priceAdjustment = this.calculatePriceAdjustment(factors);
        
        return {
            yieldAdjustment,
            costAdjustment,
            priceAdjustment,
            factors,
            confidence: this.calculateConfidence(factors),
            explanation: this.generateExplanation(factors, district)
        };
    },
    
    /**
     * WEATHER INTELLIGENCE
     */
    getRainfallFactor: function(rainfallMm) {
        if (!rainfallMm) return 1.0;
        
        const rainfall = parseInt(rainfallMm);
        
        // Optimal rainfall: 800-1200mm
        if (rainfall >= 800 && rainfall <= 1200) return 1.0;
        
        // Too low: reduce yield
        if (rainfall < 400) return 0.5; // 50% yield penalty
        if (rainfall < 600) return 0.7;
        if (rainfall < 800) return 0.85;
        
        // Too high: moderate reduction
        if (rainfall > 1200) return 0.95;
        if (rainfall > 1500) return 0.9;
        
        return 1.0;
    },
    
    getTemperatureFactor: function(naturalRegion) {
        if (!naturalRegion) return 1.0;
        
        const region = naturalRegion.toLowerCase();
        
        // Natural Region classification (Zimbabwe)
        const regionFactors = {
            'i': 1.1,    // Region I: Excellent (high rainfall)
            'ii': 1.05,  // Region II: Very good
            'iia': 1.05, // Region IIa
            'iib': 1.0,  // Region IIb
            'iii': 0.9,  // Region III: Moderate
            'iv': 0.75,  // Region IV: Low rainfall
            'v': 0.6     // Region V: Very low rainfall
        };
        
        // Extract region number
        for (const [key, factor] of Object.entries(regionFactors)) {
            if (region.includes(key)) {
                return factor;
            }
        }
        
        return 1.0;
    },
    
    /**
     * SOIL INTELLIGENCE
     */
    getSoilProductivityFactor: function(soilType) {
        if (!soilType) return 1.0;
        
        const soil = soilType.toLowerCase();
        
        // Soil type productivity factors
        if (soil.includes('red clay') || soil.includes('loam')) return 1.1;
        if (soil.includes('sandy loam')) return 1.05;
        if (soil.includes('clay')) return 1.0;
        if (soil.includes('sandy')) return 0.9;
        if (soil.includes('granite')) return 0.85;
        
        return 1.0;
    },
    
    /**
     * ECONOMIC INTELLIGENCE
     */
    getInputPriceFactor: function(province) {
        if (!province) return 1.0;
        
        // Input prices vary by province (distance from suppliers)
        const priceFactors = {
            'harare': 1.0,        // Base (capital, lowest prices)
            'bulawayo': 1.02,     // Second city
            'mashonaland': 1.05,  // Near capital
            'manicaland': 1.08,   // Eastern highlands
            'matabeleland': 1.1,  // Far from capital
            'midlands': 1.06,     // Central
            'masvingo': 1.07      // Southern
        };
        
        const prov = province.toLowerCase();
        
        for (const [key, factor] of Object.entries(priceFactors)) {
            if (prov.includes(key)) {
                return factor;
            }
        }
        
        return 1.05; // Default: 5% higher than Harare
    },
    
    getMarketAccessFactor: function(district) {
        // Better market access = better prices
        const markets = district.markets?.local_markets || {};
        const growthPoints = (markets.growth_points || []).length;
        const serviceCentres = (markets.service_centres || []).length;
        const weeklyMarkets = (markets.weekly_markets || []).length;
        
        const totalMarkets = growthPoints + serviceCentres + weeklyMarkets;
        
        // More markets = better prices (up to 10% premium)
        if (totalMarkets >= 5) return 1.1;
        if (totalMarkets >= 3) return 1.05;
        if (totalMarkets >= 1) return 1.02;
        
        return 0.95; // Remote areas: 5% price discount
    },
    
    getLogisticsCostFactor: function(district) {
        // Logistics costs based on remoteness
        const sellingLocations = district.selling_locations || {};
        const nationalMarkets = (sellingLocations.national || []).length;
        const regionalMarkets = (sellingLocations.regional || []).length;
        
        // Good access to national markets = lower transport costs
        if (nationalMarkets >= 3) return 0.95; // 5% lower costs
        if (regionalMarkets >= 2) return 1.0;
        
        return 1.1; // Remote: 10% higher transport costs
    },
    
    /**
     * CHALLENGE INTELLIGENCE
     */
    getChallengeFactor: function(challenges) {
        if (!challenges || challenges.length === 0) return 1.0;
        
        let penalty = 0;
        
        challenges.forEach(challenge => {
            const c = challenge.toLowerCase();
            
            if (c.includes('drought')) penalty += 0.15;
            if (c.includes('flood')) penalty += 0.1;
            if (c.includes('pest')) penalty += 0.08;
            if (c.includes('disease')) penalty += 0.08;
            if (c.includes('market')) penalty += 0.05;
            if (c.includes('input')) penalty += 0.07;
            if (c.includes('water')) penalty += 0.12;
        });
        
        return Math.max(0.6, 1.0 - penalty); // Maximum 40% penalty
    },
    
    /**
     * COMPOSITE CALCULATIONS
     */
    calculateYieldAdjustment: function(factors) {
        // Yield = rainfall × temperature × soil × challenges
        return factors.rainfall * 
               factors.temperature * 
               factors.soilProductivity * 
               factors.challenges;
    },
    
    calculateCostAdjustment: function(factors) {
        // Costs = inputPrices × logisticsCosts
        return factors.inputPrices * factors.logisticsCosts;
    },
    
    calculatePriceAdjustment: function(factors) {
        // Selling price = marketAccess
        return factors.marketAccess;
    },
    
    /**
     * APPLY ADJUSTMENTS
     */
    adjustSummary: function(summary, adjustments) {
        return {
            ...summary,
            gross_yield_kg_per_ha: summary.gross_yield_kg_per_ha * adjustments.yieldAdjustment,
            net_yield_kg_per_ha: summary.net_yield_kg_per_ha * adjustments.yieldAdjustment,
            variable_costs_per_ha: summary.variable_costs_per_ha * adjustments.costAdjustment,
            variable_costs_per_kg: summary.variable_costs_per_kg * adjustments.costAdjustment / adjustments.yieldAdjustment,
            farm_gate_price: summary.farm_gate_price * adjustments.priceAdjustment,
            gross_return: (summary.net_yield_kg_per_ha * adjustments.yieldAdjustment) * 
                         (summary.farm_gate_price * adjustments.priceAdjustment),
            gross_profit: ((summary.net_yield_kg_per_ha * adjustments.yieldAdjustment) * 
                          (summary.farm_gate_price * adjustments.priceAdjustment)) - 
                          (summary.variable_costs_per_ha * adjustments.costAdjustment)
        };
    },
    
    adjustCosts: function(costs, adjustments) {
        const adjusted = {};
        
        for (const [category, items] of Object.entries(costs)) {
            adjusted[category] = items.map(item => ({
                ...item,
                total_cost: item.total_cost * adjustments.costAdjustment
            }));
        }
        
        return adjusted;
    },
    
    /**
     * CONFIDENCE & EXPLANATION
     */
    calculateConfidence: function(factors) {
        // Confidence based on how many factors we have data for
        let dataPoints = 0;
        let totalPoints = 0;
        
        for (const [key, value] of Object.entries(factors)) {
            totalPoints++;
            if (value !== 1.0) dataPoints++; // We have actual data
        }
        
        return dataPoints / totalPoints;
    },
    
    generateExplanation: function(factors, district) {
        const explanations = [];
        
        if (factors.rainfall !== 1.0) {
            const change = ((factors.rainfall - 1) * 100).toFixed(0);
            explanations.push(`Rainfall (${district.geographic_info?.rainfall_mm}): ${change > 0 ? '+' : ''}${change}% yield`);
        }
        
        if (factors.temperature !== 1.0) {
            const change = ((factors.temperature - 1) * 100).toFixed(0);
            explanations.push(`Natural Region (${district.geographic_info?.natural_region}): ${change > 0 ? '+' : ''}${change}% yield`);
        }
        
        if (factors.soilProductivity !== 1.0) {
            const change = ((factors.soilProductivity - 1) * 100).toFixed(0);
            explanations.push(`Soil (${district.geographic_info?.soil_type}): ${change > 0 ? '+' : ''}${change}% yield`);
        }
        
        if (factors.inputPrices !== 1.0) {
            const change = ((factors.inputPrices - 1) * 100).toFixed(0);
            explanations.push(`Input prices (${district.geographic_info?.province}): ${change > 0 ? '+' : ''}${change}% costs`);
        }
        
        if (factors.marketAccess !== 1.0) {
            const change = ((factors.marketAccess - 1) * 100).toFixed(0);
            explanations.push(`Market access: ${change > 0 ? '+' : ''}${change}% selling price`);
        }
        
        if (factors.challenges !== 1.0) {
            const change = ((factors.challenges - 1) * 100).toFixed(0);
            explanations.push(`Regional challenges: ${change}% yield impact`);
        }
        
        return explanations;
    }
};

// Export for use in tools.html
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DistrictIntelligence;
}
