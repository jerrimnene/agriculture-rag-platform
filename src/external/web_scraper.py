"""
Web Scraping Module for External Agricultural Data Sources
Fetches and indexes content from international organizations
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDataSource:
    """Base class for web data sources."""
    
    def __init__(self, name: str, base_url: str, categories: List[str]):
        self.name = name
        self.base_url = base_url
        self.categories = categories
        self.last_scraped = None
    
    def fetch_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (AgriRAG Bot; +https://example.com/bot)'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def generate_doc_id(self, url: str) -> str:
        """Generate unique document ID from URL."""
        return hashlib.md5(url.encode()).hexdigest()


class ZimbabweAgricultureScraper:
    """Main scraper for Zimbabwe agricultural data sources."""
    
    # Priority sources for Zimbabwe agriculture
    PRIORITY_SOURCES = [
        {
            'name': 'World Bank Zimbabwe',
            'urls': [
                'https://www.worldbank.org/en/country/zimbabwe',
                'https://www.worldbank.org/en/topic/agriculture'
            ],
            'category': 'policy',
            'organization': 'World Bank'
        },
        {
            'name': 'FAO Zimbabwe',
            'urls': [
                'https://www.fao.org/zimbabwe/en/',
                'https://www.fao.org/faostat/en'
            ],
            'category': 'crop',
            'organization': 'FAO'
        },
        {
            'name': 'USAID Zimbabwe',
            'urls': [
                'https://www.usaid.gov/zimbabwe'
            ],
            'category': 'development',
            'organization': 'USAID'
        },
        {
            'name': 'ICRISAT',
            'urls': [
                'https://www.icrisat.org'
            ],
            'category': 'research',
            'organization': 'ICRISAT'
        },
        {
            'name': 'CGIAR',
            'urls': [
                'https://www.cgiar.org'
            ],
            'category': 'research',
            'organization': 'CGIAR'
        }
    ]
    
    def __init__(self, cache_dir: str = "./data/web_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scrape_log = self.cache_dir / "scrape_log.json"
        self.load_log()
    
    def load_log(self):
        """Load scraping log."""
        if self.scrape_log.exists():
            with open(self.scrape_log, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = {'sources': {}, 'last_run': None}
    
    def save_log(self):
        """Save scraping log."""
        with open(self.scrape_log, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def should_scrape(self, source_name: str, max_age_hours: int = 168) -> bool:
        """Check if source should be scraped based on age."""
        if source_name not in self.log['sources']:
            return True
        
        last_scraped = self.log['sources'][source_name].get('last_scraped')
        if not last_scraped:
            return True
        
        # Check if older than max age
        last_time = datetime.fromisoformat(last_scraped)
        age_hours = (datetime.now() - last_time).total_seconds() / 3600
        
        return age_hours > max_age_hours
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """Scrape a single source."""
        logger.info(f"Scraping {source['name']}...")
        
        documents = []
        
        for url in source['urls']:
            try:
                # Fetch content
                html = self._fetch_with_retry(url)
                if not html:
                    continue
                
                # Extract text
                soup = BeautifulSoup(html, 'html.parser')
                text = self._extract_clean_text(soup)
                
                if len(text) < 100:  # Skip if too short
                    continue
                
                # Create document
                doc = {
                    'url': url,
                    'source': source['name'],
                    'organization': source['organization'],
                    'category': source['category'],
                    'content': text[:10000],  # Limit to 10k chars
                    'scraped_at': datetime.now().isoformat(),
                    'title': self._extract_title(soup),
                    'doc_id': hashlib.md5(url.encode()).hexdigest()
                }
                
                documents.append(doc)
                
                # Cache the document
                self._cache_document(doc)
                
                # Be polite - wait between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        # Update log
        self.log['sources'][source['name']] = {
            'last_scraped': datetime.now().isoformat(),
            'documents_fetched': len(documents)
        }
        self.save_log()
        
        return documents
    
    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch URL with retry logic."""
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; AgriRAG/1.0; +https://agrievidence.com)'
                }
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
        return None
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from soup."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Get main content
        main = soup.find(['main', 'article', 'div[class*="content"]'])
        if main:
            text = main.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Untitled Document"
    
    def _cache_document(self, doc: Dict):
        """Cache document to disk."""
        cache_file = self.cache_dir / f"{doc['doc_id']}.json"
        with open(cache_file, 'w') as f:
            json.dump(doc, f, indent=2)
    
    def scrape_all_sources(self, force: bool = False) -> List[Dict]:
        """Scrape all priority sources."""
        all_documents = []
        
        for source in self.PRIORITY_SOURCES:
            if force or self.should_scrape(source['name']):
                docs = self.scrape_source(source)
                all_documents.extend(docs)
                logger.info(f"Fetched {len(docs)} documents from {source['name']}")
            else:
                logger.info(f"Skipping {source['name']} (recently scraped)")
        
        self.log['last_run'] = datetime.now().isoformat()
        self.save_log()
        
        return all_documents
    
    def get_cached_documents(self) -> List[Dict]:
        """Load all cached documents."""
        documents = []
        
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name == 'scrape_log.json':
                continue
            
            try:
                with open(cache_file, 'r') as f:
                    doc = json.load(f)
                    documents.append(doc)
            except Exception as e:
                logger.error(f"Error loading cached document {cache_file}: {e}")
        
        return documents


class ExternalDataIndexer:
    """Indexes external web data into the vector store."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.scraper = ZimbabweAgricultureScraper()
    
    def index_web_data(self, force_scrape: bool = False) -> Dict:
        """Scrape and index external web data."""
        logger.info("Starting external data indexing...")
        
        # Scrape sources
        documents = self.scraper.scrape_all_sources(force=force_scrape)
        
        if not documents:
            logger.info("No new documents to index")
            return {'indexed': 0, 'total': 0}
        
        # Convert to Document format
        from ..ingestion.document_processor import Document
        
        doc_objects = []
        for doc in documents:
            # Split into chunks if needed
            chunks = self._chunk_text(doc['content'], max_length=1000)
            
            for idx, chunk in enumerate(chunks):
                doc_obj = Document(
                    doc_id=doc['doc_id'],
                    content=chunk,
                    metadata={
                        'filename': f"{doc['source']}_{doc['doc_id']}.web",
                        'source': doc['source'],
                        'organization': doc['organization'],
                        'category': doc['category'],
                        'url': doc['url'],
                        'title': doc['title'],
                        'scraped_at': doc['scraped_at'],
                        'chunk_index': idx
                    },
                    chunk_id=idx
                )
                doc_objects.append(doc_obj)
        
        # Add to vector store
        self.vector_store.add_documents(doc_objects)
        
        logger.info(f"Indexed {len(doc_objects)} chunks from {len(documents)} web documents")
        
        return {
            'indexed': len(doc_objects),
            'total': len(documents),
            'sources': [doc['source'] for doc in documents]
        }
    
    def _chunk_text(self, text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_length
            chunk = text[start:end]
            
            # Try to break at sentence
            if end < len(text):
                last_period = chunk.rfind('. ')
                if last_period > max_length // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks


if __name__ == "__main__":
    # Test the scraper
    scraper = ZimbabweAgricultureScraper()
    
    print("Testing web scraper...")
    documents = scraper.scrape_all_sources(force=True)
    
    print(f"\nScraped {len(documents)} documents")
    for doc in documents[:3]:
        print(f"\n- {doc['title']}")
        print(f"  Source: {doc['organization']}")
        print(f"  URL: {doc['url']}")
        print(f"  Content length: {len(doc['content'])} chars")
