#!/usr/bin/env python3
"""
Test rainfall data integration by running sample queries.
"""

import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.embeddings.vector_store import VectorStore

def test_rainfall_queries():
    """Test various rainfall-related queries."""
    
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize vector store
    vector_db_path = Path(__file__).parent / "data" / "vector_db"
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    # Test queries
    queries = [
        "What is the average rainfall in Masvingo district?",
        "Tell me about rainfall patterns in Harare",
        "Which districts have low rainfall?",
        "Compare rainfall between 1980s and 2010s in Gweru",
        "Is irrigation needed in Beitbridge?",
        "What are the recent rainfall trends in Manicaland?",
        "Show me districts with stable rainfall patterns",
        "Climate risk assessment for Bulawayo district"
    ]
    
    print("=" * 70)
    print("Testing Rainfall Data Queries")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}] Query: {query}")
        print("-" * 70)
        
        results = vector_store.search(query, top_k=3)
        
        if results:
            for j, result in enumerate(results, 1):
                metadata = result['metadata']
                print(f"\n  Result {j}:")
                print(f"    Type: {metadata.get('type', 'N/A')}")
                print(f"    Province: {metadata.get('province', 'N/A')}")
                print(f"    District: {metadata.get('district', 'N/A')}")
                if 'mean_rainfall_mm' in metadata:
                    print(f"    Mean Rainfall: {metadata.get('mean_rainfall_mm')} mm")
                if 'rainfall_pattern' in metadata:
                    print(f"    Pattern: {metadata.get('rainfall_pattern')}")
                print(f"    Relevance Score: {result.get('score', 0):.4f}")
                
                # Show snippet of content
                content = result.get('content', '')
                snippet = content[:200] + "..." if len(content) > 200 else content
                print(f"    Content Preview: {snippet}")
        else:
            print("  ⚠️  No results found")
    
    print("\n" + "=" * 70)
    print("✅ Testing Complete!")
    print("=" * 70)
    
    # Get overall stats
    stats = vector_store.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total Documents: {stats.get('total_documents', 'N/A')}")
    print(f"  Rainfall documents available for querying")

if __name__ == "__main__":
    test_rainfall_queries()
