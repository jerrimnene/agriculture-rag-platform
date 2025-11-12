"""
Gross Margin Calculator
Comprehensive profitability analysis for agricultural enterprises
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CropInput:
    """Represents a crop input cost."""
    name: str
    quantity: float
    unit: str
    cost_per_unit: float
    category: str  # labor, inputs, water, land, etc.
    
    @property
    def total_cost(self) -> float:
        return self.quantity * self.cost_per_unit


@dataclass
class MarginCalculation:
    """Represents a gross margin calculation."""
    crop: str
    district: str
    yield_tonnes_per_ha: float
    price_per_tonne: float
    gross_income: float
    variable_costs: Dict[str, float]
    total_variable_costs: float
    gross_margin: float
    gross_margin_per_tonne: float
    profit_margin_percentage: float
    
    def to_dict(self) -> Dict:
        return {
            "crop": self.crop,
            "district": self.district,
            "yield_tonnes_per_ha": self.yield_tonnes_per_ha,
            "price_per_tonne": self.price_per_tonne,
            "gross_income": round(self.gross_income, 2),
            "variable_costs": {k: round(v, 2) for k, v in self.variable_costs.items()},
            "total_variable_costs": round(self.total_variable_costs, 2),
            "gross_margin": round(self.gross_margin, 2),
            "gross_margin_per_tonne": round(self.gross_margin_per_tonne, 2),
            "profit_margin_percentage": round(self.profit_margin_percentage, 2)
        }


class GrossMarginCalculator:
    """Calculates gross margins for agricultural enterprises."""
    
    # Default cost templates for common crops in Zimbabwe
    COST_TEMPLATES = {
        "maize": {
            "labor": {"quantity": 15, "unit": "person-days", "cost_per_unit": 150},
            "seeds": {"quantity": 25, "unit": "kg", "cost_per_unit": 85},
            "fertilizer_base": {"quantity": 500, "unit": "kg", "cost_per_unit": 3},
            "fertilizer_top": {"quantity": 200, "unit": "kg", "cost_per_unit": 3},
            "herbicide": {"quantity": 2, "unit": "L", "cost_per_unit": 850},
            "insecticide": {"quantity": 1, "unit": "L", "cost_per_unit": 2500},
            "land_preparation": {"quantity": 1, "unit": "operation", "cost_per_unit": 1500},
            "transport": {"quantity": 1, "unit": "operation", "cost_per_unit": 500}
        },
        "sorghum": {
            "labor": {"quantity": 12, "unit": "person-days", "cost_per_unit": 150},
            "seeds": {"quantity": 20, "unit": "kg", "cost_per_unit": 50},
            "fertilizer": {"quantity": 300, "unit": "kg", "cost_per_unit": 3},
            "herbicide": {"quantity": 1.5, "unit": "L", "cost_per_unit": 800},
            "land_preparation": {"quantity": 1, "unit": "operation", "cost_per_unit": 1200},
            "transport": {"quantity": 1, "unit": "operation", "cost_per_unit": 300}
        },
        "groundnuts": {
            "labor": {"quantity": 20, "unit": "person-days", "cost_per_unit": 150},
            "seeds": {"quantity": 50, "unit": "kg", "cost_per_unit": 15},
            "fertilizer": {"quantity": 250, "unit": "kg", "cost_per_unit": 3},
            "fungicide": {"quantity": 2, "unit": "L", "cost_per_unit": 1200},
            "land_preparation": {"quantity": 1, "unit": "operation", "cost_per_unit": 1500},
            "transport": {"quantity": 1, "unit": "operation", "cost_per_unit": 400}
        },
        "vegetables": {
            "labor": {"quantity": 30, "unit": "person-days", "cost_per_unit": 150},
            "seeds": {"quantity": 2, "unit": "kg", "cost_per_unit": 8000},
            "fertilizer": {"quantity": 500, "unit": "kg", "cost_per_unit": 3},
            "fungicide": {"quantity": 4, "unit": "L", "cost_per_unit": 1500},
            "insecticide": {"quantity": 3, "unit": "L", "cost_per_unit": 1800},
            "water": {"quantity": 20, "unit": "irrigation_sessions", "cost_per_unit": 200},
            "land_preparation": {"quantity": 1, "unit": "operation", "cost_per_unit": 2000},
            "transport": {"quantity": 1, "unit": "operation", "cost_per_unit": 800}
        }
    }
    
    # Default yields by district and crop (tonnes/ha)
    YIELD_BY_DISTRICT = {
        "Harare": {"maize": 8.0, "sorghum": 3.0, "groundnuts": 2.5, "vegetables": 20},
        "Binga": {"maize": 1.5, "sorghum": 2.0, "groundnuts": 1.5, "vegetables": 5},
        "Chitungwiza": {"maize": 7.5, "sorghum": 2.8, "groundnuts": 2.3, "vegetables": 18},
        "Bulawayo": {"maize": 5.0, "sorghum": 2.5, "groundnuts": 2.0, "vegetables": 10}
    }
    
    # Market prices by crop (ZWL per tonne) - sample data
    MARKET_PRICES = {
        "maize": 200000,
        "sorghum": 180000,
        "groundnuts": 320000,
        "vegetables": 500000,
        "beans": 280000,
        "tobacco": 800000
    }
    
    def __init__(self):
        """Initialize the calculator."""
        pass
    
    def calculate_margin(
        self,
        crop: str,
        district: str,
        yield_tonnes_per_ha: Optional[float] = None,
        price_per_tonne: Optional[float] = None,
        custom_costs: Optional[Dict[str, float]] = None
    ) -> MarginCalculation:
        """
        Calculate gross margin for a crop in a district.
        
        Args:
            crop: Crop name
            district: District name
            yield_tonnes_per_ha: Override default yield
            price_per_tonne: Override default price
            custom_costs: Override specific costs
        """
        
        # Get yield
        if yield_tonnes_per_ha is None:
            yield_tonnes_per_ha = self.YIELD_BY_DISTRICT.get(district, {}).get(crop, 0)
            if yield_tonnes_per_ha == 0:
                logger.warning(f"No yield data for {crop} in {district}, using 0")
        
        # Get price
        if price_per_tonne is None:
            price_per_tonne = self.MARKET_PRICES.get(crop, 200000)
        
        # Calculate gross income
        gross_income = yield_tonnes_per_ha * price_per_tonne
        
        # Calculate variable costs
        variable_costs = self._calculate_variable_costs(crop, custom_costs)
        total_variable_costs = sum(variable_costs.values())
        
        # Calculate gross margin
        gross_margin = gross_income - total_variable_costs
        gross_margin_per_tonne = gross_margin / yield_tonnes_per_ha if yield_tonnes_per_ha > 0 else 0
        profit_margin_percentage = (gross_margin / gross_income * 100) if gross_income > 0 else 0
        
        return MarginCalculation(
            crop=crop,
            district=district,
            yield_tonnes_per_ha=yield_tonnes_per_ha,
            price_per_tonne=price_per_tonne,
            gross_income=gross_income,
            variable_costs=variable_costs,
            total_variable_costs=total_variable_costs,
            gross_margin=gross_margin,
            gross_margin_per_tonne=gross_margin_per_tonne,
            profit_margin_percentage=profit_margin_percentage
        )
    
    def _calculate_variable_costs(self, crop: str, custom_costs: Optional[Dict] = None) -> Dict[str, float]:
        """Calculate all variable costs for a crop."""
        template = self.COST_TEMPLATES.get(crop, {})
        costs = {}
        
        for cost_name, cost_info in template.items():
            costs[cost_name] = cost_info["quantity"] * cost_info["cost_per_unit"]
        
        # Apply custom overrides
        if custom_costs:
            costs.update(custom_costs)
        
        return costs
    
    def compare_crops(self, district: str, crops: List[str]) -> List[Dict]:
        """Compare margins across multiple crops for a district."""
        results = []
        
        for crop in crops:
            margin = self.calculate_margin(crop, district)
            results.append(margin.to_dict())
        
        # Sort by gross margin (highest first)
        results.sort(key=lambda x: x["gross_margin"], reverse=True)
        
        return results
    
    def get_breakeven_analysis(self, crop: str, district: str) -> Dict:
        """Calculate breakeven yield and price for a crop."""
        variable_costs = self._calculate_variable_costs(crop)
        total_costs = sum(variable_costs.values())
        
        # Get current price
        price = self.MARKET_PRICES.get(crop, 200000)
        
        # Breakeven yield = Total Variable Costs / Price per tonne
        breakeven_yield = total_costs / price if price > 0 else 0
        
        # Breakeven price = Total Variable Costs / Typical yield
        typical_yield = self.YIELD_BY_DISTRICT.get(district, {}).get(crop, 1)
        breakeven_price = total_costs / typical_yield if typical_yield > 0 else 0
        
        return {
            "crop": crop,
            "district": district,
            "total_variable_costs": round(total_costs, 2),
            "current_market_price": price,
            "breakeven_yield_tonnes_per_ha": round(breakeven_yield, 2),
            "breakeven_price_per_tonne": round(breakeven_price, 2),
            "typical_yield": typical_yield,
            "risk_assessment": self._assess_risk(breakeven_yield, typical_yield)
        }
    
    def _assess_risk(self, breakeven_yield: float, typical_yield: float) -> str:
        """Assess farming risk based on breakeven vs typical yield."""
        if breakeven_yield == 0 or typical_yield == 0:
            return "insufficient_data"
        
        ratio = typical_yield / breakeven_yield
        
        if ratio < 1.5:
            return "high_risk"
        elif ratio < 2.0:
            return "medium_risk"
        else:
            return "low_risk"
    
    def get_cost_breakdown(self, crop: str) -> Dict[str, Any]:
        """Get detailed cost breakdown for a crop."""
        costs = self._calculate_variable_costs(crop)
        total = sum(costs.values())
        
        breakdown = {}
        for cost_name, cost_value in costs.items():
            breakdown[cost_name] = {
                "amount": round(cost_value, 2),
                "percentage": round((cost_value / total * 100), 1) if total > 0 else 0
            }
        
        return {
            "crop": crop,
            "total_variable_costs": round(total, 2),
            "breakdown": breakdown
        }
    
    def scenario_analysis(
        self,
        crop: str,
        district: str,
        scenarios: List[Dict]
    ) -> List[Dict]:
        """
        Analyze different scenarios (e.g., different yields or prices).
        
        Args:
            crop: Crop name
            district: District name
            scenarios: List of dicts with 'name', 'yield', 'price' keys
        """
        results = []
        
        for scenario in scenarios:
            margin = self.calculate_margin(
                crop=crop,
                district=district,
                yield_tonnes_per_ha=scenario.get("yield"),
                price_per_tonne=scenario.get("price")
            )
            
            result = margin.to_dict()
            result["scenario"] = scenario.get("name", "Custom")
            results.append(result)
        
        return results
