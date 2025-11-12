"""
External Data Sync Module
Synchronizes data from Zimbabwean agricultural authorities and institutions
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class DataSource(Enum):
    """Supported external data sources."""
    AGRITEX = "agritex"
    AMA = "ama"  # Agricultural Marketing Authority
    ZMX = "zmx"  # Zimbabwe Stock Exchange (Commodity prices)
    TIMB = "timb"  # Tobacco Industry Marketing Board
    GMB = "gmb"  # Grain Marketing Board


@dataclass
class SyncRecord:
    """Record of a sync operation."""
    source: str
    timestamp: str
    status: str
    records_fetched: int
    records_updated: int
    records_new: int
    errors: List[str]
    duration_seconds: float
    next_sync: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DataEntry:
    """Standardized data entry from external source."""
    source: str
    data_type: str  # price, yield, weather, policy, advisory
    content: Dict[str, Any]
    timestamp: str
    location: Optional[str] = None
    crop: Optional[str] = None
    metadata: Optional[Dict] = None
    hash: Optional[str] = None
    
    def __post_init__(self):
        """Generate hash for deduplication."""
        if not self.hash:
            content_str = json.dumps(self.content, sort_keys=True)
            self.hash = hashlib.md5(
                f"{self.source}:{self.data_type}:{content_str}".encode()
            ).hexdigest()
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DataTransformer:
    """Transforms external data into standardized format."""
    
    @staticmethod
    def transform_agritex(raw_data: Dict) -> List[DataEntry]:
        """Transform AGRITEX extension advisory data."""
        entries = []
        
        # Transform advisories
        if 'advisories' in raw_data:
            for advisory in raw_data['advisories']:
                entry = DataEntry(
                    source='AGRITEX',
                    data_type='advisory',
                    content={
                        'title': advisory.get('title', ''),
                        'description': advisory.get('description', ''),
                        'recommendations': advisory.get('recommendations', []),
                        'target_crops': advisory.get('crops', []),
                        'natural_regions': advisory.get('regions', [])
                    },
                    timestamp=advisory.get('date', datetime.now().isoformat()),
                    location=advisory.get('district'),
                    crop=advisory.get('crops', [None])[0] if advisory.get('crops') else None,
                    metadata={'advisory_id': advisory.get('id'), 'priority': advisory.get('priority')}
                )
                entries.append(entry)
        
        return entries
    
    @staticmethod
    def transform_ama(raw_data: Dict) -> List[DataEntry]:
        """Transform AMA market price data."""
        entries = []
        
        # Transform market prices
        if 'prices' in raw_data:
            for price_data in raw_data['prices']:
                entry = DataEntry(
                    source='AMA',
                    data_type='price',
                    content={
                        'commodity': price_data.get('commodity'),
                        'price_per_unit': price_data.get('price'),
                        'unit': price_data.get('unit', 'kg'),
                        'currency': price_data.get('currency', 'USD'),
                        'market_name': price_data.get('market'),
                        'price_trend': price_data.get('trend', 'stable')
                    },
                    timestamp=price_data.get('date', datetime.now().isoformat()),
                    location=price_data.get('market'),
                    crop=price_data.get('commodity'),
                    metadata={'market_type': price_data.get('market_type'), 'volume': price_data.get('volume')}
                )
                entries.append(entry)
        
        return entries
    
    @staticmethod
    def transform_zmx(raw_data: Dict) -> List[DataEntry]:
        """Transform ZMX commodity trading data."""
        entries = []
        
        # Transform commodity quotes
        if 'commodities' in raw_data:
            for commodity in raw_data['commodities']:
                entry = DataEntry(
                    source='ZMX',
                    data_type='price',
                    content={
                        'commodity': commodity.get('name'),
                        'price_per_unit': commodity.get('last_price'),
                        'unit': commodity.get('unit', 'tonne'),
                        'currency': 'USD',
                        'open_price': commodity.get('open'),
                        'high_price': commodity.get('high'),
                        'low_price': commodity.get('low'),
                        'volume': commodity.get('volume')
                    },
                    timestamp=commodity.get('timestamp', datetime.now().isoformat()),
                    crop=commodity.get('name'),
                    metadata={'exchange': 'ZMX', 'ticker': commodity.get('ticker')}
                )
                entries.append(entry)
        
        return entries
    
    @staticmethod
    def transform_timb(raw_data: Dict) -> List[DataEntry]:
        """Transform TIMB tobacco data."""
        entries = []
        
        # Transform tobacco sales data
        if 'sales' in raw_data:
            for sale in raw_data['sales']:
                entry = DataEntry(
                    source='TIMB',
                    data_type='price',
                    content={
                        'commodity': 'tobacco',
                        'grade': sale.get('grade'),
                        'price_per_unit': sale.get('avg_price'),
                        'unit': 'kg',
                        'currency': 'USD',
                        'total_volume': sale.get('volume_kg'),
                        'total_value': sale.get('total_value')
                    },
                    timestamp=sale.get('sale_date', datetime.now().isoformat()),
                    location=sale.get('selling_floor'),
                    crop='tobacco',
                    metadata={'season': sale.get('season'), 'grade': sale.get('grade')}
                )
                entries.append(entry)
        
        return entries
    
    @staticmethod
    def transform_gmb(raw_data: Dict) -> List[DataEntry]:
        """Transform GMB grain data."""
        entries = []
        
        # Transform grain procurement data
        if 'procurement' in raw_data:
            for record in raw_data['procurement']:
                entry = DataEntry(
                    source='GMB',
                    data_type='price',
                    content={
                        'commodity': record.get('grain_type'),
                        'price_per_unit': record.get('producer_price'),
                        'unit': 'kg',
                        'currency': 'USD',
                        'depot_location': record.get('depot'),
                        'grade': record.get('grade'),
                        'moisture_content': record.get('moisture_pct')
                    },
                    timestamp=record.get('date', datetime.now().isoformat()),
                    location=record.get('depot'),
                    crop=record.get('grain_type'),
                    metadata={'season': record.get('season'), 'payment_terms': record.get('payment_terms')}
                )
                entries.append(entry)
        
        return entries


class ConflictResolver:
    """Resolves conflicts between external data and existing data."""
    
    @staticmethod
    def resolve(existing: DataEntry, new: DataEntry, strategy: str = "newest") -> DataEntry:
        """
        Resolve conflict between existing and new data.
        
        Strategies:
        - newest: Use most recent data
        - highest_authority: Use data from most authoritative source
        - merge: Merge both entries
        """
        if strategy == "newest":
            existing_time = datetime.fromisoformat(existing.timestamp)
            new_time = datetime.fromisoformat(new.timestamp)
            return new if new_time > existing_time else existing
        
        elif strategy == "highest_authority":
            authority_order = ['AGRITEX', 'GMB', 'TIMB', 'AMA', 'ZMX']
            existing_priority = authority_order.index(existing.source) if existing.source in authority_order else 99
            new_priority = authority_order.index(new.source) if new.source in authority_order else 99
            return new if new_priority < existing_priority else existing
        
        elif strategy == "merge":
            # Merge metadata and content
            merged_content = {**existing.content, **new.content}
            merged_metadata = {**(existing.metadata or {}), **(new.metadata or {})}
            
            return DataEntry(
                source=f"{existing.source}+{new.source}",
                data_type=new.data_type,
                content=merged_content,
                timestamp=max(existing.timestamp, new.timestamp),
                location=new.location or existing.location,
                crop=new.crop or existing.crop,
                metadata=merged_metadata
            )
        
        return new


class ExternalDataSync:
    """Main external data synchronization manager."""
    
    def __init__(self, storage_path: str = "./data/external_sync"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.sync_log_path = self.storage_path / "sync_log.json"
        self.data_store_path = self.storage_path / "synced_data.json"
        self.config_path = self.storage_path / "sync_config.json"
        
        self.transformer = DataTransformer()
        self.resolver = ConflictResolver()
        
        # Load existing data
        self.synced_data = self._load_synced_data()
        self.sync_log = self._load_sync_log()
        self.config = self._load_config()
        
        logger.info(f"External Data Sync initialized at {self.storage_path}")
    
    def _load_synced_data(self) -> Dict[str, DataEntry]:
        """Load previously synced data."""
        if self.data_store_path.exists():
            with open(self.data_store_path, 'r') as f:
                data = json.load(f)
                return {k: DataEntry(**v) for k, v in data.items()}
        return {}
    
    def _save_synced_data(self):
        """Save synced data to disk."""
        data_dict = {k: v.to_dict() for k, v in self.synced_data.items()}
        with open(self.data_store_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
    
    def _load_sync_log(self) -> List[SyncRecord]:
        """Load sync operation log."""
        if self.sync_log_path.exists():
            with open(self.sync_log_path, 'r') as f:
                data = json.load(f)
                return [SyncRecord(**record) for record in data]
        return []
    
    def _save_sync_log(self):
        """Save sync log to disk."""
        with open(self.sync_log_path, 'w') as f:
            json.dump([r.to_dict() for r in self.sync_log], f, indent=2)
    
    def _load_config(self) -> Dict:
        """Load sync configuration."""
        default_config = {
            'sync_intervals': {
                'agritex': 24,  # hours
                'ama': 24,
                'zmx': 1,  # Real-time during trading hours
                'timb': 24,
                'gmb': 24
            },
            'enabled_sources': ['agritex', 'ama', 'zmx', 'timb', 'gmb'],
            'conflict_resolution_strategy': 'newest',
            'retry_attempts': 3,
            'timeout_seconds': 30
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                loaded = json.load(f)
                return {**default_config, **loaded}
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def sync_source(self, source: DataSource, raw_data: Dict) -> SyncRecord:
        """
        Sync data from a specific source.
        
        Args:
            source: Data source enum
            raw_data: Raw data from the source API
            
        Returns:
            SyncRecord with sync operation details
        """
        start_time = time.time()
        errors = []
        records_fetched = 0
        records_updated = 0
        records_new = 0
        
        logger.info(f"Starting sync for {source.value}")
        
        try:
            # Transform data
            if source == DataSource.AGRITEX:
                entries = self.transformer.transform_agritex(raw_data)
            elif source == DataSource.AMA:
                entries = self.transformer.transform_ama(raw_data)
            elif source == DataSource.ZMX:
                entries = self.transformer.transform_zmx(raw_data)
            elif source == DataSource.TIMB:
                entries = self.transformer.transform_timb(raw_data)
            elif source == DataSource.GMB:
                entries = self.transformer.transform_gmb(raw_data)
            else:
                raise ValueError(f"Unknown source: {source}")
            
            records_fetched = len(entries)
            
            # Process each entry
            for entry in entries:
                if entry.hash in self.synced_data:
                    # Check if update needed
                    existing = self.synced_data[entry.hash]
                    if existing.timestamp != entry.timestamp:
                        # Resolve conflict
                        resolved = self.resolver.resolve(
                            existing, entry, 
                            self.config['conflict_resolution_strategy']
                        )
                        self.synced_data[entry.hash] = resolved
                        records_updated += 1
                else:
                    # New entry
                    self.synced_data[entry.hash] = entry
                    records_new += 1
            
            # Save data
            self._save_synced_data()
            
            duration = time.time() - start_time
            
            # Calculate next sync time
            interval_hours = self.config['sync_intervals'].get(source.value, 24)
            next_sync = (datetime.now() + timedelta(hours=interval_hours)).isoformat()
            
            record = SyncRecord(
                source=source.value,
                timestamp=datetime.now().isoformat(),
                status=SyncStatus.SUCCESS.value,
                records_fetched=records_fetched,
                records_updated=records_updated,
                records_new=records_new,
                errors=errors,
                duration_seconds=round(duration, 2),
                next_sync=next_sync
            )
            
            logger.info(
                f"✓ Sync complete for {source.value}: "
                f"{records_new} new, {records_updated} updated in {duration:.2f}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            errors.append(error_msg)
            logger.error(f"✗ Sync failed for {source.value}: {error_msg}")
            
            record = SyncRecord(
                source=source.value,
                timestamp=datetime.now().isoformat(),
                status=SyncStatus.FAILED.value,
                records_fetched=records_fetched,
                records_updated=records_updated,
                records_new=records_new,
                errors=errors,
                duration_seconds=round(duration, 2)
            )
        
        # Log the sync operation
        self.sync_log.append(record)
        self._save_sync_log()
        
        return record
    
    def sync_all(self, data_by_source: Dict[str, Dict]) -> List[SyncRecord]:
        """
        Sync all enabled sources.
        
        Args:
            data_by_source: Dict mapping source name to raw data
            
        Returns:
            List of sync records
        """
        records = []
        
        for source_name, raw_data in data_by_source.items():
            if source_name not in self.config['enabled_sources']:
                logger.info(f"Skipping disabled source: {source_name}")
                continue
            
            try:
                source = DataSource(source_name)
                record = self.sync_source(source, raw_data)
                records.append(record)
            except ValueError:
                logger.warning(f"Unknown source: {source_name}")
        
        return records
    
    def get_data_by_type(self, data_type: str) -> List[DataEntry]:
        """Get all synced data of a specific type."""
        return [entry for entry in self.synced_data.values() if entry.data_type == data_type]
    
    def get_data_by_source(self, source: str) -> List[DataEntry]:
        """Get all synced data from a specific source."""
        return [entry for entry in self.synced_data.values() if entry.source == source]
    
    def get_data_by_crop(self, crop: str) -> List[DataEntry]:
        """Get all synced data for a specific crop."""
        return [entry for entry in self.synced_data.values() if entry.crop and crop.lower() in entry.crop.lower()]
    
    def get_sync_status(self) -> Dict:
        """Get current sync status for all sources."""
        status = {}
        
        for source in DataSource:
            recent_syncs = [r for r in self.sync_log if r.source == source.value]
            if recent_syncs:
                last_sync = recent_syncs[-1]
                status[source.value] = {
                    'last_sync': last_sync.timestamp,
                    'status': last_sync.status,
                    'records': last_sync.records_new + last_sync.records_updated,
                    'next_sync': last_sync.next_sync
                }
            else:
                status[source.value] = {
                    'last_sync': None,
                    'status': 'never_synced',
                    'records': 0,
                    'next_sync': None
                }
        
        return status
    
    def get_statistics(self) -> Dict:
        """Get sync statistics."""
        total_records = len(self.synced_data)
        by_source = {}
        by_type = {}
        
        for entry in self.synced_data.values():
            by_source[entry.source] = by_source.get(entry.source, 0) + 1
            by_type[entry.data_type] = by_type.get(entry.data_type, 0) + 1
        
        recent_syncs = self.sync_log[-10:] if len(self.sync_log) > 10 else self.sync_log
        
        return {
            'total_records': total_records,
            'by_source': by_source,
            'by_type': by_type,
            'total_syncs': len(self.sync_log),
            'recent_syncs': [r.to_dict() for r in recent_syncs]
        }


if __name__ == "__main__":
    # Test the sync system with mock data
    sync = ExternalDataSync()
    
    # Mock AGRITEX data
    agritex_data = {
        'advisories': [
            {
                'id': 'ADV001',
                'title': 'Maize Planting Advisory',
                'description': 'Recommended planting window for maize',
                'recommendations': ['Plant after 50mm cumulative rainfall', 'Use certified seed'],
                'crops': ['maize'],
                'regions': ['II', 'III'],
                'district': 'Harare',
                'date': '2024-10-15T10:00:00',
                'priority': 'high'
            }
        ]
    }
    
    # Mock AMA price data
    ama_data = {
        'prices': [
            {
                'commodity': 'maize',
                'price': 350,
                'unit': 'kg',
                'currency': 'USD',
                'market': 'Mbare',
                'date': '2024-10-20T08:00:00',
                'market_type': 'wholesale',
                'volume': 5000,
                'trend': 'rising'
            }
        ]
    }
    
    # Perform sync
    records = sync.sync_all({
        'agritex': agritex_data,
        'ama': ama_data
    })
    
    print("\n=== SYNC RESULTS ===")
    for record in records:
        print(f"\nSource: {record.source}")
        print(f"Status: {record.status}")
        print(f"New: {record.records_new}, Updated: {record.records_updated}")
        print(f"Duration: {record.duration_seconds}s")
    
    print("\n=== STATISTICS ===")
    stats = sync.get_statistics()
    print(f"Total records: {stats['total_records']}")
    print(f"By source: {stats['by_source']}")
    print(f"By type: {stats['by_type']}")
