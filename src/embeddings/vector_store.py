"""
Vector store module for agriculture RAG platform.
Handles document embeddings and similarity search using ChromaDB.
"""

import os
from typing import List, Dict, Optional, Tuple
import logging

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

from ..ingestion.document_processor import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages document embeddings and retrieval using ChromaDB."""
    
    def __init__(
        self, 
        persist_directory: str,
        collection_name: str = "agriculture_docs",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized. Collection '{collection_name}' has {self.collection.count()} documents")
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding texts"):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            embeddings.extend(batch_embeddings.tolist())
        
        return embeddings
    
    def add_documents(self, documents: List[Document], batch_size: int = 100):
        """Add documents to the vector store."""
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Prepare data
        texts = [doc.content for doc in documents]
        ids = [f"{doc.doc_id}_chunk_{doc.chunk_id}" for doc in documents]
        metadatas = []
        for doc in documents:
            processed_metadata = {}
            for key, value in doc.metadata.items():
                if isinstance(value, list):
                    processed_metadata[key] = ", ".join(value)
                else:
                    processed_metadata[key] = value
            metadatas.append(processed_metadata)
        
        # Generate embeddings
        embeddings = self.embed_texts(texts, batch_size=batch_size)
        
        # Add to ChromaDB in batches
        for i in tqdm(range(0, len(documents), batch_size), desc="Adding to vector store"):
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas
            )
        
        logger.info(f"Successfully added {len(documents)} documents. Total: {self.collection.count()}")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'id': results['ids'][0][i]
                })
        
        return formatted_results
    
    def search_with_score_threshold(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search with a minimum similarity score threshold."""
        results = self.search(query, top_k=top_k * 2, filter_metadata=filter_metadata)
        
        # Filter by score (lower distance = higher similarity for cosine)
        # Convert distance to similarity score: similarity = 1 - distance
        filtered_results = []
        for result in results:
            if result['distance'] is not None:
                similarity = 1 - result['distance']
                if similarity >= score_threshold:
                    result['similarity_score'] = similarity
                    filtered_results.append(result)
        
        return filtered_results[:top_k]
    
    def delete_collection(self):
        """Delete the current collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        count = self.collection.count()
        
        # Get sample of metadata to understand categories
        sample = self.collection.get(limit=min(100, count))
        categories = set()
        if sample['metadatas']:
            for meta in sample['metadatas']:
                if 'category' in meta:
                    categories.add(meta['category'])
        
        return {
            'total_documents': count,
            'collection_name': self.collection_name,
            'categories': list(categories),
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension()
        }


if __name__ == "__main__":
    # Test the vector store
    vector_store = VectorStore(
        persist_directory="./data/vector_db",
        collection_name="agriculture_docs"
    )
    
    print("Vector store stats:", vector_store.get_stats())
