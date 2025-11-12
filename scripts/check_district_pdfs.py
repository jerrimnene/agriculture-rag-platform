#!/usr/bin/env python3
"""
Check if district-specific PDFs are ingested in the vector database.
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
    print("CHECKING DISTRICT-SPECIFIC PDFs IN VECTOR DATABASE")
    print("=" * 80)
    
    # Test queries for specific districts
    districts = [
        "Bindura",
        "Hwange",
        "Masvingo",
        "Mutare",
        "Gweru",
        "Goromonzi",
        "Chipinge",
        "Beitbridge",
        "Gokwe North",
        "Tsholotsho"
    ]
    
    found_count = 0
    
    for district in districts:
        query = f"{district} district agriculture profile"
        results = vector_store.search(query, top_k=1)
        
        if results:
            result = results[0]
            filename = result['metadata'].get('filename', result['metadata'].get('source', 'Unknown'))
            
            # Check if it's a district-specific PDF
            if 'District' in filename or district.lower() in filename.lower():
                print(f"✅ {district}: Found '{filename}'")
                found_count += 1
            else:
                print(f"⚠️  {district}: Found but not district-specific ('{filename}')")
        else:
            print(f"❌ {district}: No results found")
    
    print("\n" + "=" * 80)
    print(f"District PDFs Found: {found_count}/{len(districts)}")
    print("=" * 80)
    
    # Get all documents with "District" in filename
    print("\n📊 Sampling documents with 'District' in metadata...")
    
    # Search for a generic district query to see what's available
    results = vector_store.search("district profile agriculture", top_k=10)
    
    district_files = set()
    for result in results:
        filename = result['metadata'].get('filename', result['metadata'].get('source', ''))
        if 'District' in filename:
            district_files.add(filename)
    
    print(f"\nFound {len(district_files)} unique district files in sample:")
    for i, filename in enumerate(sorted(district_files)[:20], 1):
        print(f"  {i}. {filename}")
    
    if len(district_files) > 20:
        print(f"  ... and {len(district_files) - 20} more")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
