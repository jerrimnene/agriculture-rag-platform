"""
Historical Data Archive
Time-series database for crop yields, market prices, weather patterns, and rainfall
with trend analysis, year-over-year comparisons, and anomaly detection
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """Categories of historical data."""
    CROP_YIELD = "crop_yield"
    MARKET_PRICE = "market_price"
    WEATHER = "weather"
    RAINFALL = "rainfall"
    TEMPERATURE = "temperature"
    PRODUCTION_VOLUME = "production_volume"


@dataclass
class TimeSeriesEntry:
    """Single time-series data point."""
    timestamp: str  # ISO format
    value: float
    unit: str
    location: Optional[str] = None
    crop: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Trend analysis results."""
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    average: float
    median: float
    min_value: float
    max_value: float
    std_deviation: float
    growth_rate: Optional[float] = None  # percentage
    periods_analyzed: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class YearOverYearComparison:
    """Year-over-year comparison results."""
    year1: int
    year2: int
    value1: float
    value2: float
    change_absolute: float
    change_percentage: float
    direction: str  # increase, decrease, stable
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Anomaly:
    """Detected anomaly in time-series data."""
    timestamp: str
    value: float
    expected_range: Tuple[float, float]
    deviation_score: float  # Standard deviations from mean
    severity: str  # low, medium, high
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['expected_range'] = list(self.expected_range)
        return result


class HistoricalDataArchive:
    """Main historical data archive and analysis system."""
    
    def __init__(self, storage_path: str = "./data/historical"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.data_store = self.storage_path / "timeseries.json"
        self.analysis_cache = self.storage_path / "analysis_cache.json"
        
        # Load existing data
        self.timeseries_db: Dict[str, List[TimeSeriesEntry]] = self._load_data()
        
        logger.info(f"Historical Data Archive initialized with {len(self.timeseries_db)} time series")
    
    def _load_data(self) -> Dict[str, List[TimeSeriesEntry]]:
        """Load time-series data."""
        if self.data_store.exists():
            with open(self.data_store, 'r') as f:
                data = json.load(f)
                db = {}
                for series_id, entries in data.items():
                    db[series_id] = [TimeSeriesEntry(**e) for e in entries]
                return db
        return {}
    
    def _save_data(self):
        """Save time-series data."""
        data = {}
        for series_id, entries in self.timeseries_db.items():
            data[series_id] = [e.to_dict() for e in entries]
        
        with open(self.data_store, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_series_id(
        self,
        category: str,
        crop: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """Generate time-series ID."""
        parts = [category]
        if crop:
            parts.append(crop.lower().replace(' ', '_'))
        if location:
            parts.append(location.lower().replace(' ', '_'))
        return "_".join(parts)
    
    def add_data_point(
        self,
        category: DataCategory,
        timestamp: str,
        value: float,
        unit: str,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add a data point to the archive."""
        series_id = self._generate_series_id(category.value, crop, location)
        
        entry = TimeSeriesEntry(
            timestamp=timestamp,
            value=value,
            unit=unit,
            location=location,
            crop=crop,
            metadata=metadata
        )
        
        if series_id not in self.timeseries_db:
            self.timeseries_db[series_id] = []
        
        self.timeseries_db[series_id].append(entry)
        
        # Sort by timestamp
        self.timeseries_db[series_id].sort(key=lambda e: e.timestamp)
        
        self._save_data()
        logger.debug(f"Added data point to {series_id}")
        return True
    
    def get_time_series(
        self,
        category: DataCategory,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[TimeSeriesEntry]:
        """Retrieve time-series data with optional filtering."""
        series_id = self._generate_series_id(category.value, crop, location)
        
        if series_id not in self.timeseries_db:
            return []
        
        entries = self.timeseries_db[series_id]
        
        # Filter by date range
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        
        return entries
    
    def analyze_trend(
        self,
        category: DataCategory,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[TrendAnalysis]:
        """Analyze trend in time-series data."""
        entries = self.get_time_series(category, crop, location, start_date, end_date)
        
        if len(entries) < 2:
            logger.warning(f"Insufficient data for trend analysis: {len(entries)} points")
            return None
        
        values = [e.value for e in entries]
        
        # Calculate statistics
        avg = statistics.mean(values)
        median = statistics.median(values)
        min_val = min(values)
        max_val = max(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Calculate trend direction using simple linear regression
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x_values)
        y_mean = avg
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend direction and strength
        if abs(slope) < std_dev * 0.1:
            direction = "stable"
            strength = 0.0
        elif slope > 0:
            direction = "increasing"
            strength = min(abs(slope) / (std_dev if std_dev > 0 else 1), 1.0)
        else:
            direction = "decreasing"
            strength = min(abs(slope) / (std_dev if std_dev > 0 else 1), 1.0)
        
        # Calculate growth rate (first to last)
        if values[0] != 0:
            growth_rate = ((values[-1] - values[0]) / values[0]) * 100
        else:
            growth_rate = None
        
        return TrendAnalysis(
            trend_direction=direction,
            trend_strength=strength,
            average=avg,
            median=median,
            min_value=min_val,
            max_value=max_val,
            std_deviation=std_dev,
            growth_rate=growth_rate,
            periods_analyzed=len(entries)
        )
    
    def compare_year_over_year(
        self,
        category: DataCategory,
        year1: int,
        year2: int,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        aggregation: str = "average"  # average, sum, median
    ) -> Optional[YearOverYearComparison]:
        """Compare data between two years."""
        # Get data for each year
        start1 = f"{year1}-01-01"
        end1 = f"{year1}-12-31"
        start2 = f"{year2}-01-01"
        end2 = f"{year2}-12-31"
        
        data1 = self.get_time_series(category, crop, location, start1, end1)
        data2 = self.get_time_series(category, crop, location, start2, end2)
        
        if not data1 or not data2:
            logger.warning(f"Insufficient data for YoY comparison: {len(data1)} vs {len(data2)}")
            return None
        
        values1 = [e.value for e in data1]
        values2 = [e.value for e in data2]
        
        # Aggregate values
        if aggregation == "average":
            value1 = statistics.mean(values1)
            value2 = statistics.mean(values2)
        elif aggregation == "sum":
            value1 = sum(values1)
            value2 = sum(values2)
        elif aggregation == "median":
            value1 = statistics.median(values1)
            value2 = statistics.median(values2)
        else:
            value1 = statistics.mean(values1)
            value2 = statistics.mean(values2)
        
        # Calculate change
        change_abs = value2 - value1
        change_pct = (change_abs / value1 * 100) if value1 != 0 else 0
        
        # Determine direction
        if abs(change_pct) < 5:
            direction = "stable"
        elif change_pct > 0:
            direction = "increase"
        else:
            direction = "decrease"
        
        return YearOverYearComparison(
            year1=year1,
            year2=year2,
            value1=value1,
            value2=value2,
            change_absolute=change_abs,
            change_percentage=change_pct,
            direction=direction
        )
    
    def detect_anomalies(
        self,
        category: DataCategory,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        threshold_stdev: float = 2.0
    ) -> List[Anomaly]:
        """Detect anomalies in time-series data."""
        entries = self.get_time_series(category, crop, location, start_date, end_date)
        
        if len(entries) < 10:
            logger.warning(f"Insufficient data for anomaly detection: {len(entries)} points")
            return []
        
        values = [e.value for e in entries]
        
        # Calculate mean and standard deviation
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Detect anomalies
        anomalies = []
        
        for entry in entries:
            deviation = abs(entry.value - mean) / std_dev if std_dev > 0 else 0
            
            if deviation >= threshold_stdev:
                # Calculate expected range
                lower_bound = mean - threshold_stdev * std_dev
                upper_bound = mean + threshold_stdev * std_dev
                
                # Determine severity
                if deviation >= 3.0:
                    severity = "high"
                elif deviation >= 2.5:
                    severity = "medium"
                else:
                    severity = "low"
                
                anomalies.append(Anomaly(
                    timestamp=entry.timestamp,
                    value=entry.value,
                    expected_range=(lower_bound, upper_bound),
                    deviation_score=deviation,
                    severity=severity
                ))
        
        return anomalies
    
    def get_seasonal_pattern(
        self,
        category: DataCategory,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        years: int = 3
    ) -> Dict[int, float]:
        """Get average values by month (seasonal pattern)."""
        # Get recent years of data
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=365 * years)).isoformat()
        
        entries = self.get_time_series(category, crop, location, start_date, end_date)
        
        if not entries:
            return {}
        
        # Group by month
        monthly_values = {i: [] for i in range(1, 13)}
        
        for entry in entries:
            month = datetime.fromisoformat(entry.timestamp).month
            monthly_values[month].append(entry.value)
        
        # Calculate average for each month
        monthly_averages = {}
        for month, values in monthly_values.items():
            if values:
                monthly_averages[month] = statistics.mean(values)
        
        return monthly_averages
    
    def get_statistics(self) -> Dict:
        """Get archive statistics."""
        total_series = len(self.timeseries_db)
        total_points = sum(len(entries) for entries in self.timeseries_db.values())
        
        by_category = {}
        for series_id in self.timeseries_db.keys():
            category = series_id.split('_')[0]
            by_category[category] = by_category.get(category, 0) + 1
        
        # Find oldest and newest data points
        all_timestamps = []
        for entries in self.timeseries_db.values():
            all_timestamps.extend([e.timestamp for e in entries])
        
        oldest = min(all_timestamps) if all_timestamps else None
        newest = max(all_timestamps) if all_timestamps else None
        
        return {
            'total_time_series': total_series,
            'total_data_points': total_points,
            'by_category': by_category,
            'oldest_data': oldest,
            'newest_data': newest
        }


if __name__ == "__main__":
    # Test Historical Data Archive
    archive = HistoricalDataArchive()
    
    print("\n=== HISTORICAL DATA ARCHIVE TEST ===\n")
    
    # Add sample crop yield data for maize in Harare over 5 years
    print("1. Adding historical crop yield data...")
    for year in range(2019, 2024):
        for month in [4, 5, 6]:  # Harvest season
            timestamp = f"{year}-{month:02d}-15T12:00:00"
            # Simulate yield data with trend and variation
            base_yield = 4.5 + (year - 2019) * 0.3  # Increasing trend
            variation = (-1)**month * 0.2  # Seasonal variation
            value = base_yield + variation
            
            archive.add_data_point(
                category=DataCategory.CROP_YIELD,
                timestamp=timestamp,
                value=value,
                unit="tonnes/ha",
                crop="maize",
                location="Harare",
                metadata={'season': f'{year-1}/{year}'}
            )
    print("✓ Added 15 data points\n")
    
    # Add market price data
    print("2. Adding market price data...")
    for year in range(2019, 2024):
        for month in range(1, 13):
            timestamp = f"{year}-{month:02d}-01T12:00:00"
            # Simulate price with inflation
            base_price = 300 + (year - 2019) * 50
            seasonal_factor = 1.0 + 0.1 * ((month - 6) ** 2) / 36  # Price peaks mid-year
            value = base_price * seasonal_factor
            
            archive.add_data_point(
                category=DataCategory.MARKET_PRICE,
                timestamp=timestamp,
                value=value,
                unit="USD/tonne",
                crop="maize",
                location="Mbare"
            )
    print("✓ Added 60 price data points\n")
    
    # Add rainfall data
    print("3. Adding rainfall data...")
    for year in range(2019, 2024):
        for month in range(1, 13):
            timestamp = f"{year}-{month:02d}-01T12:00:00"
            # Simulate rainfall pattern (rainy season Nov-Mar)
            if month in [11, 12, 1, 2, 3]:
                rainfall = 100 + (month % 3) * 30
            else:
                rainfall = 10 + month * 2
            
            # Add anomaly in 2021
            if year == 2021 and month == 1:
                rainfall = 20  # Drought
            
            archive.add_data_point(
                category=DataCategory.RAINFALL,
                timestamp=timestamp,
                value=rainfall,
                unit="mm",
                location="Harare"
            )
    print("✓ Added 60 rainfall data points\n")
    
    # Analyze trend
    print("4. Analyzing crop yield trend...")
    trend = archive.analyze_trend(
        category=DataCategory.CROP_YIELD,
        crop="maize",
        location="Harare"
    )
    if trend:
        print(f"   Direction: {trend.trend_direction}")
        print(f"   Strength: {trend.trend_strength:.2f}")
        print(f"   Average: {trend.average:.2f} tonnes/ha")
        print(f"   Growth Rate: {trend.growth_rate:.1f}%\n")
    
    # Year-over-year comparison
    print("5. Year-over-year comparison (2022 vs 2023)...")
    yoy = archive.compare_year_over_year(
        category=DataCategory.CROP_YIELD,
        year1=2022,
        year2=2023,
        crop="maize",
        location="Harare"
    )
    if yoy:
        print(f"   2022: {yoy.value1:.2f} tonnes/ha")
        print(f"   2023: {yoy.value2:.2f} tonnes/ha")
        print(f"   Change: {yoy.change_percentage:+.1f}% ({yoy.direction})\n")
    
    # Detect anomalies in rainfall
    print("6. Detecting rainfall anomalies...")
    anomalies = archive.detect_anomalies(
        category=DataCategory.RAINFALL,
        location="Harare",
        threshold_stdev=2.0
    )
    print(f"   Found {len(anomalies)} anomalies")
    for anom in anomalies[:3]:  # Show first 3
        print(f"   - {anom.timestamp[:7]}: {anom.value:.1f}mm (severity: {anom.severity})")
    print()
    
    # Seasonal pattern
    print("7. Analyzing seasonal pattern (market prices)...")
    seasonal = archive.get_seasonal_pattern(
        category=DataCategory.MARKET_PRICE,
        crop="maize",
        location="Mbare",
        years=5
    )
    print("   Average prices by month:")
    for month, price in sorted(seasonal.items())[:6]:
        print(f"   Month {month}: ${price:.0f}/tonne")
    print()
    
    # Statistics
    print("=== ARCHIVE STATISTICS ===")
    stats = archive.get_statistics()
    print(f"Total time series: {stats['total_time_series']}")
    print(f"Total data points: {stats['total_data_points']}")
    print(f"By category: {stats['by_category']}")
    print(f"Date range: {stats['oldest_data'][:10]} to {stats['newest_data'][:10]}")
