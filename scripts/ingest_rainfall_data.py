#!/usr/bin/env python3
"""
Ingest Zimbabwe rainfall timeseries data from CSV into vector database.
Processes district-level rainfall data from 1981-2025 for RAG retrieval.
"""

import sys
import csv
import statistics
from pathlib import Path
import yaml
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore
from src.ingestion.document_processor import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_rainfall_trends(rainfall_values: List[float]) -> Dict:
    """Analyze rainfall data to extract trends and patterns."""
    if not rainfall_values or len(rainfall_values) == 0:
        return {}
    
    # Remove None values
    valid_values = [v for v in rainfall_values if v is not None]
    
    if not valid_values:
        return {}
    
    return {
        'mean': round(statistics.mean(valid_values), 2),
        'median': round(statistics.median(valid_values), 2),
        'std_dev': round(statistics.stdev(valid_values), 2) if len(valid_values) > 1 else 0,
        'min': round(min(valid_values), 2),
        'max': round(max(valid_values), 2),
        'recent_5yr_avg': round(statistics.mean(valid_values[-5:]), 2) if len(valid_values) >= 5 else None,
        'recent_10yr_avg': round(statistics.mean(valid_values[-10:]), 2) if len(valid_values) >= 10 else None,
    }


def classify_rainfall_pattern(stats: Dict) -> str:
    """Classify rainfall pattern based on statistics."""
    if not stats or 'mean' not in stats:
        return "Unknown"
    
    mean = stats['mean']
    std_dev = stats.get('std_dev', 0)
    
    # Coefficient of variation
    cv = (std_dev / mean * 100) if mean > 0 else 0
    
    if cv > 30:
        reliability = "Highly Variable"
    elif cv > 20:
        reliability = "Moderately Variable"
    else:
        reliability = "Relatively Stable"
    
    if mean >= 3:
        category = "High Rainfall"
    elif mean >= 2:
        category = "Moderate-High Rainfall"
    elif mean >= 1.5:
        category = "Moderate Rainfall"
    elif mean >= 1:
        category = "Low-Moderate Rainfall"
    else:
        category = "Low Rainfall"
    
    return f"{category}, {reliability}"


def csv_to_documents(csv_file_path: str) -> List[Document]:
    """Convert rainfall CSV data to Document objects for vector store."""
    documents = []
    
    logger.info(f"Loading rainfall data from {csv_file_path}")
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    logger.info(f"Processing {len(rows)} district records")
    
    # Create overview document
    overview_text = f"""
    Zimbabwe Rainfall Time Series Data (1981-2025)
    
    This dataset contains annual average rainfall data (in meters) for {len(rows)} districts across Zimbabwe's provinces.
    Data is derived from CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data) satellite rainfall estimates.
    
    Coverage: 45 years of historical rainfall data (1981-2025)
    Spatial Resolution: District level across all provinces
    
    This data is critical for:
    - Climate risk assessment and drought monitoring
    - Agricultural planning and crop selection
    - Irrigation requirement calculation
    - Historical climate pattern analysis
    - Climate change impact studies
    """
    
    documents.append(Document(
        content=overview_text.strip(),
        metadata={
            'source': 'chirps_rainfall_timeseries',
            'type': 'dataset_overview',
            'category': 'climate',
            'country': 'Zimbabwe',
            'years': '1981-2025',
            'data_source': 'CHIRPS'
        },
        doc_id='zw_rainfall_overview',
        chunk_id=0
    ))
    
    # Process each district
    for idx, row in enumerate(rows):
        province = row['Province']
        district = row['District']
        
        # Extract rainfall values (convert from string to float, handling empty values)
        rainfall_years = []
        rainfall_values = []
        
        for year in range(1981, 2026):
            col_name = f'rain_{year}'
            if col_name in row and row[col_name]:
                try:
                    value = float(row[col_name])
                    rainfall_years.append(year)
                    rainfall_values.append(value)
                except ValueError:
                    pass
        
        if not rainfall_values:
            logger.warning(f"No valid rainfall data for {district}, {province}")
            continue
        
        # Analyze the data
        stats = analyze_rainfall_trends(rainfall_values)
        pattern = classify_rainfall_pattern(stats)
        
        # Create detailed district document
        district_text = f"""
        RAINFALL PROFILE: {district} District, {province} Province
        
        Historical Rainfall Statistics (1981-2025):
        - Average Annual Rainfall: {stats.get('mean', 'N/A')} meters ({stats.get('mean', 0) * 1000:.0f} mm)
        - Median Rainfall: {stats.get('median', 'N/A')} meters
        - Rainfall Range: {stats.get('min', 'N/A')} - {stats.get('max', 'N/A')} meters
        - Standard Deviation: {stats.get('std_dev', 'N/A')} meters
        - Recent 5-year Average (2021-2025): {stats.get('recent_5yr_avg', 'N/A')} meters
        - Recent 10-year Average (2016-2025): {stats.get('recent_10yr_avg', 'N/A')} meters
        
        Rainfall Pattern: {pattern}
        
        Years of Data Available: {len(rainfall_values)} years ({min(rainfall_years)}-{max(rainfall_years)})
        
        Agricultural Implications:
        - Suitable for {"drought-resistant crops" if stats.get('mean', 0) < 1.5 else "moderate water requirement crops" if stats.get('mean', 0) < 2.5 else "water-intensive crops"}
        - {"Irrigation highly recommended" if stats.get('mean', 0) < 1.5 else "Supplementary irrigation may be needed" if stats.get('mean', 0) < 2 else "Rainfed agriculture viable"}
        - Climate Risk: {"High" if stats.get('std_dev', 0) / stats.get('mean', 1) > 0.3 else "Moderate" if stats.get('std_dev', 0) / stats.get('mean', 1) > 0.2 else "Low"} variability
        
        Recent Trends (Last 10 Years):
        {"Declining rainfall trend" if stats.get('recent_10yr_avg', 0) < stats.get('mean', 0) * 0.95 else "Stable rainfall pattern" if stats.get('recent_10yr_avg', 0) < stats.get('mean', 0) * 1.05 else "Increasing rainfall trend"}
        """
        
        documents.append(Document(
            content=district_text.strip(),
            metadata={
                'source': 'chirps_rainfall_timeseries',
                'type': 'district_rainfall',
                'category': 'climate',
                'province': province,
                'district': district,
                'mean_rainfall_m': stats.get('mean'),
                'mean_rainfall_mm': round(stats.get('mean', 0) * 1000, 0),
                'rainfall_variability': stats.get('std_dev'),
                'data_years': len(rainfall_values),
                'rainfall_pattern': pattern
            },
            doc_id=f'rainfall_{province}_{district}'.replace(' ', '_').lower(),
            chunk_id=0
        ))
        
        # Create decade summary documents for more granular retrieval
        decades = [
            (1981, 1990, '1980s'),
            (1991, 2000, '1990s'),
            (2001, 2010, '2000s'),
            (2011, 2020, '2010s'),
            (2021, 2025, '2020s')
        ]
        
        for start_year, end_year, decade_name in decades:
            decade_values = [
                rainfall_values[i] for i, year in enumerate(rainfall_years)
                if start_year <= year <= end_year
            ]
            
            if decade_values:
                decade_stats = analyze_rainfall_trends(decade_values)
                
                decade_text = f"""
                {district} District, {province} - {decade_name} Rainfall Summary
                
                Decade: {start_year}-{end_year}
                Average: {decade_stats.get('mean', 'N/A')} meters ({decade_stats.get('mean', 0) * 1000:.0f} mm)
                Range: {decade_stats.get('min', 'N/A')} - {decade_stats.get('max', 'N/A')} meters
                Pattern: {classify_rainfall_pattern(decade_stats)}
                
                This decade had {"above average" if decade_stats.get('mean', 0) > stats.get('mean', 0) else "below average" if decade_stats.get('mean', 0) < stats.get('mean', 0) else "average"} rainfall compared to the 45-year mean.
                """
                
                documents.append(Document(
                    content=decade_text.strip(),
                    metadata={
                        'source': 'chirps_rainfall_timeseries',
                        'type': 'decade_rainfall',
                        'category': 'climate',
                        'province': province,
                        'district': district,
                        'decade': decade_name,
                        'start_year': start_year,
                        'end_year': end_year,
                        'mean_rainfall_m': decade_stats.get('mean')
                    },
                    doc_id=f'rainfall_{province}_{district}_{decade_name}'.replace(' ', '_').lower(),
                    chunk_id=0
                ))
    
    # Create province summaries
    provinces = {}
    for row in rows:
        province = row['Province']
        if province not in provinces:
            provinces[province] = []
        
        # Get mean rainfall for this district
        rainfall_values = []
        for year in range(1981, 2026):
            col_name = f'rain_{year}'
            if col_name in row and row[col_name]:
                try:
                    rainfall_values.append(float(row[col_name]))
                except ValueError:
                    pass
        
        if rainfall_values:
            stats = analyze_rainfall_trends(rainfall_values)
            provinces[province].append({
                'district': row['District'],
                'mean': stats.get('mean', 0),
                'std_dev': stats.get('std_dev', 0)
            })
    
    # Create province summary documents
    for province, districts_data in provinces.items():
        if not districts_data:
            continue
        
        province_means = [d['mean'] for d in districts_data]
        province_stats = {
            'mean': round(statistics.mean(province_means), 2),
            'min': round(min(province_means), 2),
            'max': round(max(province_means), 2),
            'std_dev': round(statistics.stdev(province_means), 2) if len(province_means) > 1 else 0
        }
        
        districts_list = ', '.join([d['district'] for d in districts_data])
        
        province_text = f"""
        {province} Province - Rainfall Overview (1981-2025)
        
        Provincial Statistics:
        - Number of Districts: {len(districts_data)}
        - Average Rainfall Across Province: {province_stats['mean']} meters ({province_stats['mean'] * 1000:.0f} mm)
        - Rainfall Range: {province_stats['min']} - {province_stats['max']} meters
        - Districts: {districts_list}
        
        Spatial Variability: {classify_rainfall_pattern(province_stats)}
        
        The province shows {"high" if province_stats['std_dev'] > 0.5 else "moderate" if province_stats['std_dev'] > 0.3 else "low"} spatial variability in rainfall across districts.
        """
        
        documents.append(Document(
            content=province_text.strip(),
            metadata={
                'source': 'chirps_rainfall_timeseries',
                'type': 'province_rainfall_summary',
                'category': 'climate',
                'province': province,
                'num_districts': len(districts_data),
                'mean_rainfall_m': province_stats['mean'],
                'mean_rainfall_mm': round(province_stats['mean'] * 1000, 0)
            },
            doc_id=f'rainfall_province_{province}'.replace(' ', '_').lower(),
            chunk_id=0
        ))
    
    logger.info(f"Created {len(documents)} document chunks from rainfall data")
    return documents


def main():
    """Main ingestion process."""
    logger.info("=" * 60)
    logger.info("Zimbabwe Rainfall Timeseries Data Ingestion")
    logger.info("=" * 60)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Path to CSV file
    csv_file = Path("/Users/providencemtendereki/Downloads/chirps_africa_zim/zim_rainfall_timeseries_1981_2025.csv")
    
    if not csv_file.exists():
        logger.error(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Convert CSV to documents
    logger.info("\n📄 Step 1: Converting CSV to documents...")
    documents = csv_to_documents(str(csv_file))
    
    # Initialize vector store
    logger.info("\n🔍 Step 2: Initializing vector store...")
    vector_db_path = Path(__file__).parent.parent / "data" / "vector_db"
    
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    # Add documents to vector store
    logger.info("\n💾 Step 3: Adding documents to vector database...")
    vector_store.add_documents(
        documents,
        batch_size=config['embeddings']['batch_size']
    )
    
    # Verify
    logger.info("\n✅ Step 4: Verification...")
    stats = vector_store.get_stats()
    
    logger.info("=" * 60)
    logger.info("Data Ingestion Complete!")
    logger.info("=" * 60)
    logger.info(f"Total documents in DB: {stats['total_documents']}")
    logger.info(f"New documents added: {len(documents)}")
    logger.info("=" * 60)
    
    # Test queries
    logger.info("\n🧪 Testing with sample queries...")
    
    test_queries = [
        "What is the rainfall pattern in Masvingo district?",
        "Historical rainfall data for Harare",
        "Which districts in Matabeleland have low rainfall?",
        "Rainfall trends in the 2010s decade"
    ]
    
    for query in test_queries:
        results = vector_store.search(query, top_k=2)
        if results:
            logger.info(f"\n✓ Query: '{query}'")
            logger.info(f"  Top result: {results[0]['metadata'].get('district', 'N/A')} - {results[0]['metadata'].get('type', 'Unknown')}")
        else:
            logger.warning(f"⚠️  No results for query: '{query}'")
    
    logger.info("\n🎉 Rainfall data successfully ingested into RAG system!")
    logger.info("\nNext steps:")
    logger.info("1. Query the system about district rainfall patterns")
    logger.info("2. Get climate risk assessments for different regions")
    logger.info("3. Compare historical trends across provinces")
    logger.info("4. Make informed crop selection based on rainfall data")


if __name__ == "__main__":
    main()
