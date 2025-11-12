"""
Agentic RAG system for agriculture knowledge base.
Provides intelligent retrieval with multiple tools and reasoning.
"""

import json
from typing import List, Dict, Optional, Any
import logging

import ollama
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage

from ..embeddings.vector_store import VectorStore
from ..geo.enrich_context import ContextEnricher
from ..agents.citation_engine import CitationEngine
from ..translation.local_language import LocalLanguageTranslator
from ..reconciliation.source_reconciler import SourceReconciler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaLLM:
    """Wrapper for Ollama LLM to work with LangChain."""
    
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
    
    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Generate response from Ollama."""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'stop': stop if stop else []
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: {str(e)}"
    
    def generate(self, messages: List[Dict], **kwargs) -> str:
        """Generate chat completion."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return f"Error: {str(e)}"


class AgricultureRAGTools:
    """Tools for the agriculture RAG agent."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def semantic_search(self, query: str) -> str:
        """Search the agriculture knowledge base for relevant information."""
        results = self.vector_store.search_with_score_threshold(
            query=query,
            top_k=5,
            score_threshold=0.5
        )
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Format results
        formatted = "Found relevant information:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"[Source {i}: {result['metadata'].get('filename', 'Unknown')}]\n"
            formatted += f"{result['content'][:500]}...\n"
            formatted += f"(Relevance: {result.get('similarity_score', 0):.2f})\n\n"
        
        return formatted
    
    def category_search(self, query: str, category: str) -> str:
        """Search within a specific category (crop, livestock, policy, etc.)."""
        valid_categories = ['crop', 'livestock', 'policy', 'climate', 'market', 'food_security']
        
        if category not in valid_categories:
            return f"Invalid category. Valid categories are: {', '.join(valid_categories)}"
        
        results = self.vector_store.search_with_score_threshold(
            query=query,
            top_k=3,
            score_threshold=0.5,
            filter_metadata={'category': category}
        )
        
        if not results:
            return f"No relevant information found in the {category} category."
        
        formatted = f"Found in {category} documents:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"[{result['metadata'].get('filename', 'Unknown')}]\n"
            formatted += f"{result['content'][:400]}...\n\n"
        
        return formatted
    
    def multi_query_search(self, query: str) -> str:
        """Generate multiple query variations and combine results."""
        # For simplicity, use query variations
        variations = [
            query,
            f"best practices for {query}",
            f"guidelines for {query}",
        ]
        
        all_results = []
        seen_ids = set()
        
        for var_query in variations:
            results = self.vector_store.search(var_query, top_k=2)
            for result in results:
                if result['id'] not in seen_ids:
                    all_results.append(result)
                    seen_ids.add(result['id'])
        
        if not all_results:
            return "No relevant information found."
        
        # Take top 5 unique results
        formatted = "Comprehensive search results:\n\n"
        for i, result in enumerate(all_results[:5], 1):
            formatted += f"[Source {i}: {result['metadata'].get('filename', 'Unknown')}]\n"
            formatted += f"{result['content'][:400]}...\n\n"
        
        return formatted
    
    def list_categories(self) -> str:
        """List available document categories."""
        stats = self.vector_store.get_stats()
        categories = stats.get('categories', [])
        
        return f"Available categories: {', '.join(categories)}\nTotal documents: {stats['total_documents']}"


class AgricultureRAGAgent:
    """Main agentic RAG system with geo-context support."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm_model: str = "mistral",
        llm_base_url: str = "http://localhost:11434"
    ):
        self.vector_store = vector_store
        self.llm = OllamaLLM(model=llm_model, base_url=llm_base_url)
        self.tools_handler = AgricultureRAGTools(vector_store)
        self.context_enricher = ContextEnricher()
        self.citation_engine = CitationEngine()
        self.translator = LocalLanguageTranslator(llm_model=llm_model, llm_base_url=llm_base_url)
        self.reconciler = SourceReconciler()
        
        # Initialize tools
        self.tools = [
            Tool(
                name="semantic_search",
                func=self.tools_handler.semantic_search,
                description="Search the agriculture knowledge base for relevant information. Use this for general queries about farming, crops, livestock, or policies."
            ),
            Tool(
                name="category_search",
                func=lambda query: self.tools_handler.category_search(
                    query.split('|')[0],
                    query.split('|')[1] if '|' in query else 'crop'
                ),
                description="Search within a specific category. Input format: 'query|category'. Categories: crop, livestock, policy, climate, market, food_security"
            ),
            Tool(
                name="multi_query_search",
                func=self.tools_handler.multi_query_search,
                description="Perform a comprehensive search using multiple query variations. Use when you need broader context."
            ),
            Tool(
                name="list_categories",
                func=lambda x: self.tools_handler.list_categories(),
                description="List all available document categories and statistics."
            )
        ]
        
        logger.info(f"Agriculture RAG Agent initialized with {len(self.tools)} tools")
    
    def query(
        self, 
        user_query: str, 
        district: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        max_iterations: int = 3,
        include_translations: bool = True
    ) -> Dict[str, Any]:
        """Process a user query using the RAG system with optional geo-context.
        
        Args:
            user_query: User's question
            district: District name (optional)
            lat: Latitude (optional)
            lon: Longitude (optional)
            max_iterations: Maximum tool iterations (not used in simple mode)
            
        Returns:
            Dictionary with query, response, sources, and metadata
        """
        logger.info(f"Processing query: {user_query}")
        if district:
            logger.info(f"With district context: {district}")
        
        # Search for relevant documents
        results = self.vector_store.search_with_score_threshold(
            query=user_query,
            top_k=5,
            score_threshold=0.5
        )
        
        # Format results as chunks for enricher
        retrieved_chunks = []
        for result in results:
            retrieved_chunks.append({
                'content': result['content'],
                'metadata': result.get('metadata', {})
            })
        
        # Build AgriEvidence prompt with geo-context
        enriched_prompt = self.context_enricher.build_agrievidence_prompt(
            question=user_query,
            retrieved_chunks=retrieved_chunks,
            district=district,
            lat=lat,
            lon=lon
        )
        
        # Generate response
        messages = [
            {"role": "user", "content": enriched_prompt}
        ]
        
        response = self.llm.generate(messages)
        
        # Get geo context for metadata
        geo_context = None
        if district or (lat and lon):
            geo_context = self.context_enricher._get_geo_context(district, lat, lon)
        
        # Generate citations with confidence scoring
        citations = self.citation_engine.format_citations(results, include_confidence=True)
        
        # Check for conflicting sources and reconcile if needed
        reconciliation_result = None
        if len(results) >= 2:
            try:
                # Prepare sources for reconciliation
                sources_for_reconciliation = [
                    {
                        'content': result['content'],
                        'metadata': result.get('metadata', {})
                    }
                    for result in results
                ]
                reconciliation_result = self.reconciler.reconcile_sources(
                    sources_for_reconciliation,
                    user_query
                )
                logger.info(f"Reconciliation: {reconciliation_result.get('summary', 'Complete')}")
            except Exception as e:
                logger.warning(f"Source reconciliation failed: {e}")
        
        # Generate multilingual summary
        translations = None
        if include_translations:
            try:
                translations = self.translator.generate_multilingual_summary(response)
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
                translations = {'english': 'Key points: ' + response[:200]}
        
        return {
            'query': user_query,
            'response': response,
            'sources': retrieved_chunks,
            'citations': citations,
            'translations': translations,
            'reconciliation': reconciliation_result,
            'tool_used': 'semantic_search_with_geo_context',
            'geo_context': geo_context
        }
    
    def chat(
        self, 
        messages: List[Dict[str, str]],
        district: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> str:
        """Handle multi-turn conversations with optional geo-context.
        
        Args:
            messages: Conversation history
            district: District name (optional)
            lat: Latitude (optional)
            lon: Longitude (optional)
            
        Returns:
            Assistant's response string
        """
        # Get last user message for retrieval
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            return "No user message found."
        
        last_query = user_messages[-1]['content']
        
        # Retrieve relevant context
        results = self.vector_store.search_with_score_threshold(
            query=last_query,
            top_k=5,
            score_threshold=0.5
        )
        
        # Format results as chunks
        retrieved_chunks = []
        for result in results:
            retrieved_chunks.append({
                'content': result['content'],
                'metadata': result.get('metadata', {})
            })
        
        # Build enriched prompt
        enriched_content = self.context_enricher.build_agrievidence_prompt(
            question=last_query,
            retrieved_chunks=retrieved_chunks,
            district=district,
            lat=lat,
            lon=lon
        )
        
        # Replace last user message with enriched version
        enhanced_messages = messages[:-1] + [
            {'role': 'user', 'content': enriched_content}
        ]
        
        # Generate response
        response = self.llm.generate(enhanced_messages)
        return response


if __name__ == "__main__":
    # Test the agent
    from ..embeddings.vector_store import VectorStore
    
    vector_store = VectorStore(
        persist_directory="/Users/providencemtendereki/agriculture-rag-platform/data/vector_db",
        collection_name="agriculture_docs"
    )
    
    agent = AgricultureRAGAgent(vector_store)
    
    # Test query
    result = agent.query("What are the best practices for maize farming in Zimbabwe?")
    print("Response:", result['response'])
