"""
Market prices API for AgriEvidence.
Provides commodity pricing data for agricultural decision-making.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MarketPricesAPI:
    """Interface for agricultural commodity market prices."""
    
    def __init__(self, prices_file: Optional[str] = None):
        """Initialize the market prices API."""
        if prices_file is None:
            prices_file = Path(__file__).parent / "market_prices.json"
        
        with open(prices_file, 'r') as f:
            self.data = json.load(f)
    
    def get_all_markets(self) -> Dict:
        """Get list of all available markets."""
        markets_list = []
        for market_name, market_data in self.data['markets'].items():
            markets_list.append({
                'name': market_name,
                'district': market_data['district'],
                'province': market_data['province'],
                'type': market_data['type'],
                'commodities_count': len(market_data['commodities'])
            })
        
        return {
            'last_updated': self.data['last_updated'],
            'currency': self.data['currency'],
            'markets': markets_list
        }
    
    def get_market_prices(self, market_name: str) -> Optional[Dict]:
        """Get prices for a specific market."""
        market_data = self.data['markets'].get(market_name)
        
        if not market_data:
            return None
        
        return {
            'market': market_name,
            'district': market_data['district'],
            'province': market_data['province'],
            'type': market_data['type'],
            'last_updated': self.data['last_updated'],
            'currency': self.data['currency'],
            'commodities': market_data['commodities']
        }
    
    def get_district_prices(self, district_name: str) -> Optional[Dict]:
        """Get market prices for a district."""
        # Find market by district
        for market_name, market_data in self.data['markets'].items():
            if market_data['district'].lower() == district_name.lower():
                return self.get_market_prices(market_name)
        
        # If no exact match, find nearest market
        return self._find_nearest_market(district_name)
    
    def get_commodity_comparison(self, commodity: str) -> Dict:
        """Compare prices for a commodity across all markets."""
        prices = []
        
        for market_name, market_data in self.data['markets'].items():
            if commodity in market_data['commodities']:
                comm_data = market_data['commodities'][commodity]
                prices.append({
                    'market': market_name,
                    'district': market_data['district'],
                    'price_per_kg': comm_data['price_per_kg'],
                    'availability': comm_data['availability']
                })
        
        if not prices:
            return {'commodity': commodity, 'message': 'No price data available', 'prices': []}
        
        # Sort by price
        prices.sort(key=lambda x: x['price_per_kg'])
        
        # Calculate averages
        avg_price = sum(p['price_per_kg'] for p in prices) / len(prices)
        lowest = prices[0]
        highest = prices[-1]
        
        # Get trend if available
        trend = self.data['price_trends'].get(commodity, {})
        
        return {
            'commodity': commodity,
            'currency': self.data['currency'],
            'average_price': round(avg_price, 2),
            'lowest_price': {
                'market': lowest['market'],
                'district': lowest['district'],
                'price': lowest['price_per_kg']
            },
            'highest_price': {
                'market': highest['market'],
                'district': highest['district'],
                'price': highest['price_per_kg']
            },
            'trend': trend,
            'all_markets': prices
        }
    
    def get_price_trends(self) -> Dict:
        """Get price trends for all commodities."""
        return {
            'last_updated': self.data['last_updated'],
            'trends': self.data['price_trends']
        }
    
    def get_nearest_market(self, district_name: str) -> Optional[str]:
        """Find the nearest market for a district."""
        # For now, return simple mapping
        # In production, this would use geo coordinates
        district_lower = district_name.lower()
        
        # Province-based routing
        province_markets = {
            'harare': 'Mbare Musika',
            'bulawayo': 'Bulawayo',
            'manicaland': 'Mutare',
            'midlands': 'Gweru',
            'masvingo': 'Masvingo',
            'mashonaland west': 'Chinhoyi',
            'mashonaland central': 'Bindura',
            'mashonaland east': 'Mbare Musika',
            'matabeleland north': 'Bulawayo',
            'matabeleland south': 'Bulawayo'
        }
        
        # Try to find by province (would need geo context integration)
        for province, market in province_markets.items():
            if province in district_lower:
                return market
        
        return 'Mbare Musika'  # Default to largest market
    
    def _find_nearest_market(self, district_name: str) -> Optional[Dict]:
        """Find and return prices from nearest market."""
        nearest_market = self.get_nearest_market(district_name)
        
        if nearest_market:
            result = self.get_market_prices(nearest_market)
            if result:
                result['note'] = f'Prices from nearest market: {nearest_market}'
            return result
        
        return None
    
    def format_market_summary(self, district_name: str) -> str:
        """Format a human-readable market summary for a district."""
        prices = self.get_district_prices(district_name)
        
        if not prices:
            return f"No market price data available for {district_name}."
        
        lines = [
            f"Market Prices - {prices['market']} ({prices['type']})",
            f"District: {prices['district']}, Province: {prices['province']}",
            f"Last Updated: {prices['last_updated']} | Currency: {prices['currency']}",
            "",
            "Commodities:"
        ]
        
        for commodity, data in prices['commodities'].items():
            commodity_display = commodity.replace('_', ' ').title()
            lines.append(f"  • {commodity_display}: ${data['price_per_kg']:.2f}/{data['unit']} ({data['availability']} availability)")
        
        return '\n'.join(lines)


# Convenience function
def get_market_prices(district: Optional[str] = None, commodity: Optional[str] = None) -> Dict:
    """
    Get market prices for a district or commodity.
    
    Args:
        district: District name (optional)
        commodity: Commodity name (optional)
        
    Returns:
        Market price data
    """
    market_api = MarketPricesAPI()
    
    if commodity:
        return market_api.get_commodity_comparison(commodity)
    elif district:
        return market_api.get_district_prices(district)
    else:
        return market_api.get_all_markets()
