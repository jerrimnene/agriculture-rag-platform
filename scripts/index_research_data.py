#!/usr/bin/env python3
"""
Index Agriculture Research Data into Vector Database
Processes research studies with citations and adds them to the RAG system.
"""

import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings.vector_store import VectorStore
from src.ingestion.document_processor import Document


def parse_research_data(file_path: str) -> list[dict]:
    """Parse the research data markdown file into structured chunks."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = []
    
    # Split by section markers (numbered sections or major headings)
    # Look for patterns like "1. DISTRICT" or "Section X:"
    sections = re.split(r'\n(?=\d+\.\s+[A-Z])', content)
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
            
        # Try to extract district/location from section
        district_match = re.search(r'(?:District|Province|Region)[:\s]*([A-Za-z\s,]+)', section, re.IGNORECASE)
        district = district_match.group(1).strip() if district_match else None
        
        # Extract DOI or URL if present
        url_match = re.search(r'https?://[^\s\)]+', section)
        citation_url = url_match.group(0) if url_match else None
        
        # Extract key findings or statistics
        stats_matches = re.findall(r'(\d+[\.\,]?\d*\s*(?:%|t/ha|kg/ha|ha|USD|persons))', section)
        
        # Create metadata
        metadata = {
            'source': 'agriculture_research_data',
            'type': 'research_study',
            'category': 'research',
            'section_id': i
        }
        
        if district:
            metadata['district'] = district
        if citation_url:
            metadata['citation_url'] = citation_url
        if stats_matches:
            metadata['has_statistics'] = True
        
        # Determine research topic
        if 'conservation' in section.lower() or 'ca' in section.lower():
            metadata['topic'] = 'conservation_agriculture'
        elif 'youth' in section.lower():
            metadata['topic'] = 'youth_in_agriculture'
        elif 'drought' in section.lower() or 'pfumvudza' in section.lower():
            metadata['topic'] = 'climate_adaptation'
        elif 'yield' in section.lower():
            metadata['topic'] = 'crop_productivity'
        else:
            metadata['topic'] = 'general_research'
        
        # Add the full section as a chunk
        chunks.append({
            'text': section.strip(),
            'metadata': metadata
        })
        
        # Also create smaller chunks for specific findings
        # Split by paragraph (double newline)
        paragraphs = [p.strip() for p in section.split('\n\n') if p.strip() and len(p.strip()) > 100]
        
        for j, para in enumerate(paragraphs[:3]):  # Max 3 paragraphs per section
            para_metadata = metadata.copy()
            para_metadata['type'] = 'research_finding'
            para_metadata['paragraph_id'] = j
            
            chunks.append({
                'text': para,
                'metadata': para_metadata
            })
    
    return chunks


def main():
    """Main indexing function."""
    
    print("=" * 70)
    print("AGRICULTURE RESEARCH DATA INDEXING")
    print("=" * 70)
    
    # File path
    file_path = 'data/raw/agriculture_research_data.md'
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"\n📄 Reading research data from: {file_path}")
    
    # Parse research data
    print("\n🔍 Parsing research data...")
    chunks = parse_research_data(file_path)
    print(f"✓ Parsed {len(chunks)} chunks from research data")
    
    # Show summary
    topics = {}
    citations = 0
    for chunk in chunks:
        topic = chunk['metadata'].get('topic', 'unknown')
        topics[topic] = topics.get(topic, 0) + 1
        if chunk['metadata'].get('citation_url'):
            citations += 1
    
    print(f"\n📊 Research Summary:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Citations found: {citations}")
    print(f"  Topics:")
    for topic, count in sorted(topics.items()):
        print(f"    - {topic}: {count} chunks")
    
    # Initialize vector store
    print("\n🤖 Initializing vector store...")
    vector_store = VectorStore(persist_directory="data/vector_db")
    
    # Convert chunks to Document objects
    print("\n📦 Converting chunks to Document objects...")
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            content=chunk['text'],
            doc_id=f"research_{i}",
            chunk_id=0,
            metadata=chunk['metadata']
        )
        documents.append(doc)
    
    print(f"✓ Created {len(documents)} Document objects")
    
    # Add all documents in one batch
    print("\n📥 Adding documents to vector store...")
    try:
        vector_store.add_documents(documents, batch_size=25)
        indexed_count = len(documents)
        print(f"\n✅ Successfully indexed {indexed_count} chunks")
    except Exception as e:
        print(f"\n❌ Error indexing documents: {e}")
        indexed_count = 0
    
    # Get updated stats
    stats = vector_store.get_stats()
    
    print("\n" + "=" * 70)
    print("✅ INDEXING COMPLETE!")
    print("=" * 70)
    print(f"\n💾 Total chunks indexed: {indexed_count}")
    print(f"📚 Total documents in database: {stats['total_documents']:,}")
    print(f"🔬 Research studies with citations: {citations}")
    print(f"🗄️  Vector database location: data/vector_db/")
    print("\n")


if __name__ == "__main__":
    main()
