/**
 * LIVESTOCK INTELLIGENCE ENGINE
 * 
 * Adjusts livestock budgets based on district-specific factors:
 * - Carrying capacity (grazing pressure)
 * - Water availability
 * - Disease prevalence
 * - Market/abattoir access
 * - Veterinary services
 * - Veld type & quality
 */

const LivestockIntelligence = {
    
    /**
     * Adjust livestock budget for a specific district
     */
    adjustBudgetForDistrict: function(livestockBudget, districtProfile) {
        if (!livestockBudget || !districtProfile) {
            return livestockBudget;
        }
        
        const adjustments = this.calculateDistrictAdjustments(districtProfile);
        const adjustedBudget = JSON.parse(JSON.stringify(livestockBudget)); // Deep copy
        
        // Apply weight gain adjustment (affects yield)
        adjustedBudget.summary.gross_yield_kg *= adjustments.weightGainFactor;
        adjustedBudget.summary.net_yield_kg *= adjustments.weightGainFactor;
        
        // Apply mortality adjustment
        const baseMortality = adjustedBudget.summary.mortality_rate;
        adjustedBudget.summary.mortality_rate = baseMortality * adjustments.mortalityFactor;
        adjustedBudget.summary.net_yield_kg = adjustedBudget.summary.gross_yield_kg * 
                                              (1 - adjustedBudget.summary.mortality_rate / 100);
        
        // Apply price adjustment
        adjustedBudget.summary.farm_gate_price *= adjustments.priceFactor;
        
        // Apply feed cost adjustment
        adjustedBudget.summary.variable_costs *= adjustments.feedCostFactor;
        
        // Recalculate totals
        adjustedBudget.summary.gross_return = adjustedBudget.summary.net_yield_kg * 
                                             adjustedBudget.summary.farm_gate_price;
        adjustedBudget.summary.gross_profit = adjustedBudget.summary.gross_return - 
                                             adjustedBudget.summary.variable_costs;
        adjustedBudget.summary.profit_per_head = adjustedBudget.summary.gross_profit / 
                                                adjustedBudget.summary.herd_size;
        
        // Store adjustment details
        adjustedBudget.adjustments = adjustments;
        adjustedBudget.confidence = adjustments.confidence;
        
        return adjustedBudget;
    },
    
    /**
     * Calculate all district-specific adjustment factors
     */
    calculateDistrictAdjustments: function(district) {
        const factors = {
            carryingCapacity: this.assessCarryingCapacity(district),
            waterAvailability: this.assessWaterAvailability(district),
            diseaseRisk: this.assessDiseaseRisk(district),
            marketAccess: this.assessMarketAccess(district),
            vetServices: this.assessVetServices(district),
            veldQuality: this.assessVeldQuality(district),
            climateStress: this.assessClimateStress(district)
        };
        
        // Calculate composite adjustments
        const weightGainFactor = 
            factors.carryingCapacity.weight_gain_impact *
            factors.waterAvailability.weight_gain_impact *
            factors.veldQuality.weight_gain_impact *
            factors.climateStress.weight_gain_impact;
        
        const mortalityFactor = 
            factors.diseaseRisk.mortality_impact *
            factors.waterAvailability.mortality_impact *
            factors.climateStress.mortality_impact *
            factors.vetServices.mortality_impact;
        
        const priceFactor =
            factors.marketAccess.price_impact;
        
        const feedCostFactor =
            factors.carryingCapacity.feed_cost_impact *
            factors.veldQuality.feed_cost_impact;
        
        // Build explanation array
        const explanation = [];
        
        // Carrying capacity
        if (factors.carryingCapacity.impact !== 'none') {
            explanation.push(factors.carryingCapacity.explanation);
        }
        
        // Water
        if (factors.waterAvailability.impact !== 'none') {
            explanation.push(factors.waterAvailability.explanation);
        }
        
        // Disease
        if (factors.diseaseRisk.impact !== 'none') {
            explanation.push(factors.diseaseRisk.explanation);
        }
        
        // Market
        if (factors.marketAccess.impact !== 'none') {
            explanation.push(factors.marketAccess.explanation);
        }
        
        // Vet services
        if (factors.vetServices.impact !== 'none') {
            explanation.push(factors.vetServices.explanation);
        }
        
        // Veld quality
        if (factors.veldQuality.impact !== 'none') {
            explanation.push(factors.veldQuality.explanation);
        }
        
        // Climate stress
        if (factors.climateStress.impact !== 'none') {
            explanation.push(factors.climateStress.explanation);
        }
        
        // Calculate confidence (0-1)
        const confidence = this.calculateConfidence(district, factors);
        
        return {
            weightGainFactor,
            mortalityFactor,
            priceFactor,
            feedCostFactor,
            explanation,
            confidence,
            factors
        };
    },
    
    /**
     * Assess grazing carrying capacity
     */
    assessCarryingCapacity: function(district) {
        const geoInfo = district.geographic_info || {};
        const naturalRegion = geoInfo.natural_region || '';
        
        // Region I & II: Good carrying capacity
        if (naturalRegion.includes('I') && !naturalRegion.includes('III') && !naturalRegion.includes('IV')) {
            return {
                impact: 'positive',
                weight_gain_impact: 1.1,
                feed_cost_impact: 0.9,
                explanation: `Natural Region ${naturalRegion}: Excellent grazing (+10% weight gain, -10% feed costs)`
            };
        }
        
        // Region III: Moderate
        if (naturalRegion.includes('III')) {
            return {
                impact: 'none',
                weight_gain_impact: 1.0,
                feed_cost_impact: 1.0,
                explanation: null
            };
        }
        
        // Region IV: Poor grazing, need supplements
        if (naturalRegion.includes('IV')) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.85,
                feed_cost_impact: 1.25,
                explanation: `Natural Region ${naturalRegion}: Limited grazing (-15% weight gain, +25% feed costs)`
            };
        }
        
        // Region V: Very poor
        if (naturalRegion.includes('V')) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.7,
                feed_cost_impact: 1.5,
                explanation: `Natural Region ${naturalRegion}: Poor grazing (-30% weight gain, +50% feed costs)`
            };
        }
        
        return {
            impact: 'none',
            weight_gain_impact: 1.0,
            feed_cost_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess water availability
     */
    assessWaterAvailability: function(district) {
        const geoInfo = district.geographic_info || {};
        const rainfall = geoInfo.rainfall_mm || '';
        
        let rainfallNum = 0;
        if (rainfall.includes('-')) {
            const parts = rainfall.split('-').map(s => s.trim().replace('mm', ''));
            rainfallNum = (parseInt(parts[0]) + parseInt(parts[1])) / 2;
        }
        
        // Low rainfall = water stress
        if (rainfallNum < 500) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.8,
                mortality_impact: 1.2,
                explanation: `Low rainfall (${rainfall}): Water stress affects weight gain (-20%) and mortality (+20%)`
            };
        }
        
        // Very low rainfall = severe stress
        if (rainfallNum < 400) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.7,
                mortality_impact: 1.4,
                explanation: `Very low rainfall (${rainfall}): Severe water stress (-30% weight gain, +40% mortality)`
            };
        }
        
        // Adequate rainfall
        if (rainfallNum >= 800) {
            return {
                impact: 'positive',
                weight_gain_impact: 1.05,
                mortality_impact: 0.95,
                explanation: `Good rainfall (${rainfall}): Adequate water (+5% weight gain, -5% mortality)`
            };
        }
        
        return {
            impact: 'none',
            weight_gain_impact: 1.0,
            mortality_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess disease risk based on district challenges
     */
    assessDiseaseRisk: function(district) {
        const quickFacts = district.quick_facts || {};
        const challenges = (quickFacts.main_challenges || []).join(' ').toLowerCase();
        
        // Check for disease-related challenges
        const hasDiseaseIssues = 
            challenges.includes('disease') ||
            challenges.includes('tick') ||
            challenges.includes('fmd') ||
            challenges.includes('livestock disease');
        
        if (hasDiseaseIssues) {
            return {
                impact: 'negative',
                mortality_impact: 1.3,
                explanation: 'District has livestock disease challenges (+30% mortality risk)'
            };
        }
        
        return {
            impact: 'none',
            mortality_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess market and abattoir access
     */
    assessMarketAccess: function(district) {
        const markets = district.markets || {};
        const localMarkets = markets.local_markets || {};
        const totalMarkets = 
            (localMarkets.growth_points || []).length +
            (localMarkets.service_centres || []).length +
            (localMarkets.weekly_markets || []).length;
        
        // Good market access
        if (totalMarkets >= 5) {
            return {
                impact: 'positive',
                price_impact: 1.08,
                explanation: 'Good market access: 5+ local markets (+8% price premium)'
            };
        }
        
        // Limited market access
        if (totalMarkets <= 2) {
            return {
                impact: 'negative',
                price_impact: 0.92,
                explanation: 'Limited market access: Few local markets (-8% price penalty)'
            };
        }
        
        return {
            impact: 'none',
            price_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess veterinary services availability
     */
    assessVetServices: function(district) {
        const quickFacts = district.quick_facts || {};
        const challenges = (quickFacts.main_challenges || []).join(' ').toLowerCase();
        
        // Check for vet service issues
        const hasVetIssues = 
            challenges.includes('vet') ||
            challenges.includes('dip tank') ||
            challenges.includes('animal health');
        
        if (hasVetIssues) {
            return {
                impact: 'negative',
                mortality_impact: 1.15,
                explanation: 'Limited veterinary services (+15% mortality risk)'
            };
        }
        
        return {
            impact: 'none',
            mortality_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess veld quality (sweet vs sour veld)
     */
    assessVeldQuality: function(district) {
        const geoInfo = district.geographic_info || {};
        const soilType = (geoInfo.soil_type || '').toLowerCase();
        
        // Clay/loam soils usually = better veld
        if (soilType.includes('clay') || soilType.includes('loam')) {
            return {
                impact: 'positive',
                weight_gain_impact: 1.08,
                feed_cost_impact: 0.95,
                explanation: `${geoInfo.soil_type || 'Good'} soils: Better veld quality (+8% weight gain, -5% feed costs)`
            };
        }
        
        // Sandy soils = poorer veld
        if (soilType.includes('sandy')) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.93,
                feed_cost_impact: 1.1,
                explanation: `${geoInfo.soil_type || 'Sandy'} soils: Poorer veld quality (-7% weight gain, +10% feed costs)`
            };
        }
        
        return {
            impact: 'none',
            weight_gain_impact: 1.0,
            feed_cost_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Assess climate stress (drought/flood)
     */
    assessClimateStress: function(district) {
        const quickFacts = district.quick_facts || {};
        const challenges = (quickFacts.main_challenges || []).join(' ').toLowerCase();
        
        // Check for drought
        if (challenges.includes('drought')) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.85,
                mortality_impact: 1.2,
                explanation: 'Drought-prone district: Feed/water stress (-15% weight gain, +20% mortality)'
            };
        }
        
        // Check for floods (affects grazing)
        if (challenges.includes('flood')) {
            return {
                impact: 'negative',
                weight_gain_impact: 0.9,
                mortality_impact: 1.1,
                explanation: 'Flood-prone district: Grazing disruption (-10% weight gain, +10% mortality)'
            };
        }
        
        return {
            impact: 'none',
            weight_gain_impact: 1.0,
            mortality_impact: 1.0,
            explanation: null
        };
    },
    
    /**
     * Calculate confidence score
     */
    calculateConfidence: function(district, factors) {
        let confidence = 0.7; // Base confidence
        
        // Increase confidence if we have key district data
        if (district.geographic_info?.natural_region) confidence += 0.1;
        if (district.geographic_info?.rainfall_mm) confidence += 0.1;
        if (district.quick_facts?.main_challenges) confidence += 0.05;
        if (district.markets?.local_markets) confidence += 0.05;
        
        return Math.min(confidence, 0.95);
    }
};

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LivestockIntelligence;
}
