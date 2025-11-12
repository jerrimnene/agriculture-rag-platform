"""
District Context Engine
Provides comprehensive district-specific data for holistic agricultural advisory
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DistrictContextEngine:
    """Fetches and manages comprehensive district-specific agricultural data."""
    
    # Path to compiled district databases
    DISTRICTS_DB_PATH = Path(__file__).parent.parent.parent / "data" / "districts_database.json"
    DISTRICTS_FULL_PATH = Path(__file__).parent.parent.parent / "data" / "districts_full.json"
    DISTRICTS_DEEP_PATH = Path(__file__).parent.parent.parent / "data" / "districts_deep.json"
    DISTRICTS_CITED_PATH = Path(__file__).parent.parent.parent / "data" / "districts_cited.json"
    DISTRICTS_EVIDENCE_PATH = Path(__file__).parent.parent.parent / "data" / "districts_evidence.json"
    
    def __init__(self):
        """Initialize with district data."""
        self.district_data = self._load_district_data()
        self.district_full_data = self._load_full_district_data()  # Enhanced extraction
        self.district_deep_data = self._load_deep_district_data()  # Deep extraction with ALL pages
        self.district_cited_data = self._load_cited_district_data()  # Citation-tracked extraction
        self.district_evidence = self._load_evidence_data()  # Evidence for audit trails
        self.market_data = self._load_market_data()
        self.district_challenges = self._load_district_challenges()
        
    def _load_deep_district_data(self) -> Dict:
        """Load deep extracted district data (all pages, tables, comprehensive)."""
        if self.DISTRICTS_DEEP_PATH.exists():
            try:
                with open(self.DISTRICTS_DEEP_PATH, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded DEEP extraction data for {len(data)} districts")
                    return data
            except Exception as e:
                logger.warning(f"Could not load deep extraction data: {e}")
        return {}
    
    def _load_cited_district_data(self) -> Dict:
        """Load citation-tracked district data (Level 5 with full citations)."""
        if self.DISTRICTS_CITED_PATH.exists():
            try:
                with open(self.DISTRICTS_CITED_PATH, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded CITED extraction data for {len(data)} districts with citations")
                    return data
            except Exception as e:
                logger.warning(f"Could not load cited data: {e}")
        return {}
    
    def _load_evidence_data(self) -> Dict:
        """Load evidence/audit trail data for all citations."""
        if self.DISTRICTS_EVIDENCE_PATH.exists():
            try:
                with open(self.DISTRICTS_EVIDENCE_PATH, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded EVIDENCE data for {len(data)} districts")
                    return data
            except Exception as e:
                logger.warning(f"Could not load evidence data: {e}")
        return {}
    
    def _load_full_district_data(self) -> Dict:
        """Load enriched district data extracted from PDFs."""
        if self.DISTRICTS_FULL_PATH.exists():
            try:
                with open(self.DISTRICTS_FULL_PATH, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded enriched data for {len(data)} districts from extraction")
                    return data
            except Exception as e:
                logger.warning(f"Could not load enriched data: {e}")
        return {}
    
    def _load_district_data(self) -> Dict:
        """Load district geographic and agricultural data from JSON database."""
        
        # Try to load from JSON database first
        if self.DISTRICTS_DB_PATH.exists():
            try:
                with open(self.DISTRICTS_DB_PATH, 'r') as f:
                    loaded_data = json.load(f)
                    logger.info(f"Loaded {len(loaded_data)} districts from JSON database")
                    return loaded_data
            except Exception as e:
                logger.warning(f"Could not load from JSON database: {e}. Using fallback data.")
        
        # Fallback to hardcoded data for backward compatibility
        return {
            "Harare": {
                "name": "Harare",
                "province": "Harare",
                "agro_zone": "IIb",
                "rainfall_mm": 750,
                "soil_type": "Sandy loam to clay",
                "elevation": 1480,
                "primary_crops": ["maize", "tobacco", "vegetables"],
                "primary_livestock": ["poultry", "cattle", "goats"],
                "season_start": "November",
                "season_end": "March",
                "nearest_major_city": "Harare",
                "coordinates": {"lat": -17.8252, "lon": 31.0335}
            },
            "Binga": {
                "province": "Matabeleland North",
                "agro_zone": "IV",
                "rainfall_mm": 450,
                "soil_type": "Sandy, shallow",
                "elevation": 700,
                "primary_crops": ["millet", "sorghum", "groundnuts"],
                "primary_livestock": ["goats", "cattle", "poultry"],
                "season_start": "December",
                "season_end": "February",
                "nearest_major_city": "Hwange",
                "coordinates": {"lat": -17.4667, "lon": 27.3167},
                "challenges": ["drought", "low_rainfall", "sandy_soils", "remote_location"]
            },
            "Chitungwiza": {
                "province": "Harare",
                "agro_zone": "IIb",
                "rainfall_mm": 750,
                "soil_type": "Clay loam",
                "elevation": 1450,
                "primary_crops": ["maize", "vegetables", "beans"],
                "primary_livestock": ["poultry", "rabbits", "goats"],
                "season_start": "November",
                "season_end": "March",
                "nearest_major_city": "Harare",
                "coordinates": {"lat": -17.9333, "lon": 31.0333}
            },
            "Bulawayo": {
                "province": "Bulawayo",
                "agro_zone": "III",
                "rainfall_mm": 550,
                "soil_type": "Red clay",
                "elevation": 1350,
                "primary_crops": ["maize", "sorghum", "sunflower"],
                "primary_livestock": ["cattle", "goats", "poultry"],
                "season_start": "November",
                "season_end": "March",
                "nearest_major_city": "Bulawayo",
                "coordinates": {"lat": -20.1500, "lon": 28.5833}
            }
        }
    
    def _load_market_data(self) -> Dict:
        """Load market and trading center data by district."""
        return {
            "Harare": {
                "major_markets": ["Mbare Musika", "Borrowdale", "Eastlea Vegetable Market"],
                "trading_centers": ["Warren Park", "Budiriro", "Mufakose"],
                "main_commodities": ["vegetables", "maize", "beans", "groundnuts"],
                "avg_buyer_density": "high",
                "transport_cost_to_center": 20,  # ZWL per bag
                "market_days": ["daily"]
            },
            "Binga": {
                "major_markets": ["Binga Growth Point", "Siabuwa"],
                "trading_centers": ["Binga", "Karoi", "Nyaminyami"],
                "main_commodities": ["millet", "sorghum", "goats", "cattle"],
                "avg_buyer_density": "low",
                "transport_cost_to_center": 150,  # ZWL per bag
                "market_days": ["Wednesday", "Saturday"],
                "nearby_urban_markets": ["Hwange (150km)", "Victoria Falls (200km)"]
            },
            "Chitungwiza": {
                "major_markets": ["Chitungwiza Market", "Unit F"],
                "trading_centers": ["Seke", "St Marys", "Zengeza"],
                "main_commodities": ["vegetables", "maize", "beans"],
                "avg_buyer_density": "high",
                "transport_cost_to_center": 15,
                "market_days": ["daily"],
                "nearby_urban_markets": ["Harare (25km)"]
            },
            "Bulawayo": {
                "major_markets": ["Sakubva Market", "Bulawayo City Market"],
                "trading_centers": ["Entumbane", "Pumula", "Njuba"],
                "main_commodities": ["maize", "groundnuts", "sorghum", "cattle"],
                "avg_buyer_density": "high",
                "transport_cost_to_center": 30,
                "market_days": ["daily"]
            }
        }
    
    def _load_district_challenges(self) -> Dict:
        """Load farming challenges and difficulty factors by district."""
        return {
            "Binga": {
                "difficulty_level": "high",
                "primary_challenges": [
                    "Low rainfall (450mm) - unsuitable for maize",
                    "Sandy, shallow soils - poor water retention",
                    "Remote location - high transport costs",
                    "Limited market access - low buyer density",
                    "Frequent droughts - crop failure risk"
                ],
                "viable_alternatives": [
                    "Drought-resistant crops: millet, sorghum, groundnuts",
                    "Livestock-focused: goat farming, small ruminants",
                    "Rainwater harvesting: conservation agriculture",
                    "Supply chain: source produce from Hwange, resell locally"
                ],
                "mitigation_strategies": [
                    "Diversify with drought-tolerant varieties",
                    "Implement water harvesting structures",
                    "Partner with Hwange/Victoria Falls markets for supplies",
                    "Focus on value-added products (milled grains, dried vegetables)",
                    "Cooperative marketing to reduce transport costs"
                ]
            },
            "Harare": {
                "difficulty_level": "low",
                "primary_challenges": [],
                "viable_alternatives": ["maize", "tobacco", "vegetables", "poultry"],
                "mitigation_strategies": ["standard_farming_practices"]
            }
        }
    
    def get_district_overview(self, district: str) -> Dict[str, Any]:
        """Get comprehensive overview for a district."""
        if district not in self.district_data:
            return {"error": f"District {district} not found"}
        
        overview = {
            "district": district,
            "geography": self.district_data[district],
            "markets": self.market_data.get(district, {}),
            "challenges": self.district_challenges.get(district, {})
        }
        
        return overview
    
    def get_viable_crops(self, district: str) -> List[Dict]:
        """Get viable crop recommendations for a district."""
        if district not in self.district_data:
            return []
        
        data = self.district_data[district]
        difficulties = self.district_challenges.get(district, {})
        
        viable = {
            "primary_crops": data.get("primary_crops", []),
            "difficulty_level": difficulties.get("difficulty_level", "low"),
            "alternatives": difficulties.get("viable_alternatives", [])
        }
        
        return viable
    
    def get_market_recommendations(self, district: str, crop: str) -> Dict:
        """Get market recommendations for a crop in a district."""
        market_info = self.market_data.get(district, {})
        
        recommendations = {
            "district": district,
            "crop": crop,
            "local_markets": market_info.get("major_markets", []),
            "trading_centers": market_info.get("trading_centers", []),
            "transport_cost": market_info.get("transport_cost_to_center"),
            "buyer_density": market_info.get("avg_buyer_density"),
            "nearby_cities": market_info.get("nearby_urban_markets", []),
            "supply_chain_tip": self._get_supply_chain_tip(district, crop)
        }
        
        return recommendations
    
    def _get_supply_chain_tip(self, district: str, crop: str) -> str:
        """Generate supply chain recommendations."""
        if district == "Binga":
            if crop in ["millet", "sorghum"]:
                return "Source from Hwange (150km away), process locally, sell to Bulawayo/Victoria Falls urban markets"
            else:
                return "Consider importing from Hwange/Karoi, add value through processing"
        
        return "Use local markets. Connect with cooperatives to reduce transport costs."
    
    def get_difficulty_assessment(self, district: str) -> Dict:
        """Get farming difficulty assessment and recommendations."""
        challenges = self.district_challenges.get(district, {})
        
        assessment = {
            "district": district,
            "difficulty_level": challenges.get("difficulty_level", "low"),
            "primary_challenges": challenges.get("primary_challenges", []),
            "mitigation_strategies": challenges.get("mitigation_strategies", []),
            "alternative_livelihoods": challenges.get("viable_alternatives", [])
        }
        
        return assessment
    
    def get_seasonal_calendar(self, district: str) -> Dict:
        """Get seasonal farming calendar for district."""
        data = self.district_data[district]
        
        return {
            "district": district,
            "season_start": data.get("season_start"),
            "season_end": data.get("season_end"),
            "rainfall_mm": data.get("rainfall_mm"),
            "agro_zone": data.get("agro_zone"),
            "primary_crops": data.get("primary_crops", [])
        }
    
    def list_all_districts(self) -> List[str]:
        """List all available districts."""
        return list(self.district_data.keys())
    
    def get_nearby_districts(self, district: str, radius_km: int = 200) -> List[str]:
        """Get nearby districts for supply chain optimization."""
        if district not in self.district_data:
            return []
        
        # Simplified nearby districts - in production, use real distance calculation
        proximity_map = {
            "Binga": ["Hwange", "Kariba"],
            "Harare": ["Chitungwiza", "Epworth"],
            "Chitungwiza": ["Harare", "Epworth"],
            "Bulawayo": ["Plumtree", "Gwanda"]
        }
        
        return proximity_map.get(district, [])
