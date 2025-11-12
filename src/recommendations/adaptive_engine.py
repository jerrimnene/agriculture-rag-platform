"""
Adaptive Recommendations Engine
Generates intelligent, context-aware agricultural recommendations based on district conditions
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class AdaptiveRecommendationEngine:
    """Generates adaptive recommendations for difficult farming scenarios."""
    
    # Define difficulty-based strategies
    DIFFICULTY_STRATEGIES = {
        "high": [
            "drought_tolerant_crops",
            "water_harvesting",
            "alternative_sourcing",
            "value_addition",
            "cooperative_marketing"
        ],
        "medium": [
            "improved_varieties",
            "soil_conservation",
            "market_linkage",
            "input_optimization"
        ],
        "low": [
            "standard_practices",
            "market_integration",
            "value_addition"
        ]
    }
    
    # Specific recommendations for difficult districts
    DIFFICULT_DISTRICT_SOLUTIONS = {
        "Binga": {
            "primary_challenge": "Low rainfall (450mm) and drought risk",
            "crop_alternatives": [
                {
                    "crop": "Millet",
                    "reason": "Drought-tolerant, 2-3 tonnes/ha in Binga",
                    "practices": ["Mulching for moisture retention", "Plant spacing 60x30cm"]
                },
                {
                    "crop": "Sorghum",
                    "reason": "Deep-rooting, needs only 400mm rainfall",
                    "practices": ["Early planting (October)", "Resistant to fall armyworm"]
                },
                {
                    "crop": "Groundnuts",
                    "reason": "1.5 tonnes/ha, fixes nitrogen, drought-resistant",
                    "practices": ["Intercrop with sorghum", "Sandy soil suitable"]
                },
                {
                    "crop": "Goat farming",
                    "reason": "Drought-resilient livestock, high market value",
                    "practices": ["Browse available vegetation", "10-15 goats per hectare", "Breed: Boer or Local mix"]
                }
            ],
            "water_management": [
                "Build water harvesting ponds (3-5 ponds per 5 hectares)",
                "Implement zai pits for tree planting",
                "Use contour ridges to reduce runoff",
                "Plant vetiver grass as windbreaks"
            ],
            "market_strategy": [
                "Source milled grains from Hwange (150km)",
                "Buy wholesale at 10% discount, sell at local markets for 15-20% markup",
                "Transport cost: ~150 ZWL/bag, profit margin: 30-50 ZWL/bag",
                "Target: Victoria Falls (200km), Hwange (150km) urban markets",
                "Join grain trader cooperatives for bulk buying discounts"
            ],
            "income_diversification": [
                "Process sorghum into traditional beer (pombe) for local sales",
                "Dry millet for porridge flour - high demand in urban areas",
                "Sell goats as live animals to traders (700,000-1,000,000 ZWL per goat)",
                "Honey production from bees (suitable in dry areas)"
            ]
        }
    }
    
    # Supply chain optimization strategies
    SUPPLY_CHAIN_STRATEGIES = {
        "remote_high_transport": {
            "description": "For areas with high transport costs",
            "tactics": [
                "Form farmer cooperatives to aggregate produce (5-10 farmers)",
                "Share transport costs (50-60 ZWL per farmer vs 150 alone)",
                "Identify trusted trader/middleman for consistent offtake",
                "Process crops to add value before transport (reduce weight/volume)",
                "Direct bulk sales to urban retailers or restaurants"
            ]
        },
        "low_buyer_density": {
            "description": "For areas with few local buyers",
            "tactics": [
                "Develop supply contracts with urban traders",
                "Use phone/WhatsApp to connect with distant buyers",
                "Organize group marketing to attract commercial buyers",
                "Supply to schools, hospitals, government programs",
                "Participate in agricultural markets (Harare, Bulawayo) weekly"
            ]
        },
        "seasonal_price_volatility": {
            "description": "For unstable market prices",
            "tactics": [
                "Diversify crop portfolio to spread income across seasons",
                "Store crops for off-season sales (grains, groundnuts)",
                "Forward contracts with buyers to lock in prices",
                "Value addition (milling, packaging) to stabilize prices",
                "Join commodity exchange platforms if available"
            ]
        }
    }
    
    def generate_holistic_advisory(
        self,
        crop: str,
        district: str,
        difficulty_level: str,
        challenges: List[str],
        market_info: Dict,
        margin_info: Dict
    ) -> Dict[str, Any]:
        """
        Generate comprehensive advisory integrating all factors.
        
        Args:
            crop: Target crop
            district: Target district
            difficulty_level: low/medium/high
            challenges: List of specific challenges
            market_info: Market data for the area
            margin_info: Gross margin analysis
        """
        
        advisory = {
            "district": district,
            "crop": crop,
            "difficulty_level": difficulty_level,
            "holistic_assessment": self._generate_assessment(crop, district, difficulty_level),
            "viability_score": self._calculate_viability_score(crop, district, margin_info),
            "what_to_plant": self._get_planting_advice(crop, district, difficulty_level),
            "why_this_crop": self._get_crop_justification(crop, district),
            "costs_and_profitability": self._format_profitability(margin_info),
            "market_opportunity": self._format_market_info(market_info),
            "key_challenges": challenges,
            "mitigation_strategies": self._get_mitigation_strategies(crop, district, difficulty_level),
            "alternative_strategies": self._get_alternatives(crop, district, difficulty_level),
            "supply_chain_options": self._get_supply_chain_options(district, market_info),
            "nearby_opportunities": self._get_nearby_city_opportunities(district),
            "investment_requirement": self._estimate_investment(crop, margin_info),
            "expected_return": self._estimate_return(margin_info),
            "implementation_timeline": self._get_implementation_timeline(crop, district)
        }
        
        return advisory
    
    def _generate_assessment(self, crop: str, district: str, difficulty: str) -> str:
        """Generate an assessment of farming viability."""
        if difficulty == "high":
            if district == "Binga" and crop == "maize":
                return (
                    "❌ MAIZE IN BINGA IS NOT RECOMMENDED. "
                    "450mm rainfall is below maize's 600mm minimum requirement. "
                    "Expected yield: 1.5 tonnes/ha (vs 8 tonnes in Harare). "
                    "Alternative: Switch to millet, sorghum, or groundnuts. "
                    "Or source maize from Hwange and resell locally with 30% markup."
                )
            return (
                f"⚠️ CHALLENGING CONDITIONS. {crop} is difficult in {district} due to arid conditions. "
                f"Success requires adaptation strategies or alternative approaches."
            )
        elif difficulty == "medium":
            return (
                f"⚠️ MODERATE CHALLENGE. {crop} can succeed with improved practices. "
                f"Focus on soil conservation and water management."
            )
        else:
            return f"✅ FAVORABLE CONDITIONS. {crop} has good potential in {district}."
    
    def _calculate_viability_score(self, crop: str, district: str, margin_info: Dict) -> float:
        """Calculate crop viability score 0-100."""
        margin = margin_info.get("gross_margin", 0)
        income = margin_info.get("gross_income", 1)
        
        if income == 0:
            return 0
        
        # Score based on gross margin percentage
        margin_percent = (margin / income) * 100
        
        if margin_percent > 50:
            return 85  # Excellent
        elif margin_percent > 30:
            return 65  # Good
        elif margin_percent > 10:
            return 40  # Moderate
        else:
            return 20  # Risky
    
    def _get_planting_advice(self, crop: str, district: str, difficulty_level: str) -> Dict:
        """Get specific planting recommendations."""
        return {
            "recommended": crop,
            "planting_season": "November-December",
            "spacing": self._get_spacing(crop),
            "quantities": self._get_quantities(crop),
            "difficulties_specific_notes": self._get_difficulty_specific_notes(crop, district, difficulty_level)
        }
    
    def _get_spacing(self, crop: str) -> str:
        """Get recommended spacing for a crop."""
        spacing = {
            "maize": "75cm x 25cm (3-4 plants per hill)",
            "sorghum": "80cm x 30cm (1-2 plants per hill)",
            "groundnuts": "60cm x 20cm (no thinning needed)",
            "millet": "60cm x 15cm (thin to 1 plant)",
            "vegetables": "30-45cm depending on variety"
        }
        return spacing.get(crop, "Consult local extension for recommended spacing")
    
    def _get_quantities(self, crop: str) -> str:
        """Get seed/input quantities per hectare."""
        quantities = {
            "maize": "25kg seeds, 100kg lime + 200kg 7:14:7 base + 200kg CAN",
            "sorghum": "20kg seeds, 10kg lime + 200kg 7:14:7",
            "groundnuts": "50kg seeds, 10kg lime + 150kg 7:14:7",
            "millet": "15kg seeds, 10kg lime + 150kg 7:14:7"
        }
        return quantities.get(crop, "Consult seed packet for exact quantities")
    
    def _get_difficulty_specific_notes(self, crop: str, district: str, difficulty: str) -> str:
        """Get notes specific to the difficulty level."""
        if difficulty == "high" and district == "Binga":
            return (
                "🔴 In Binga: Low rainfall makes {crop} risky unless irrigated. "
                "Consider: (1) Drought-resistant varieties, (2) Water harvesting, (3) Sourcing from Hwange"
            ).format(crop=crop)
        elif difficulty == "high":
            return "🟡 Use drought-resistant varieties and practice conservation agriculture"
        else:
            return "🟢 Standard practices should work well. Focus on good agronomic practices."
    
    def _get_crop_justification(self, crop: str, district: str) -> str:
        """Justify why this crop is recommended."""
        justifications = {
            "Binga_millet": "Millet needs only 400mm rainfall (Binga has 450mm). Drought-resistant. Yield: 2-3 tonnes/ha.",
            "Binga_sorghum": "Deep-rooted, stores water in stalk. Requires only 400mm. Pest-resistant. Yield: 2 tonnes/ha.",
            "Binga_groundnuts": "Fixes nitrogen, drought-tolerant. Profitable at 320,000 ZWL/tonne. Yield: 1.5 tonnes/ha.",
            "Binga_goats": "Thrive on sparse vegetation. Drought-proof. High market value: 800,000-1,000,000 ZWL/animal.",
            "Harare_maize": "Optimal rainfall (750mm). High yield: 8 tonnes/ha. Strong market. Margin: 1,000,000+ ZWL/ha.",
        }
        
        key = f"{district}_{crop}"
        return justifications.get(key, f"{crop} is suitable for {district} conditions.")
    
    def _format_profitability(self, margin_info: Dict) -> Dict:
        """Format profitability information clearly."""
        return {
            "yield_tonnes_per_ha": margin_info.get("yield_tonnes_per_ha"),
            "market_price_per_tonne": margin_info.get("price_per_tonne"),
            "gross_income": f"{margin_info.get('gross_income', 0):,.0f} ZWL/ha",
            "variable_costs": f"{margin_info.get('total_variable_costs', 0):,.0f} ZWL/ha",
            "gross_margin": f"{margin_info.get('gross_margin', 0):,.0f} ZWL/ha",
            "profit_per_tonne": f"{margin_info.get('gross_margin_per_tonne', 0):,.0f} ZWL/tonne",
            "profit_margin_percentage": f"{margin_info.get('profit_margin_percentage', 0):.1f}%",
            "recommendation": self._get_profitability_recommendation(margin_info)
        }
    
    def _get_profitability_recommendation(self, margin_info: Dict) -> str:
        """Get recommendation based on margin."""
        margin_percent = margin_info.get('profit_margin_percentage', 0)
        
        if margin_percent > 50:
            return "✅ HIGHLY PROFITABLE - Strong investment case"
        elif margin_percent > 30:
            return "🟢 PROFITABLE - Good returns worth pursuing"
        elif margin_percent > 10:
            return "🟡 MARGINAL - Risky, consider alternatives"
        else:
            return "🔴 NOT PROFITABLE - Do NOT invest in this crop in this district"
    
    def _format_market_info(self, market_info: Dict) -> Dict:
        """Format market information clearly."""
        return {
            "local_markets": market_info.get("local_markets", []),
            "trading_centers": market_info.get("trading_centers", []),
            "buyer_density": market_info.get("buyer_density"),
            "transport_cost_per_bag": f"{market_info.get('transport_cost')} ZWL",
            "market_frequency": market_info.get("market_days", ["Unknown"]),
            "nearby_urban_centers": market_info.get("nearby_cities", []),
            "market_outlook": self._get_market_outlook(market_info)
        }
    
    def _get_market_outlook(self, market_info: Dict) -> str:
        """Get outlook on market viability."""
        density = market_info.get("buyer_density", "low")
        transport = market_info.get("transport_cost", 0)
        
        if density == "high" and transport < 50:
            return "✅ Excellent market access - Easy to sell"
        elif density == "high":
            return "🟡 Good buyers but high transport costs - Consider cooperatives"
        elif density == "low":
            return "🔴 Limited buyers - Focus on direct sales or value addition"
        else:
            return "Information needed"
    
    def _get_mitigation_strategies(self, crop: str, district: str, difficulty: str) -> List[str]:
        """Get strategies to mitigate risks."""
        strategies = []
        
        if difficulty == "high":
            strategies.extend([
                "Diversify crops - Don't rely on single crop",
                "Build water harvesting structures (3-5 ponds per hectare)",
                "Use drought-resistant varieties",
                "Practice conservation agriculture (mulching, composting)",
                "Keep small livestock for fallback income"
            ])
        
        if district == "Binga":
            strategies.extend([
                "Join farmer cooperative for bulk inputs at 10-20% discount",
                "Store grains for off-season sales (January-June prices higher)",
                "Establish relationship with trader from Hwange for supply chain support",
                "Use mobile money for payments to reduce risk"
            ])
        
        return strategies
    
    def _get_alternatives(self, crop: str, district: str, difficulty: str) -> List[Dict]:
        """Get alternative crops if primary crop fails."""
        alternatives = []
        
        if district == "Binga":
            alternatives = [
                {
                    "crop": "Millet",
                    "why": "Better drought tolerance than maize",
                    "expected_yield": "2-3 tonnes/ha",
                    "margin": "400,000-600,000 ZWL/ha"
                },
                {
                    "crop": "Goat farming",
                    "why": "Drought-proof income",
                    "expected_yield": "10-15 kids per year per goat",
                    "margin": "500,000-1,000,000 ZWL per animal"
                },
                {
                    "crop": "Honey production",
                    "why": "Low input, uses natural resources",
                    "expected_yield": "30-50kg per hive annually",
                    "margin": "50,000 ZWL per kg"
                }
            ]
        
        return alternatives
    
    def _get_supply_chain_options(self, district: str, market_info: Dict) -> List[Dict]:
        """Get supply chain options specific to district."""
        options = []
        
        if district == "Binga":
            options = [
                {
                    "option": "Direct sourcing from Hwange traders",
                    "description": "Buy grains wholesale, transport (150 ZWL/bag cost), sell locally for 30% markup",
                    "pros": ["Guaranteed supply", "Predictable costs", "Retail price advantage"],
                    "cons": ["Requires capital", "Transport risk", "Bulk commitment"],
                    "estimated_profit": "30-50 ZWL per bag"
                },
                {
                    "option": "Cooperative marketing",
                    "description": "Join 5-10 farmers, bulk sales to traders, reduced transport per farmer",
                    "pros": ["Lower transport costs", "Negotiation power", "Shared risk"],
                    "cons": ["Coordination complexity", "Profit sharing"],
                    "estimated_profit": "20% higher than individual sales"
                },
                {
                    "option": "Contract farming with urban traders",
                    "description": "Pre-arrange supply commitment with Bulawayo/Victoria Falls traders",
                    "pros": ["Guaranteed market", "Price stability", "Extension support"],
                    "cons": ["Lower prices", "Quality requirements", "Binding contract"],
                    "estimated_profit": "Standard + extension services"
                }
            ]
        
        return options
    
    def _get_nearby_city_opportunities(self, district: str) -> Dict:
        """Identify nearby urban centers and opportunities."""
        opportunities = {
            "Binga": {
                "hwange": {
                    "distance": "150km",
                    "drive_time": "3-4 hours",
                    "market_demand": "High - mining town population 15,000+",
                    "products": ["Milled grains", "Dried vegetables", "Groundnuts"],
                    "wholesale_contacts": "Hwange Growth Point traders",
                    "margin_opportunity": "15-30% markup on bulk purchases"
                },
                "victoria_falls": {
                    "distance": "200km",
                    "drive_time": "4-5 hours",
                    "market_demand": "Very high - 500,000+ annual tourists",
                    "products": ["Vegetables", "Fresh produce", "Honey", "Crafts"],
                    "opportunities": ["Hotels", "Restaurants", "Curio shops"],
                    "margin_opportunity": "50-100% markup on specialty items"
                }
            }
        }
        
        return opportunities.get(district, {})
    
    def _estimate_investment(self, crop: str, margin_info: Dict) -> str:
        """Estimate initial investment needed."""
        # Rough estimate based on costs per hectare
        costs = margin_info.get("total_variable_costs", 0)
        
        if costs < 500000:
            return "💰 Low investment (< 500,000 ZWL/ha) - Accessible for smallholder"
        elif costs < 1500000:
            return "💰💰 Medium investment (500,000-1,500,000 ZWL/ha) - Need some capital"
        else:
            return "💰💰💰 High investment (> 1,500,000 ZWL/ha) - Requires significant capital or credit"
    
    def _estimate_return(self, margin_info: Dict) -> str:
        """Estimate return on investment."""
        margin = margin_info.get("gross_margin", 0)
        
        if margin > 1000000:
            return "🎯 EXCELLENT RETURN - Strong income generation"
        elif margin > 500000:
            return "🎯 GOOD RETURN - Solid profit potential"
        elif margin > 0:
            return "🎯 MODEST RETURN - Contributes to household income"
        else:
            return "❌ NEGATIVE RETURN - Do not proceed without major changes"
    
    def _get_implementation_timeline(self, crop: str, district: str) -> Dict:
        """Get implementation timeline for the crop."""
        timelines = {
            "maize": {
                "Nov": "Land prep, planting",
                "Dec": "Weeding (1st round)",
                "Jan": "Weeding (2nd round), nutrients",
                "Feb": "Crop monitoring",
                "Mar": "Harvesting begins",
                "Apr": "Harvest completion, storage"
            },
            "sorghum": {
                "Oct": "Land prep",
                "Nov": "Planting",
                "Dec": "Weeding, thinning",
                "Jan-Feb": "Crop growth",
                "Mar": "Harvesting",
                "Apr": "Threshing, storage"
            },
            "groundnuts": {
                "Nov": "Land prep, planting",
                "Dec": "Emergence, weeding",
                "Jan-Feb": "Growth",
                "Mar": "Flowering, pod filling",
                "Apr-May": "Harvesting"
            }
        }
        
        return timelines.get(crop, {"Note": "Consult local extension agent for specific timeline"})
