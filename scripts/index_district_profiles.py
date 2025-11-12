#!/usr/bin/env python3
"""
Index Zimbabwe District Profiles into Vector Database
Processes the comprehensive district profiles and adds them to the RAG system.
"""

import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.rag_agent import AgricultureRAGAgent
from src.embeddings.vector_store import VectorStore
from src.ingestion.document_processor import Document


def parse_district_profiles(file_path: str) -> list[dict]:
    """Parse the district profiles markdown file into structured chunks."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by district headers
    districts = re.split(r'\n## ([A-Z\s\(\)]+DISTRICT[^\n]*)\s*\n', content)
    
    chunks = []
    
    # Skip the first element (header)
    for i in range(1, len(districts), 2):
        if i + 1 < len(districts):
            district_name = districts[i].strip()
            district_content = districts[i + 1].strip()
            
            # Create a full document for the district
            full_text = f"## {district_name}\n\n{district_content}"
            
            chunks.append({
                'text': full_text,
                'metadata': {
                    'source': 'zimbabwe_district_profiles',
                    'district': district_name.replace(' DISTRICT', '').strip(),
                    'type': 'district_profile',
                    'category': 'geography'
                }
            })
            
            # Also create smaller chunks for specific sections
            sections = {
                'Natural Region': r'\*\*Natural Region:\*\*\s*([^\n]+)',
                'Province': r'\*\*Province:\*\*\s*([^\n]+)',
                'Main Town': r'\*\*Main Town[:/]\*\*\s*([^\n]+)',
                'Markets': r'\*\*Markets:\*\*\s*([^\n]+)',
                'Agriculture': r'\*\*Agriculture:\*\*\s*(.*?)(?=\n##|\n---|\Z)',
                'Challenges': r'\*\*Challenges:\*\*\s*([^\n]+)',
                'Opportunities': r'\*\*Opportunities:\*\*\s*([^\n]+)',
            }
            
            for section_name, pattern in sections.items():
                match = re.search(pattern, district_content, re.DOTALL)
                if match:
                    section_text = match.group(1).strip()
                    
                    # Create focused chunk
                    chunk_text = f"## {district_name} - {section_name}\n\n{section_text}"
                    
                    chunks.append({
                        'text': chunk_text,
                        'metadata': {
                            'source': 'zimbabwe_district_profiles',
                            'district': district_name.replace(' DISTRICT', '').strip(),
                            'type': f'district_{section_name.lower().replace(" ", "_")}',
                            'category': 'geography',
                            'section': section_name
                        }
                    })
    
    return chunks


def main():
    """Main indexing function."""
    
    print("=" * 70)
    print("ZIMBABWE DISTRICT PROFILES INDEXING")
    print("=" * 70)
    
    # File path
    file_path = 'data/raw/zimbabwe_district_profiles.md'
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"\n📄 Reading district profiles from: {file_path}")
    
    # Parse profiles
    print("\n🔍 Parsing district profiles...")
    chunks = parse_district_profiles(file_path)
    print(f"✓ Parsed {len(chunks)} chunks from district profiles")
    
    # Initialize vector store and RAG agent
    print("\n🤖 Initializing vector store and RAG agent...")
    vector_store = VectorStore(persist_directory="data/vector_db")
    agent = AgricultureRAGAgent(vector_store=vector_store)
    
    # Index documents
    print("\n📚 Indexing documents into vector database...")
    
    # Convert chunks to Document objects
    print("\n📦 Converting chunks to Document objects...")
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            content=chunk['text'],
            doc_id=f"district_profile_{i}",
            chunk_id=0,
            metadata=chunk['metadata']
        )
        documents.append(doc)
    
    print(f"✓ Created {len(documents)} Document objects")
    
    # Add all documents in one batch
    print("\n📥 Adding documents to vector store...")
    try:
        vector_store.add_documents(documents, batch_size=50)
        indexed_count = len(documents)
        print(f"\n✅ Successfully indexed {indexed_count} chunks")
    except Exception as e:
        print(f"\n❌ Error indexing documents: {e}")
        indexed_count = 0
    
    print(f"\n✅ Successfully indexed {indexed_count}/{len(chunks)} chunks")
    
    # Test query
    print("\n🧪 Testing with sample query...")
    result = agent.query(
        user_query="What are the main crops grown in Beitbridge district?",
        district="Beitbridge",
        include_translations=False
    )
    
    print(f"\n📝 Sample Answer:\n{result['response'][:300]}...")
    print(f"\n📊 Retrieved {len(result.get('sources', []))} sources")
    
    print("\n" + "=" * 70)
    print("✅ INDEXING COMPLETE!")
    print("=" * 70)
    print(f"\n💾 Total chunks indexed: {indexed_count}")
    print(f"📍 Districts covered: ~40+ districts with comprehensive profiles")
    print(f"🗄️  Vector database location: data/vector_db/")
    print("\n")


if __name__ == "__main__":
    main()
