#!/usr/bin/env python3
"""
Full ingestion script for all agricultural documents.
Processes PDFs and DOCX files, extracts district/province info, and embeds into vector database.
"""

import sys
from pathlib import Path
import yaml
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.enhanced_processor import EnhancedDocumentProcessor
from src.embeddings.vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion process for all documents."""
    start_time = datetime.now()
    
    logger.info("=" * 80)
    logger.info("FULL AGRICULTURE RAG PLATFORM - COMPREHENSIVE INGESTION")
    logger.info("=" * 80)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    raw_docs_path = config['data']['raw_documents']
    logger.info(f"\n📂 Source Directory: {raw_docs_path}")
    
    if not Path(raw_docs_path).exists():
        logger.error(f"❌ Document directory not found: {raw_docs_path}")
        sys.exit(1)
    
    # Count files
    pdf_count = len(list(Path(raw_docs_path).glob("*.pdf")))
    docx_count = len(list(Path(raw_docs_path).glob("*.docx"))) + len(list(Path(raw_docs_path).glob("*.doc")))
    total_files = pdf_count + docx_count
    
    logger.info(f"📊 Files to process:")
    logger.info(f"   - PDFs: {pdf_count}")
    logger.info(f"   - DOCX: {docx_count}")
    logger.info(f"   - Total: {total_files}")
    
    # Step 1: Initialize Enhanced Processor
    logger.info("\n" + "=" * 80)
    logger.info("📄 Step 1: Initializing Enhanced Document Processor")
    logger.info("=" * 80)
    
    processor = EnhancedDocumentProcessor(
        chunk_size=config['embeddings']['chunk_size'],
        chunk_overlap=config['embeddings']['chunk_overlap'],
        use_ocr=True  # Enable OCR for scanned PDFs
    )
    
    # Step 2: Process all documents
    logger.info("\n" + "=" * 80)
    logger.info("📄 Step 2: Processing All Documents")
    logger.info("=" * 80)
    logger.info("This may take 1-3 hours depending on file sizes and OCR needs...")
    logger.info("Progress will be shown below:\n")
    
    try:
        documents = processor.process_directory(raw_docs_path)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not documents:
        logger.error("❌ No documents were processed successfully")
        sys.exit(1)
    
    logger.info(f"\n✓ Successfully processed {len(documents)} document chunks")
    
    # Analyze geographic coverage
    logger.info("\n" + "=" * 80)
    logger.info("🗺️  Geographic Coverage Analysis")
    logger.info("=" * 80)
    
    all_districts = set()
    all_provinces = set()
    all_regions = set()
    
    for doc in documents:
        if doc.metadata.get('districts'):
            all_districts.update(doc.metadata['districts'])
        if doc.metadata.get('provinces'):
            all_provinces.update(doc.metadata['provinces'])
        if doc.metadata.get('natural_regions'):
            all_regions.update(doc.metadata['natural_regions'])
    
    logger.info(f"📍 Found {len(all_districts)} unique districts:")
    for district in sorted(all_districts)[:20]:
        logger.info(f"   - {district}")
    if len(all_districts) > 20:
        logger.info(f"   ... and {len(all_districts) - 20} more")
    
    logger.info(f"\n📍 Found {len(all_provinces)} unique provinces:")
    for province in sorted(all_provinces):
        logger.info(f"   - {province}")
    
    logger.info(f"\n📍 Found {len(all_regions)} unique natural regions:")
    for region in sorted(all_regions):
        logger.info(f"   - {region}")
    
    # Step 3: Initialize Vector Store
    logger.info("\n" + "=" * 80)
    logger.info("🔍 Step 3: Initializing Vector Store")
    logger.info("=" * 80)
    
    vector_db_path = Path(__file__).parent.parent / "data" / "vector_db"
    
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    # Check existing documents
    stats_before = vector_store.get_stats()
    logger.info(f"Current database size: {stats_before['total_documents']} documents")
    
    # Step 4: Add documents to vector store
    logger.info("\n" + "=" * 80)
    logger.info("💾 Step 4: Adding Documents to Vector Database")
    logger.info("=" * 80)
    logger.info("Generating embeddings and storing in database...")
    logger.info("This may take 30-60 minutes for large collections...\n")
    
    try:
        vector_store.add_documents(
            documents,
            batch_size=config['embeddings']['batch_size']
        )
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Embedding process interrupted by user")
        logger.info("Partial data may have been saved to the database")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error during embedding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 5: Verify
    logger.info("\n" + "=" * 80)
    logger.info("✅ Step 5: Verification & Statistics")
    logger.info("=" * 80)
    
    stats_after = vector_store.get_stats()
    
    elapsed_time = datetime.now() - start_time
    hours = int(elapsed_time.total_seconds() // 3600)
    minutes = int((elapsed_time.total_seconds() % 3600) // 60)
    seconds = int(elapsed_time.total_seconds() % 60)
    
    logger.info("\n" + "=" * 80)
    logger.info("🎉 INGESTION COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"⏱️  Total Time: {hours}h {minutes}m {seconds}s")
    logger.info(f"📊 Documents before: {stats_before['total_documents']:,}")
    logger.info(f"📊 Documents after: {stats_after['total_documents']:,}")
    logger.info(f"📊 New documents added: {len(documents):,}")
    logger.info(f"📁 Source files processed: {total_files}")
    logger.info(f"🗺️  Districts covered: {len(all_districts)}")
    logger.info(f"🗺️  Provinces covered: {len(all_provinces)}")
    logger.info(f"🗺️  Natural Regions: {len(all_regions)}")
    logger.info(f"📂 Categories: {', '.join(stats_after['categories'])}")
    logger.info(f"🔍 Embedding Model: {stats_after['embedding_model']}")
    logger.info(f"💾 Vector DB Location: {vector_db_path}")
    logger.info("=" * 80)
    
    # Test queries
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Retrieval with Sample Queries")
    logger.info("=" * 80)
    
    test_queries = [
        "Bindura district agriculture",
        "Maize farming in Mashonaland East",
        "Hwange district profile",
        "Cattle farming in Matabeleland",
        "Natural Region IV crops"
    ]
    
    for query in test_queries:
        logger.info(f"\n🔍 Query: '{query}'")
        try:
            results = vector_store.search(query, top_k=2)
            if results:
                result = results[0]
                filename = result['metadata'].get('filename', 'Unknown')
                districts = result['metadata'].get('districts', [])
                provinces = result['metadata'].get('provinces', [])
                
                logger.info(f"   ✓ Top result: {filename}")
                if districts:
                    logger.info(f"   📍 Districts: {', '.join(districts)}")
                if provinces:
                    logger.info(f"   📍 Provinces: {', '.join(provinces)}")
                logger.info(f"   📄 Preview: {result['content'][:150]}...")
            else:
                logger.warning(f"   ⚠️  No results found")
        except Exception as e:
            logger.error(f"   ❌ Query failed: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ SYSTEM READY FOR USE!")
    logger.info("=" * 80)
    logger.info("\nYou can now:")
    logger.info("1. Start the API: uvicorn src.api.main:app --reload")
    logger.info("2. Test queries: python scripts/verify_ingestion.py")
    logger.info("3. Access web interface: http://localhost:8000")
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
