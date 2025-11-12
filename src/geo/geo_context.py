"""
Geographic context module for AgriEvidence.
Fetches district-level data including region, rainfall, soil type, and market info.
"""

import json
import math
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class GeoContext:
    """Handles geographic context for agricultural queries."""
    
    def __init__(self, provinces_json_path: Optional[str] = None):
        """
        Initialize the GeoContext with province data.
        
        Args:
            provinces_json_path: Path to provinces.json file. If None, uses default location.
        """
        if provinces_json_path is None:
            provinces_json_path = Path(__file__).parent / "provinces.json"
        
        with open(provinces_json_path, 'r') as f:
            self.data = json.load(f)
        
        # Build district lookup index for fast access
        self.district_index = {}
        for province in self.data['provinces']:
            for district in province['districts']:
                district_key = district['name'].lower()
                self.district_index[district_key] = {
                    **district,
                    'province': province['name']
                }
    
    def get_district_by_name(self, district_name: str) -> Optional[Dict]:
        """
        Get district information by name.
        
        Args:
            district_name: Name of the district (case-insensitive)
            
        Returns:
            Dictionary with district information or None if not found
        """
        district_key = district_name.lower().strip()
        return self.district_index.get(district_key)
    
    def get_district_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Find the nearest district based on coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with nearest district information
        """
        min_distance = float('inf')
        nearest_district = None
        
        for district_info in self.district_index.values():
            coords = district_info['coordinates']
            distance = self._calculate_distance(
                lat, lon, 
                coords['lat'], coords['lon']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_district = district_info
        
        return nearest_district
    
    def get_region_info(self, region: str) -> Optional[Dict]:
        """
        Get information about a natural region.
        
        Args:
            region: Natural region code (e.g., "Region I", "Region IIa")
            
        Returns:
            Dictionary with region information
        """
        return self.data['natural_regions'].get(region)
    
    def get_all_districts(self) -> List[str]:
        """Get list of all district names."""
        return sorted(self.district_index.keys())
    
    def get_districts_by_province(self, province_name: str) -> List[Dict]:
        """
        Get all districts in a province.
        
        Args:
            province_name: Name of the province
            
        Returns:
            List of district dictionaries
        """
        for province in self.data['provinces']:
            if province['name'].lower() == province_name.lower():
                return province['districts']
        return []
    
    def get_districts_by_region(self, region: str) -> List[Dict]:
        """
        Get all districts in a natural region.
        
        Args:
            region: Natural region code (e.g., "Region IV")
            
        Returns:
            List of district dictionaries
        """
        districts = []
        for district_info in self.district_index.values():
            if district_info['region'] == region:
                districts.append(district_info)
        return districts
    
    def format_context(self, district_info: Dict) -> Dict:
        """
        Format district information for inclusion in prompts.
        
        Args:
            district_info: District information dictionary
            
        Returns:
            Formatted context dictionary
        """
        region_info = self.get_region_info(district_info['region'])
        
        context = {
            'district': district_info['name'],
            'province': district_info['province'],
            'region': district_info['region'],
            'rainfall': district_info['rainfall'],
            'soil_type': district_info['soil_type'],
            'nearest_market': district_info['nearest_market'],
            'coordinates': district_info['coordinates']
        }
        
        # Add region-specific recommendations
        if region_info:
            context['region_description'] = region_info['description']
            context['recommended_crops'] = region_info['recommended_crops']
            context['growing_season'] = region_info['growing_season']
            if 'maize_planting_window' in region_info:
                context['maize_planting_window'] = region_info['maize_planting_window']
        
        return context
    
    def format_context_string(self, district_info: Dict) -> str:
        """
        Format district information as a string for prompt injection.
        
        Args:
            district_info: District information dictionary
            
        Returns:
            Formatted context string
        """
        context = self.format_context(district_info)
        
        lines = [
            f"District: {context['district']}, Province: {context['province']}, Region: {context['region']}",
            f"Rainfall: {context['rainfall']} | Soil: {context['soil_type']} | Market: {context['nearest_market']}"
        ]
        
        if 'region_description' in context:
            lines.append(f"Region Type: {context['region_description']}")
        
        if 'recommended_crops' in context:
            crops = ', '.join(context['recommended_crops'])
            lines.append(f"Recommended Crops: {crops}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance


# Convenience function
def get_geo_context(
    district: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> Optional[Dict]:
    """
    Get geographic context for a location.
    
    Args:
        district: District name (if known)
        lat: Latitude (if district not provided)
        lon: Longitude (if district not provided)
        
    Returns:
        Formatted geographic context dictionary or None
    """
    geo = GeoContext()
    
    if district:
        district_info = geo.get_district_by_name(district)
    elif lat is not None and lon is not None:
        district_info = geo.get_district_by_coordinates(lat, lon)
    else:
        return None
    
    if district_info:
        return geo.format_context(district_info)
    
    return None
