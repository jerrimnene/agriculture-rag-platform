#!/usr/bin/env python3
"""
Check and diagnose ChromaDB issues
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import chromadb
from chromadb.config import Settings

def check_db():
    db_path = Path(__file__).parent.parent / "data" / "vector_db"
    
    print(f"Checking ChromaDB at: {db_path}")
    
    try:
        client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # List collections
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collection(s):")
        
        for coll in collections:
            print(f"\n  Collection: {coll.name}")
            print(f"  Count: {coll.count()}")
            
            # Try to get a sample
            try:
                sample = coll.get(limit=1)
                if sample['metadatas']:
                    print(f"  Sample metadata keys: {list(sample['metadatas'][0].keys())}")
            except Exception as e:
                print(f"  Error getting sample: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nThe database may be corrupted or using an incompatible schema.")
        print("Recommendation: Delete and rebuild the vector database.")

if __name__ == "__main__":
    check_db()
