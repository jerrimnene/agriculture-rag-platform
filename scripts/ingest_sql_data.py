#!/usr/bin/env python3
"""
Ingest Zimbabwe agricultural zones SQL data.
Creates embeddings from the SQL district data for RAG retrieval.
"""

import sys
import json
from pathlib import Path
import yaml
import logging
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore
from src.ingestion.document_processor import Document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_sql_to_documents(sql_file_path: str) -> list[Document]:
    """Parse SQL file and convert to Document objects."""
    documents = []
    
    logger.info(f"Reading SQL file: {sql_file_path}")
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Extract natural regions data
    natural_regions_pattern = r"INSERT INTO natural_regions VALUES\s*\((.*?)\);"
    natural_regions_matches = re.finditer(natural_regions_pattern, sql_content, re.DOTALL)
    
    for match in natural_regions_matches:
        values = match.group(1)
        # Parse the values (simplified - would need more robust parsing for production)
        parts = [p.strip().strip("'") for p in values.split("',")]
        
        if len(parts) >= 6:
            region_id = parts[0].strip("'")
            region_name = parts[1]
            description = parts[2] if len(parts) > 2 else ""
            
            region_text = f"""
            Natural Region: {region_name}
            Region ID: {region_id}
            Description: {description}
            
            This is a Zimbabwe agricultural natural region classification used for farming recommendations.
            """
            
            documents.append(Document(
                content=region_text.strip(),
                metadata={
                    'source': 'zimbabwe_agricultural_zones',
                    'type': 'natural_region_sql',
                    'category': 'regional_data',
                    'region_id': region_id
                },
                doc_id=f'sql_natural_region_{region_id}',
                chunk_id=0
            ))
    
    # Extract district data
    district_pattern = r"INSERT INTO districts \([^)]+\) VALUES\s*\((.*?)\);"
    district_matches = re.finditer(district_pattern, sql_content, re.DOTALL)
    
    for idx, match in enumerate(district_matches):
        values = match.group(1)
        # Split by comma but preserve arrays
        parts = []
        current = []
        in_array = False
        
        for char in values:
            if char == '[':
                in_array = True
                current.append(char)
            elif char == ']':
                in_array = False
                current.append(char)
            elif char == ',' and not in_array:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        # Clean up parts
        parts = [p.strip().strip("'") for p in parts]
        
        if len(parts) >= 6:
            province = parts[0].strip("'")
            district = parts[1].strip("'")
            natural_region = parts[2].strip("'")
            
            # Extract arrays (simplified)
            main_crops = []
            main_livestock = []
            markets = []
            
            for part in parts:
                if 'ARRAY[' in part:
                    # Extract array values
                    array_match = re.search(r"ARRAY\[(.*?)\]", part)
                    if array_match:
                        array_values = [v.strip().strip("'") for v in array_match.group(1).split(',')]
                        if 'maize' in part.lower() or 'tobacco' in part.lower():
                            main_crops = array_values
                        elif 'cattle' in part.lower() or 'goat' in part.lower():
                            main_livestock = array_values
                        elif 'market' in part.lower():
                            markets = array_values
            
            district_text = f"""
            District: {district}, {province} Province
            Natural Region: {natural_region}
            Main Crops: {', '.join(main_crops)}
            Main Livestock: {', '.join(main_livestock)}
            Nearest Markets: {', '.join(markets)}
            
            This district is located in {province} province and falls within Natural Region {natural_region} 
            of Zimbabwe's agricultural classification system.
            """
            
            documents.append(Document(
                content=district_text.strip(),
                metadata={
                    'source': 'zimbabwe_agricultural_zones',
                    'type': 'district_sql',
                    'category': 'regional_data',
                    'province': province,
                    'district': district,
                    'natural_region': natural_region
                },
                doc_id=f'sql_district_{idx}',
                chunk_id=0
            ))
    
    logger.info(f"Created {len(documents)} document chunks from SQL data")
    return documents


def main():
    """Main ingestion process."""
    logger.info("=" * 60)
    logger.info("Zimbabwe Agricultural Zones SQL Data Ingestion")
    logger.info("=" * 60)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Path to SQL file
    sql_file = Path(__file__).parent.parent / "data" / "raw" / "zimbabwe_agricultural_zones.sql"
    
    if not sql_file.exists():
        logger.error(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)
    
    # Parse SQL to documents
    logger.info("\n📄 Step 1: Parsing SQL file...")
    documents = parse_sql_to_documents(str(sql_file))
    
    if not documents:
        logger.warning("⚠️  No documents created from SQL file")
        return
    
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
    logger.info("SQL Data Ingestion Complete!")
    logger.info("=" * 60)
    logger.info(f"Total documents in DB: {stats['total_documents']}")
    logger.info(f"New documents added: {len(documents)}")
    logger.info("=" * 60)
    
    # Test query
    logger.info("\n🧪 Testing with sample queries...")
    
    test_queries = [
        "districts in Mashonaland Central",
        "Natural Region IV characteristics",
        "Bindura district information"
    ]
    
    for query in test_queries:
        results = vector_store.search(query, top_k=2)
        if results:
            logger.info(f"\n✓ Query: '{query}'")
            logger.info(f"  Top result: {results[0]['metadata'].get('type', 'Unknown')}")
        else:
            logger.warning(f"⚠️  No results for query: '{query}'")
    
    logger.info("\n🎉 SQL data successfully ingested into RAG system!")


if __name__ == "__main__":
    main()
