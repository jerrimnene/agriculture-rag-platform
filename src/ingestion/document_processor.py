"""
Document processing module for agriculture RAG platform.
Handles PDF extraction, text cleaning, and chunking.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

import pypdf
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a processed document chunk."""
    content: str
    metadata: Dict
    doc_id: str
    chunk_id: int


class DocumentProcessor:
    """Processes agricultural documents for RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\-\:\;\?\!\/\(\)\%\$]', '', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\b\d{1,3}\s*\|\s*Page\b', '', text)
        text = re.sub(r'\bPage\s+\d{1,3}\b', '', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, doc_id: str) -> List[Document]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text) < 100:  # Skip very small chunks
                continue
                
            chunks.append(Document(
                content=chunk_text,
                metadata={
                    'source': doc_id,
                    'chunk_index': len(chunks),
                    'total_words': len(chunk_words)
                },
                doc_id=doc_id,
                chunk_id=len(chunks)
            ))
        
        return chunks
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract metadata from document filename and path."""
        file_name = Path(file_path).stem
        
        # Determine document category based on filename
        categories = {
            'crop': ['maize', 'soya', 'bean', 'pepper', 'grains', 'horticultur'],
            'livestock': ['cattle', 'goat', 'pig', 'broiler', 'chicken', 'fish'],
            'policy': ['policy', 'framework', 'strategy', 'vision'],
            'climate': ['climate', 'csa', 'ipcc'],
            'market': ['market', 'value-chain', 'linkage'],
            'food_security': ['zimvac', 'fews', 'livelihoods', 'assessment']
        }
        
        category = 'general'
        for cat, keywords in categories.items():
            if any(keyword in file_name.lower() for keyword in keywords):
                category = cat
                break
        
        return {
            'filename': Path(file_path).name,
            'category': category,
            'file_path': file_path
        }
    
    def process_document(self, file_path: str) -> List[Document]:
        """Process a single document."""
        logger.info(f"Processing: {Path(file_path).name}")
        
        # Extract text
        raw_text = self.extract_text_from_pdf(file_path)
        if not raw_text:
            logger.warning(f"No text extracted from {file_path}")
            return []
        
        # Clean text
        clean_text = self.clean_text(raw_text)
        
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        doc_id = Path(file_path).stem
        
        # Chunk text
        chunks = self.chunk_text(clean_text, doc_id)
        
        # Add metadata to all chunks
        for chunk in chunks:
            chunk.metadata.update(metadata)
        
        logger.info(f"Created {len(chunks)} chunks from {Path(file_path).name}")
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Document]:
        """Process all PDF documents in a directory."""
        all_chunks = []
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in tqdm(pdf_files, desc="Processing documents"):
            chunks = self.process_document(str(pdf_file))
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


if __name__ == "__main__":
    # Test the processor
    processor = DocumentProcessor()
    data_path = "/Users/providencemtendereki/Documents/Old Staff/data_raw"
    
    if os.path.exists(data_path):
        documents = processor.process_directory(data_path)
        print(f"Processed {len(documents)} document chunks")
    else:
        print(f"Data path not found: {data_path}")
