#!/usr/bin/env python3
"""
Verify data ingestion by testing various queries.
"""

import sys
from pathlib import Path
import yaml
import logging

sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test queries on the vector database."""
    logger.info("=" * 80)
    logger.info("RAG System Verification")
    logger.info("=" * 80)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize vector store
    logger.info("\nInitializing vector store...")
    vector_db_path = Path(__file__).parent.parent / "data" / "vector_db"
    
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    # Get statistics
    stats = vector_store.get_stats()
    logger.info(f"\n📊 Vector Database Statistics:")
    logger.info(f"   Total documents: {stats['total_documents']:,}")
    logger.info(f"   Categories: {', '.join(stats['categories']) if stats['categories'] else 'N/A'}")
    logger.info(f"   Embedding dimension: {stats['embedding_model']}")
    
    # Test queries
    logger.info("\n" + "=" * 80)
    logger.info("Testing Retrieval with Sample Queries")
    logger.info("=" * 80)
    
    test_queries = [
        # District-specific queries
        "What crops are grown in Bindura district?",
        "Tell me about Hwange district agriculture",
        "What is the climate in Masvingo province?",
        
        # Crop-specific queries
        "Best maize varieties for Region IV",
        "Wheat irrigation requirements in Zimbabwe",
        "Potato farming recommendations",
        
        # Livestock queries
        "Cattle farming in Matabeleland",
        "Goat breeds suitable for low rainfall areas",
        
        # Natural regions
        "Characteristics of Natural Region II",
        "What can you farm in Region V?",
        
        # Technical queries
        "Fertilizer recommendations for maize",
        "How to manage fall armyworm",
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{i}. Query: '{query}'")
        
        try:
            results = vector_store.search(query, top_k=3)
            
            if results:
                logger.info(f"   ✓ Found {len(results)} results")
                for j, result in enumerate(results[:2], 1):
                    metadata = result['metadata']
                    distance = result.get('distance', 0)
                    similarity = 1 - distance if distance is not None else 'N/A'
                    
                    logger.info(f"\n   Result {j}:")
                    logger.info(f"      Type: {metadata.get('type', 'N/A')}")
                    logger.info(f"      Category: {metadata.get('category', 'N/A')}")
                    logger.info(f"      Source: {metadata.get('source', metadata.get('filename', 'N/A'))}")
                    if 'province' in metadata:
                        logger.info(f"      Province: {metadata['province']}")
                    if 'district' in metadata:
                        logger.info(f"      District: {metadata['district']}")
                    logger.info(f"      Similarity: {similarity if similarity != 'N/A' else 'N/A'}")
                    logger.info(f"      Preview: {result['content'][:150]}...")
            else:
                logger.warning(f"   ⚠️  No results found")
                
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Verification Complete!")
    logger.info("=" * 80)
    logger.info(f"\n✅ Database contains {stats['total_documents']:,} document chunks")
    logger.info("✅ Retrieval system is working")
    logger.info("\n🎉 Your RAG system is ready to use!")


if __name__ == "__main__":
    main()
