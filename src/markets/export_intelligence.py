"""
Export Market Intelligence System
Comprehensive export market data per crop with prices, demand, and trade routes
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExportMarketIntelligence:
    """Manages export market data for Zimbabwe agricultural products."""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            data_file = Path(__file__).parent.parent.parent / "data" / "export_markets.json"
        
        self.data_file = Path(data_file)
        self.markets_data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load export market data."""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize with sample data
            return self._initialize_sample_data()
    
    def save_data(self):
        """Save export market data."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.markets_data, f, indent=2)
    
    def _initialize_sample_data(self) -> Dict:
        """Initialize with sample export market data for Zimbabwe crops."""
        return {
            "tobacco": {
                "crop_name": "Tobacco (Flue-cured)",
                "export_destinations": [
                    {
                        "country": "China",
                        "percentage": 25,
                        "avg_price_usd_per_kg": 4.50,
                        "demand_level": "High",
                        "requirements": ["Phytosanitary certificate", "Quality grade A/B"],
                        "port_of_entry": "Shanghai",
                        "shipping_route": "Durban → Shanghai (35-40 days)"
                    },
                    {
                        "country": "South Africa",
                        "percentage": 20,
                        "avg_price_usd_per_kg": 4.20,
                        "demand_level": "Moderate",
                        "requirements": ["SADC certificate of origin"],
                        "port_of_entry": "Durban",
                        "shipping_route": "Road transport via Beitbridge"
                    },
                    {
                        "country": "Belgium",
                        "percentage": 15,
                        "avg_price_usd_per_kg": 5.00,
                        "demand_level": "Moderate",
                        "requirements": ["EU phytosanitary standards", "Pesticide residue certification"],
                        "port_of_entry": "Antwerp",
                        "shipping_route": "Durban → Antwerp (30-35 days)"
                    }
                ],
                "total_export_value_usd": 850000000,
                "export_volume_tonnes": 180000,
                "peak_season": "March-September",
                "quality_standards": ["TIMB grading", "ISO 3402"],
                "key_buyers": ["China National Tobacco Corporation", "Imperial Brands", "British American Tobacco"],
                "market_trends": "Increasing demand from Asian markets, declining EU demand",
                "export_incentives": "Government rebate of 5% on verified exports"
            },
            "horticulture": {
                "crop_name": "Fresh Vegetables & Flowers",
                "export_destinations": [
                    {
                        "country": "United Kingdom",
                        "percentage": 30,
                        "avg_price_usd_per_kg": 2.50,
                        "demand_level": "High",
                        "requirements": ["GlobalGAP certification", "HACCP compliance"],
                        "port_of_entry": "London Heathrow",
                        "shipping_route": "Air freight via Johannesburg (24-48 hours)"
                    },
                    {
                        "country": "Netherlands",
                        "percentage": 25,
                        "avg_price_usd_per_kg": 2.80,
                        "demand_level": "High",
                        "requirements": ["MPS certification for flowers", "EU 543/2011 standards"],
                        "port_of_entry": "Amsterdam Schiphol",
                        "shipping_route": "Air freight direct or via Johannesburg"
                    },
                    {
                        "country": "South Africa",
                        "percentage": 20,
                        "avg_price_usd_per_kg": 1.80,
                        "demand_level": "Moderate",
                        "requirements": ["SADC certificate", "South African import permit"],
                        "port_of_entry": "Johannesburg",
                        "shipping_route": "Road transport via Beitbridge (48 hours)"
                    }
                ],
                "total_export_value_usd": 120000000,
                "export_volume_tonnes": 45000,
                "peak_season": "April-November",
                "quality_standards": ["GlobalGAP", "MPS", "HACCP"],
                "key_buyers": ["Tesco", "Sainsbury's", "Royal FloraHolland"],
                "market_trends": "Growing organic produce demand, stable flower market",
                "export_incentives": "Air freight subsidy program for perishables"
            },
            "macadamia": {
                "crop_name": "Macadamia Nuts",
                "export_destinations": [
                    {
                        "country": "China",
                        "percentage": 40,
                        "avg_price_usd_per_kg": 12.00,
                        "demand_level": "Very High",
                        "requirements": ["Aflatoxin testing", "Chinese AQSIQ registration"],
                        "port_of_entry": "Shanghai/Shenzhen",
                        "shipping_route": "Durban → Shanghai (30-35 days)"
                    },
                    {
                        "country": "United States",
                        "percentage": 25,
                        "avg_price_usd_per_kg": 13.50,
                        "demand_level": "High",
                        "requirements": ["FDA compliance", "Organic certification (premium)"],
                        "port_of_entry": "Los Angeles",
                        "shipping_route": "Durban → Los Angeles (40-45 days)"
                    },
                    {
                        "country": "South Africa",
                        "percentage": 15,
                        "avg_price_usd_per_kg": 11.00,
                        "demand_level": "Moderate",
                        "requirements": ["Standard SABS certification"],
                        "port_of_entry": "Durban",
                        "shipping_route": "Road/rail transport (2-3 days)"
                    }
                ],
                "total_export_value_usd": 45000000,
                "export_volume_tonnes": 3500,
                "peak_season": "March-June (harvest)",
                "quality_standards": ["Kernel recovery rate >32%", "Moisture <1.5%", "Sound kernel >90%"],
                "key_buyers": ["Nuttex", "MacFarms", "Royal Nut Company"],
                "market_trends": "Explosive growth in Chinese demand, premium pricing for organic",
                "export_incentives": "ZIMTRADE export support services"
            },
            "coffee": {
                "crop_name": "Arabica Coffee",
                "export_destinations": [
                    {
                        "country": "Germany",
                        "percentage": 35,
                        "avg_price_usd_per_kg": 8.50,
                        "demand_level": "High",
                        "requirements": ["Specialty grade 84+", "Rainforest Alliance/Fairtrade"],
                        "port_of_entry": "Hamburg",
                        "shipping_route": "Durban → Hamburg (28-32 days)"
                    },
                    {
                        "country": "United Kingdom",
                        "percentage": 25,
                        "avg_price_usd_per_kg": 9.00,
                        "demand_level": "High",
                        "requirements": ["Specialty Coffee Association standards"],
                        "port_of_entry": "London",
                        "shipping_route": "Durban → London (28-30 days)"
                    },
                    {
                        "country": "United States",
                        "percentage": 20,
                        "avg_price_usd_per_kg": 9.50,
                        "demand_level": "Moderate",
                        "requirements": ["USDA Organic (premium)", "SCA cupping score 84+"],
                        "port_of_entry": "New York/Seattle",
                        "shipping_route": "Durban → US East/West Coast (35-45 days)"
                    }
                ],
                "total_export_value_usd": 2500000,
                "export_volume_tonnes": 280,
                "peak_season": "April-September",
                "quality_standards": ["SCA 84+ cupping score", "Moisture 10-12%", "Screen size 15+"],
                "key_buyers": ["Sustainable Harvest", "Café Imports", "Volcafe"],
                "market_trends": "Growing specialty coffee market, focus on traceability",
                "export_incentives": "Specialty coffee training programs"
            },
            "citrus": {
                "crop_name": "Citrus Fruits (Oranges, Lemons)",
                "export_destinations": [
                    {
                        "country": "European Union",
                        "percentage": 40,
                        "avg_price_usd_per_kg": 0.85,
                        "demand_level": "Moderate",
                        "requirements": ["GlobalGAP", "Cold treatment certification", "EU import license"],
                        "port_of_entry": "Rotterdam/Antwerp",
                        "shipping_route": "Durban → Rotterdam (25-28 days cold chain)"
                    },
                    {
                        "country": "Middle East",
                        "percentage": 30,
                        "avg_price_usd_per_kg": 0.90,
                        "demand_level": "High",
                        "requirements": ["Halal certification", "Phytosanitary certificate"],
                        "port_of_entry": "Dubai/Jebel Ali",
                        "shipping_route": "Durban → Dubai (14-18 days)"
                    },
                    {
                        "country": "Far East",
                        "percentage": 15,
                        "avg_price_usd_per_kg": 1.00,
                        "demand_level": "Growing",
                        "requirements": ["AQSIQ registration", "Cold treatment protocol"],
                        "port_of_entry": "Hong Kong/Singapore",
                        "shipping_route": "Durban → Singapore (20-25 days)"
                    }
                ],
                "total_export_value_usd": 28000000,
                "export_volume_tonnes": 32000,
                "peak_season": "May-October",
                "quality_standards": ["Class I EU standards", "Brix >10 for oranges"],
                "key_buyers": ["Capespan", "South Produce", "ZZ2"],
                "market_trends": "Counter-seasonal advantage for EU market",
                "export_incentives": "Cold chain infrastructure support"
            }
        }
    
    def get_crop_export_data(self, crop: str) -> Optional[Dict]:
        """Get export data for a specific crop."""
        crop_lower = crop.lower()
        
        # Try exact match first
        if crop_lower in self.markets_data:
            return self.markets_data[crop_lower]
        
        # Try partial match
        for key in self.markets_data.keys():
            if crop_lower in key or key in crop_lower:
                return self.markets_data[key]
        
        return None
    
    def get_all_crops(self) -> List[str]:
        """Get list of all crops with export data."""
        return list(self.markets_data.keys())
    
    def get_top_destinations(self, crop: str, top_n: int = 5) -> List[Dict]:
        """Get top export destinations for a crop."""
        crop_data = self.get_crop_export_data(crop)
        if not crop_data:
            return []
        
        destinations = crop_data.get('export_destinations', [])
        return sorted(destinations, key=lambda x: x['percentage'], reverse=True)[:top_n]
    
    def get_market_summary(self, crop: str) -> str:
        """Get a formatted market summary for a crop."""
        crop_data = self.get_crop_export_data(crop)
        if not crop_data:
            return f"No export market data available for {crop}"
        
        summary = []
        summary.append(f"🌍 **{crop_data['crop_name']} Export Market Intelligence**\\n")
        summary.append(f"📊 **Market Overview:**")
        summary.append(f"- Total Export Value: ${crop_data['total_export_value_usd']:,}")
        summary.append(f"- Export Volume: {crop_data['export_volume_tonnes']:,} tonnes")
        summary.append(f"- Peak Season: {crop_data['peak_season']}\\n")
        
        summary.append(f"🎯 **Top Export Destinations:**")
        for dest in self.get_top_destinations(crop, 3):
            summary.append(f"- **{dest['country']}** ({dest['percentage']}%)")
            summary.append(f"  - Price: ${dest['avg_price_usd_per_kg']}/kg")
            summary.append(f"  - Demand: {dest['demand_level']}")
            summary.append(f"  - Route: {dest['shipping_route']}")
        
        summary.append(f"\\n📋 **Key Requirements:**")
        for standard in crop_data['quality_standards'][:3]:
            summary.append(f"- {standard}")
        
        summary.append(f"\\n📈 **Market Trends:** {crop_data['market_trends']}")
        
        if crop_data.get('export_incentives'):
            summary.append(f"\\n💰 **Export Incentives:** {crop_data['export_incentives']}")
        
        return "\\n".join(summary)
    
    def search_by_destination(self, country: str) -> List[Dict]:
        """Find all crops exported to a specific country."""
        results = []
        
        for crop_key, crop_data in self.markets_data.items():
            for dest in crop_data.get('export_destinations', []):
                if country.lower() in dest['country'].lower():
                    results.append({
                        'crop': crop_data['crop_name'],
                        'percentage': dest['percentage'],
                        'price': dest['avg_price_usd_per_kg'],
                        'demand': dest['demand_level'],
                        'requirements': dest['requirements']
                    })
        
        return sorted(results, key=lambda x: x['percentage'], reverse=True)
    
    def compare_markets(self, crop1: str, crop2: str) -> Dict:
        """Compare export markets for two crops."""
        data1 = self.get_crop_export_data(crop1)
        data2 = self.get_crop_export_data(crop2)
        
        if not data1 or not data2:
            return {"error": "One or both crops not found"}
        
        return {
            'crop1': {
                'name': data1['crop_name'],
                'value': data1['total_export_value_usd'],
                'volume': data1['export_volume_tonnes'],
                'destinations': len(data1['export_destinations'])
            },
            'crop2': {
                'name': data2['crop_name'],
                'value': data2['total_export_value_usd'],
                'volume': data2['export_volume_tonnes'],
                'destinations': len(data2['export_destinations'])
            },
            'comparison': {
                'value_ratio': data1['total_export_value_usd'] / data2['total_export_value_usd'],
                'volume_ratio': data1['export_volume_tonnes'] / data2['export_volume_tonnes']
            }
        }
    
    def get_certification_requirements(self, crop: str) -> List[str]:
        """Get all certification requirements for a crop across all markets."""
        crop_data = self.get_crop_export_data(crop)
        if not crop_data:
            return []
        
        all_requirements = set()
        for dest in crop_data.get('export_destinations', []):
            all_requirements.update(dest.get('requirements', []))
        
        return sorted(list(all_requirements))
    
    def update_crop_data(self, crop: str, data: Dict):
        """Update export data for a crop."""
        crop_lower = crop.lower()
        self.markets_data[crop_lower] = data
        self.save_data()
        logger.info(f"Updated export data for {crop}")


if __name__ == "__main__":
    # Test the export intelligence system
    emi = ExportMarketIntelligence()
    
    # Initialize sample data
    emi.save_data()
    
    print("Testing Export Market Intelligence System:\\n")
    
    # Test crop summary
    print(emi.get_market_summary("tobacco"))
    print("\\n" + "="*80 + "\\n")
    
    # Test destination search
    china_exports = emi.search_by_destination("China")
    print(f"Crops exported to China: {len(china_exports)}")
    for crop in china_exports:
        print(f"- {crop['crop']}: {crop['percentage']}% (${crop['price']}/kg)")
