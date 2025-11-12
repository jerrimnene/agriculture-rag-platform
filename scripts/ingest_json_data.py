#!/usr/bin/env python3
"""
Ingest Zimbabwe regional agriculture JSON data into vector database.
Processes the JSON and creates embeddings for RAG retrieval.
"""

import sys
import json
from pathlib import Path
import yaml
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore
from src.ingestion.document_processor import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def json_to_documents(json_file_path: str) -> list[Document]:
    """Convert JSON data to Document objects for vector store."""
    documents = []
    
    logger.info(f"Loading JSON data from {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process metadata
    metadata_section = data.get('metadata', {})
    metadata_text = f"Zimbabwe Agricultural Data - {metadata_section.get('description', '')}"
    documents.append(Document(
        content=metadata_text,
        metadata={
            'source': 'zimbabwe_regional_agriculture',
            'type': 'metadata',
            'category': 'regional_data',
            'country': 'Zimbabwe'
        },
        doc_id='zw_agric_metadata',
        chunk_id=0
    ))
    
    # Process each province
    for province_data in data.get('provinces', []):
        province_name = province_data.get('name', '')
        province_id = province_data.get('province_id', '')
        
        # Provincial overview
        overview_text = f"""
        Province: {province_name}
        Population: {province_data.get('population', 'N/A'):,}
        Area: {province_data.get('area_km2', 'N/A'):,} km²
        Natural Regions: {', '.join(province_data.get('dominant_natural_regions', []))}
        Rainfall Range: {province_data.get('rainfall_range_mm', [None, None])[0]}-{province_data.get('rainfall_range_mm', [None, None])[1]} mm
        Growing Season: {province_data.get('growing_season', 'N/A')}
        Main Activity: {province_data.get('main_agricultural_activity', 'N/A')}
        """
        
        documents.append(Document(
            content=overview_text.strip(),
            metadata={
                'source': 'zimbabwe_regional_agriculture',
                'type': 'province_overview',
                'category': 'regional_data',
                'province': province_name,
                'province_id': province_id,
                'natural_regions': ','.join(province_data.get('dominant_natural_regions', []))
            },
            doc_id=f'province_{province_id}',
            chunk_id=0
        ))
        
        # Process crops for this province
        crops = province_data.get('crops', {})
        for crop_name, crop_data in crops.items():
            crop_text = f"""
            {crop_name.upper()} in {province_name}:
            - Area Planted: {crop_data.get('area_planted_ha', 'N/A'):,} hectares
            - Production: {crop_data.get('production_tonnes', 'N/A'):,} tonnes
            - Average Yield: {crop_data.get('yield_avg_t_ha', 'N/A')} tonnes/hectare
            - Natural Regions: {', '.join(crop_data.get('natural_regions', []))}
            - Main Varieties: {', '.join(crop_data.get('main_varieties', []))}
            - Planting Window: {crop_data.get('planting_window', 'N/A')}
            - Fertilizer (Basal): {crop_data.get('fertilizer_recommendation', {}).get('basal', 'N/A')}
            - Fertilizer (Topdress): {crop_data.get('fertilizer_recommendation', {}).get('topdress', 'N/A')}
            - Irrigation Required: {crop_data.get('irrigation_required', False)}
            - Input Cost: ${crop_data.get('input_cost_per_ha_usd', 'N/A')}/ha
            - Market Price: ${crop_data.get('market_price_per_tonne_usd', 'N/A')}/tonne
            - Gross Margin: ${crop_data.get('gross_margin_per_ha_usd', 'N/A')}/ha
            - Main Constraints: {', '.join(crop_data.get('main_constraints', []))}
            - Suitable Districts: {', '.join(crop_data.get('suitable_districts', []))}
            """
            
            documents.append(Document(
                content=crop_text.strip(),
                metadata={
                    'source': 'zimbabwe_regional_agriculture',
                    'type': 'crop_data',
                    'category': 'crop',
                    'province': province_name,
                    'province_id': province_id,
                    'crop': crop_name,
                    'natural_regions': ','.join(crop_data.get('natural_regions', []))
                },
                doc_id=f'province_{province_id}_crop_{crop_name}',
                chunk_id=0
            ))
        
        # Process livestock for this province
        livestock = province_data.get('livestock', {})
        for livestock_type, livestock_data in livestock.items():
            livestock_text = f"""
            {livestock_type.upper()} in {province_name}:
            - Population: {livestock_data.get('population', 'N/A'):,} head
            - Breeds: {', '.join(livestock_data.get('breeds', []))}
            - Production System: {livestock_data.get('production_system', 'N/A')}
            - Average Herd Size: {livestock_data.get('avg_herd_size', 'N/A')}
            - Milk Production: {livestock_data.get('milk_production_litres_per_cow_per_year', 'N/A')} litres/cow/year
            - Beef Price: ${livestock_data.get('beef_price_per_kg_usd', 'N/A')}/kg
            - Milk Price: ${livestock_data.get('milk_price_per_litre_usd', 'N/A')}/litre
            - Meat Price: ${livestock_data.get('meat_price_per_kg_usd', 'N/A')}/kg
            - Main Diseases: {', '.join(livestock_data.get('main_diseases', []))}
            - Veterinary Services: {livestock_data.get('veterinary_services', 'N/A')}
            - Feed Cost: ${livestock_data.get('feed_cost_per_animal_per_year_usd', 'N/A')}/animal/year
            - Kidding Rate: {livestock_data.get('kidding_rate_percent', 'N/A')}%
            - Mortality Rate: {livestock_data.get('mortality_rate_percent', 'N/A')}%
            - Main Constraints: {', '.join(livestock_data.get('main_constraints', []))}
            - Market Access: {livestock_data.get('market_access', 'N/A')}
            """
            
            documents.append(Document(
                content=livestock_text.strip(),
                metadata={
                    'source': 'zimbabwe_regional_agriculture',
                    'type': 'livestock_data',
                    'category': 'livestock',
                    'province': province_name,
                    'province_id': province_id,
                    'livestock_type': livestock_type
                },
                doc_id=f'province_{province_id}_livestock_{livestock_type}',
                chunk_id=0
            ))
    
    # Process natural region profiles
    natural_regions = data.get('natural_region_profiles', {})
    for region_id, region_data in natural_regions.items():
        region_text = f"""
        {region_data.get('name', region_id)}:
        Rainfall: {region_data.get('rainfall_mm', 'N/A')} mm
        Description: {region_data.get('description', 'N/A')}
        Suitable Crops: {', '.join(region_data.get('suitable_crops', []))}
        Livestock Suitability: {region_data.get('livestock_suitability', 'N/A')}
        Risk Level: {region_data.get('risk_level', 'N/A')}
        Provinces: {', '.join(region_data.get('provinces', []))}
        """
        
        documents.append(Document(
            content=region_text.strip(),
            metadata={
                'source': 'zimbabwe_regional_agriculture',
                'type': 'natural_region',
                'category': 'regional_data',
                'region_id': region_id,
                'risk_level': region_data.get('risk_level', 'N/A')
            },
            doc_id=f'natural_region_{region_id}',
            chunk_id=0
        ))
    
    # Process recommendations
    recommendations = data.get('recommendations', {})
    for crop_livestock, rec_data in recommendations.items():
        for region_type, details in rec_data.items():
            if isinstance(details, dict):
                rec_text = f"""
                Recommendations for {crop_livestock.upper()} - {region_type}:
                {json.dumps(details, indent=2)}
                """
                
                documents.append(Document(
                    content=rec_text.strip(),
                    metadata={
                        'source': 'zimbabwe_regional_agriculture',
                        'type': 'recommendation',
                        'category': 'general',
                        'crop_livestock': crop_livestock,
                        'region_type': region_type
                    },
                    doc_id=f'recommendation_{crop_livestock}_{region_type}',
                    chunk_id=0
                ))
    
    logger.info(f"Created {len(documents)} document chunks from JSON data")
    return documents


def main():
    """Main ingestion process."""
    logger.info("=" * 60)
    logger.info("Zimbabwe Regional Agriculture Data Ingestion")
    logger.info("=" * 60)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Path to JSON file
    json_file = Path(__file__).parent.parent / "data" / "raw" / "zimbabwe_regional_agriculture.json"
    
    if not json_file.exists():
        logger.error(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    # Convert JSON to documents
    logger.info("\n📄 Step 1: Converting JSON to documents...")
    documents = json_to_documents(str(json_file))
    
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
    
    # Test query
    logger.info("\n🧪 Testing with sample queries...")
    
    test_queries = [
        "maize production in Mashonaland East",
        "cattle farming in Matabeleland",
        "Natural Region II characteristics"
    ]
    
    for query in test_queries:
        results = vector_store.search(query, top_k=2)
        if results:
            logger.info(f"\n✓ Query: '{query}'")
            logger.info(f"  Top result: {results[0]['metadata'].get('type', 'Unknown')}")
        else:
            logger.warning(f"⚠️  No results for query: '{query}'")
    
    logger.info("\n🎉 JSON data successfully ingested into RAG system!")


if __name__ == "__main__":
    main()
