"""
Weather API integration for AgriEvidence using Open-Meteo.
Provides real-time and forecast weather data for agricultural decision-making.
"""

import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Interface to Open-Meteo weather API for agricultural data."""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self):
        """Initialize the weather API client."""
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather conditions for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with current weather data or None on error
        """
        try:
            session = await self._get_session()
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m',
                'timezone': 'Africa/Harare'
            }
            
            async with session.get(f"{self.BASE_URL}/forecast", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current = data.get('current', {})
                    
                    return {
                        'temperature': current.get('temperature_2m'),
                        'humidity': current.get('relative_humidity_2m'),
                        'precipitation': current.get('precipitation', 0),
                        'rain': current.get('rain', 0),
                        'wind_speed': current.get('wind_speed_10m'),
                        'weather_code': current.get('weather_code'),
                        'time': current.get('time'),
                        'description': self._get_weather_description(current.get('weather_code'))
                    }
                else:
                    logger.error(f"Weather API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    async def get_daily_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict]:
        """
        Get daily weather forecast.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of forecast days (default 7)
            
        Returns:
            Dictionary with forecast data or None on error
        """
        try:
            session = await self._get_session()
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_probability_max,weather_code',
                'timezone': 'Africa/Harare',
                'forecast_days': min(days, 16)  # API limit
            }
            
            async with session.get(f"{self.BASE_URL}/forecast", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    daily = data.get('daily', {})
                    
                    forecast_days = []
                    times = daily.get('time', [])
                    
                    for i in range(len(times)):
                        forecast_days.append({
                            'date': times[i],
                            'temp_max': daily.get('temperature_2m_max', [])[i],
                            'temp_min': daily.get('temperature_2m_min', [])[i],
                            'precipitation_sum': daily.get('precipitation_sum', [])[i],
                            'rain_sum': daily.get('rain_sum', [])[i],
                            'precipitation_probability': daily.get('precipitation_probability_max', [])[i],
                            'weather_code': daily.get('weather_code', [])[i],
                            'description': self._get_weather_description(daily.get('weather_code', [])[i])
                        })
                    
                    return {
                        'location': {'latitude': lat, 'longitude': lon},
                        'forecast': forecast_days
                    }
                else:
                    logger.error(f"Forecast API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None
    
    async def get_historical_precipitation(
        self, 
        lat: float, 
        lon: float, 
        days_back: int = 30
    ) -> Optional[Dict]:
        """
        Get historical precipitation data.
        
        Args:
            lat: Latitude
            lon: Longitude
            days_back: Number of days to look back
            
        Returns:
            Dictionary with historical data or None on error
        """
        try:
            session = await self._get_session()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'daily': 'precipitation_sum,rain_sum,temperature_2m_max,temperature_2m_min',
                'timezone': 'Africa/Harare'
            }
            
            async with session.get(f"{self.BASE_URL}/forecast", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    daily = data.get('daily', {})
                    
                    precipitation_data = daily.get('precipitation_sum', [])
                    rain_data = daily.get('rain_sum', [])
                    
                    total_precipitation = sum(precipitation_data)
                    total_rain = sum(rain_data)
                    avg_temp_max = sum(daily.get('temperature_2m_max', [])) / len(precipitation_data) if precipitation_data else 0
                    
                    return {
                        'period_days': days_back,
                        'total_precipitation_mm': round(total_precipitation, 1),
                        'total_rain_mm': round(total_rain, 1),
                        'avg_temp_max': round(avg_temp_max, 1),
                        'daily_data': {
                            'dates': daily.get('time', []),
                            'precipitation': precipitation_data,
                            'rain': rain_data
                        }
                    }
                else:
                    logger.error(f"Historical weather API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    async def get_agricultural_summary(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get agricultural weather summary combining current and forecast data.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Comprehensive agricultural weather summary
        """
        current = await self.get_current_weather(lat, lon)
        forecast = await self.get_daily_forecast(lat, lon, days=7)
        historical = await self.get_historical_precipitation(lat, lon, days_back=30)
        
        if not current or not forecast or not historical:
            return None
        
        # Calculate forecast totals
        forecast_rain = sum(day['rain_sum'] for day in forecast['forecast'])
        rainy_days = sum(1 for day in forecast['forecast'] if day['rain_sum'] > 1.0)
        
        return {
            'current': current,
            'forecast_7day': {
                'total_rain_mm': round(forecast_rain, 1),
                'rainy_days': rainy_days,
                'days': forecast['forecast'][:7]
            },
            'historical_30day': historical,
            'agricultural_insights': self._generate_agricultural_insights(
                current, forecast['forecast'], historical
            )
        }
    
    def _generate_agricultural_insights(
        self, 
        current: Dict, 
        forecast: List[Dict], 
        historical: Dict
    ) -> List[str]:
        """Generate agricultural recommendations based on weather data."""
        insights = []
        
        # Current conditions
        if current.get('temperature', 0) > 35:
            insights.append("⚠️ High temperatures - consider irrigation and avoid planting")
        elif current.get('temperature', 0) < 10:
            insights.append("⚠️ Low temperatures - frost risk for tender crops")
        
        # Rainfall analysis
        monthly_rain = historical.get('total_rain_mm', 0)
        if monthly_rain < 50:
            insights.append("🌵 Low rainfall this month - drought stress likely")
        elif monthly_rain > 200:
            insights.append("💧 High rainfall this month - monitor for waterlogging")
        
        # Forecast analysis
        forecast_rain = sum(day.get('rain_sum', 0) for day in forecast)
        if forecast_rain > 50:
            insights.append("🌧️ Significant rain expected - good for planting")
        elif forecast_rain < 5:
            insights.append("☀️ Dry week ahead - ensure adequate irrigation")
        
        # Humidity
        if current.get('humidity', 0) > 80:
            insights.append("💨 High humidity - increased disease risk")
        
        return insights
    
    @staticmethod
    def _get_weather_description(weather_code: Optional[int]) -> str:
        """Convert WMO weather code to description."""
        if weather_code is None:
            return "Unknown"
        
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with hail"
        }
        
        return weather_codes.get(weather_code, f"Code {weather_code}")


# Synchronous wrapper for compatibility
def get_current_weather_sync(lat: float, lon: float) -> Optional[Dict]:
    """Synchronous wrapper for get_current_weather."""
    weather_api = WeatherAPI()
    try:
        return asyncio.run(weather_api.get_current_weather(lat, lon))
    finally:
        asyncio.run(weather_api.close())


def get_agricultural_summary_sync(lat: float, lon: float) -> Optional[Dict]:
    """Synchronous wrapper for get_agricultural_summary."""
    weather_api = WeatherAPI()
    try:
        return asyncio.run(weather_api.get_agricultural_summary(lat, lon))
    finally:
        asyncio.run(weather_api.close())
