#!/usr/bin/env python3
"""
Direct test of vector database retrieval for district-specific data.
"""

import sys
from pathlib import Path
import yaml

sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore

def main():
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize vector store
    vector_db_path = Path(__file__).parent.parent / "data" / "vector_db"
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    print("=" * 80)
    print("TESTING VECTOR DATABASE RETRIEVAL")
    print("=" * 80)
    
    # Test queries for district/province data
    test_queries = [
        "Tell me about maize farming in Harare province",
        "What are the recommended crops for Mashonaland East?",
        "Cattle farming in Matabeleland South",
        "Fertilizer recommendations for maize in Natural Region IV",
        "What districts are suitable for wheat production?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        results = vector_store.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n--- Result {i} ---")
                print(f"Type: {result['metadata'].get('type', 'N/A')}")
                print(f"Category: {result['metadata'].get('category', 'N/A')}")
                print(f"Source: {result['metadata'].get('source', 'N/A')}")
                
                if 'province' in result['metadata']:
                    print(f"Province: {result['metadata']['province']}")
                if 'crop' in result['metadata']:
                    print(f"Crop: {result['metadata']['crop']}")
                if 'livestock_type' in result['metadata']:
                    print(f"Livestock: {result['metadata']['livestock_type']}")
                    
                distance = result.get('distance', 0)
                similarity = 1 - distance if distance is not None else 'N/A'
                print(f"Similarity: {similarity}")
                
                print(f"\nContent Preview:")
                print(result['content'][:300])
                print("...")
        else:
            print("No results found!")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
