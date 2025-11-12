#!/usr/bin/env python3
"""
Initialize the vector database with agriculture documents.
This script processes all PDFs and creates embeddings.
"""

import sys
from pathlib import Path
import yaml
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.document_processor import DocumentProcessor
from src.embeddings.vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the vector database."""
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info("=" * 60)
    logger.info("Agriculture RAG Platform - Database Initialization")
    logger.info("=" * 60)
    
    # Step 1: Process documents
    logger.info("\n📄 Step 1: Processing PDF documents...")
    processor = DocumentProcessor(
        chunk_size=config['embeddings']['chunk_size'],
        chunk_overlap=config['embeddings']['chunk_overlap']
    )
    
    raw_docs_path = config['data']['raw_documents']
    logger.info(f"Reading documents from: {raw_docs_path}")
    
    if not Path(raw_docs_path).exists():
        logger.error(f"❌ Document directory not found: {raw_docs_path}")
        sys.exit(1)
    
    documents = processor.process_directory(raw_docs_path)
    
    if not documents:
        logger.error("❌ No documents were processed")
        sys.exit(1)
    
    logger.info(f"✓ Processed {len(documents)} document chunks")
    
    # Step 2: Create vector store
    logger.info("\n🔍 Step 2: Creating vector embeddings...")
    vector_db_path = Path(__file__).parent.parent / "data" / "vector_db"
    
    vector_store = VectorStore(
        persist_directory=str(vector_db_path),
        collection_name=config['vector_store']['collection_name'],
        embedding_model=config['embeddings']['model_name']
    )
    
    # Step 3: Add documents to vector store
    logger.info("\n💾 Step 3: Adding documents to vector database...")
    vector_store.add_documents(
        documents,
        batch_size=config['embeddings']['batch_size']
    )
    
    # Step 4: Verify
    logger.info("\n✅ Step 4: Verification...")
    stats = vector_store.get_stats()
    
    logger.info("=" * 60)
    logger.info("Database Initialization Complete!")
    logger.info("=" * 60)
    logger.info(f"Total documents: {stats['total_documents']}")
    logger.info(f"Categories: {', '.join(stats['categories'])}")
    logger.info(f"Embedding dimension: {stats['embedding_model']}")
    logger.info(f"Vector DB location: {vector_db_path}")
    logger.info("=" * 60)
    
    # Test query
    logger.info("\n🧪 Testing with a sample query...")
    test_results = vector_store.search("maize farming best practices", top_k=3)
    
    if test_results:
        logger.info(f"✓ Found {len(test_results)} relevant results for test query")
        logger.info(f"  Top result: {test_results[0]['metadata'].get('filename', 'Unknown')}")
    else:
        logger.warning("⚠️  No results found for test query")
    
    logger.info("\n🎉 System is ready! You can now start the API server.")


if __name__ == "__main__":
    main()
