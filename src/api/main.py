"""
FastAPI application for Agriculture RAG Platform.
Provides REST API endpoints for querying the knowledge base.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import yaml

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.embeddings.vector_store import VectorStore
from src.agents.rag_agent import AgricultureRAGAgent
from src.geo.geo_context import GeoContext
from src.weather.weather_api import WeatherAPI
from src.markets.market_api import MarketPricesAPI
from src.external.data_sync import ExternalDataSync, DataSource
from src.verification.evc_tracker import EVCTracker, VerifierRole
from src.historical.archive import HistoricalDataArchive, DataCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Initialize FastAPI app
app = FastAPI(
    title="Agriculture RAG Platform",
    description="Agentic RAG system for Zimbabwean agriculture knowledge",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config['api']['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store, agent, geo context, weather API, and market prices
vector_store = None
rag_agent = None
geo_context = None
weather_api = None
market_api = None
data_sync = None
evc_tracker = None
historical_archive = None


class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: Optional[int] = 5
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict]
    tool_used: str
    geo_context: Optional[Dict] = None
    citations: Optional[Dict] = None
    translations: Optional[Dict] = None
    confidence: Optional[Dict] = None
    reconciliation: Optional[Dict] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    global vector_store, rag_agent, geo_context, weather_api, market_api, data_sync, evc_tracker, historical_archive
    
    logger.info("Initializing AgriEvidence Platform...")
    logger.warning("Running in minimal mode - some features may require data setup")
    
    # Initialize lightweight services that don't require data
    try:
        geo_context = GeoContext()
        logger.info("✓ Geographic context initialized")
    except Exception as e:
        logger.warning(f"Could not initialize geo context: {e}")
    
    try:
        weather_api = WeatherAPI()
        logger.info("✓ Weather API initialized")
    except Exception as e:
        logger.warning(f"Could not initialize weather API: {e}")
    
    try:
        market_api = MarketPricesAPI()
        logger.info("✓ Market prices API initialized")
    except Exception as e:
        logger.warning(f"Could not initialize market API: {e}")
    
    # Try to initialize vector store and RAG agent
    try:
        vector_db_path = Path(__file__).parent.parent.parent / "data" / "vector_db"
        if vector_db_path.exists():
            vector_store = VectorStore(
                persist_directory=str(vector_db_path),
                collection_name=config['vector_store']['collection_name'],
                embedding_model=config['embeddings']['model_name']
            )
            
            rag_agent = AgricultureRAGAgent(
                vector_store=vector_store,
                llm_model=config['llm']['model'],
                llm_base_url=config['llm']['base_url']
            )
            logger.info("✓ Vector store and RAG agent initialized")
        else:
            logger.warning(f"Vector store directory not found: {vector_db_path}")
            logger.warning("RAG features will not be available until data is ingested")
    except Exception as e:
        logger.warning(f"Could not initialize vector store/RAG agent: {e}")
    
    # Try to initialize extended modules
    try:
        data_sync = ExternalDataSync()
        evc_tracker = EVCTracker()
        historical_archive = HistoricalDataArchive()
        logger.info("✓ Extended modules initialized")
    except Exception as e:
        logger.warning(f"Could not initialize extended modules: {e}")
    
    # Try to register extended endpoints
    try:
        from src.api.endpoints_extended import add_sync_endpoints, add_evc_endpoints, add_historical_endpoints
        from src.api.holistic_advisory_endpoints import add_holistic_advisory_endpoints
        from src.api.district_complete_endpoints import add_complete_district_endpoints
        if data_sync:
            add_sync_endpoints(app, data_sync)
        if evc_tracker:
            add_evc_endpoints(app, evc_tracker)
        if historical_archive:
            add_historical_endpoints(app, historical_archive)
        add_holistic_advisory_endpoints(app)
        if vector_store:
            add_complete_district_endpoints(app, vector_store)
        logger.info("✓ Extended endpoints registered")
    except Exception as e:
        logger.warning(f"Could not register all extended endpoints: {e}")
    
    logger.info("✓ Platform API started (health check available at /health)")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    html_file = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    
    if html_file.exists():
        with open(html_file, 'r') as f:
            return HTMLResponse(content=f.read())
    
    return HTMLResponse(content="""
    <html>
        <head><title>Agriculture RAG Platform</title></head>
        <body>
            <h1>Agriculture RAG Platform</h1>
            <p>API is running. Access the docs at <a href="/docs">/docs</a></p>
        </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "services": {
            "vector_store": vector_store is not None,
            "rag_agent": rag_agent is not None,
            "geo_context": geo_context is not None,
            "weather_api": weather_api is not None,
            "market_api": market_api is not None
        }
    }
    
    if vector_store is not None:
        try:
            status["vector_store_stats"] = vector_store.get_stats()
        except:
            pass
    
    return status


@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Query the agriculture knowledge base with optional location context."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG agent not initialized")
    
    try:
        # Process query with location context and enhanced features
        result = rag_agent.query(
            user_query=request.query,
            district=request.district,
            lat=request.latitude,
            lon=request.longitude,
            include_translations=True
        )
        
        # Extract confidence from citations
        confidence = None
        if result.get('citations'):
            confidence = result['citations'].get('confidence')
        
        return QueryResponse(
            query=result['query'],
            response=result['response'],
            sources=result.get('sources', []),
            tool_used=result['tool_used'],
            geo_context=result.get('geo_context'),
            citations=result.get('citations'),
            translations=result.get('translations'),
            confidence=confidence,
            reconciliation=result.get('reconciliation')
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle multi-turn chat conversations with optional location context."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG agent not initialized")
    
    try:
        # Convert Pydantic models to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get response with location context
        response = rag_agent.chat(
            messages=messages,
            district=request.district,
            lat=request.latitude,
            lon=request.longitude
        )
        
        return {
            "response": response,
            "role": "assistant"
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
async def get_categories():
    """Get available document categories."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    stats = vector_store.get_stats()
    return {
        "categories": stats.get('categories', []),
        "total_documents": stats['total_documents']
    }


@app.get("/search")
async def search(q: str, category: Optional[str] = None, top_k: int = 5):
    """Direct semantic search endpoint."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        filter_meta = {'category': category} if category else None
        
        results = vector_store.search_with_score_threshold(
            query=q,
            top_k=top_k,
            score_threshold=0.5,
            filter_metadata=filter_meta
        )
        
        return {
            "query": q,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/districts")
async def get_districts():
    """Get all available districts with their geographic information."""
    if geo_context is None:
        raise HTTPException(status_code=503, detail="Geographic context not initialized")
    
    try:
        districts = []
        for district_name in geo_context.get_all_districts():
            district_info = geo_context.get_district_by_name(district_name)
            if district_info:
                districts.append({
                    'name': district_info['name'],
                    'province': district_info['province'],
                    'region': district_info['region'],
                    'rainfall': district_info['rainfall'],
                    'soil_type': district_info['soil_type']
                })
        
        return {
            "total": len(districts),
            "districts": districts
        }
        
    except Exception as e:
        logger.error(f"Error fetching districts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/district/{district_name}")
async def get_district_info(district_name: str):
    """Get detailed information for a specific district."""
    if geo_context is None:
        raise HTTPException(status_code=503, detail="Geographic context not initialized")
    
    try:
        district_info = geo_context.get_district_by_name(district_name)
        
        if not district_info:
            raise HTTPException(status_code=404, detail=f"District '{district_name}' not found")
        
        context = geo_context.format_context(district_info)
        
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching district info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/{district_name}")
async def get_district_weather(district_name: str):
    """Get current weather and forecast for a district."""
    if geo_context is None or weather_api is None:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        district_info = geo_context.get_district_by_name(district_name)
        
        if not district_info:
            raise HTTPException(status_code=404, detail=f"District '{district_name}' not found")
        
        coords = district_info['coordinates']
        weather_data = await weather_api.get_agricultural_summary(coords['lat'], coords['lon'])
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        return {
            'district': district_info['name'],
            'coordinates': coords,
            'weather': weather_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/coordinates/{lat}/{lon}")
async def get_coordinates_weather(lat: float, lon: float):
    """Get current weather and forecast for specific coordinates."""
    if weather_api is None:
        raise HTTPException(status_code=503, detail="Weather service not initialized")
    
    try:
        weather_data = await weather_api.get_agricultural_summary(lat, lon)
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        return {
            'coordinates': {'latitude': lat, 'longitude': lon},
            'weather': weather_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets")
async def get_all_markets():
    """Get list of all markets with pricing data."""
    if market_api is None:
        raise HTTPException(status_code=503, detail="Market service not initialized")
    
    try:
        return market_api.get_all_markets()
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets/{district_name}")
async def get_district_market_prices(district_name: str):
    """Get market prices for a district."""
    if market_api is None:
        raise HTTPException(status_code=503, detail="Market service not initialized")
    
    try:
        prices = market_api.get_district_prices(district_name)
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No market data for {district_name}")
        
        return prices
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets/commodity/{commodity_name}")
async def get_commodity_comparison(commodity_name: str):
    """Compare prices for a commodity across all markets."""
    if market_api is None:
        raise HTTPException(status_code=503, detail="Market service not initialized")
    
    try:
        return market_api.get_commodity_comparison(commodity_name)
    except Exception as e:
        logger.error(f"Error comparing commodity prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets/trends")
async def get_price_trends():
    """Get price trends for all commodities."""
    if market_api is None:
        raise HTTPException(status_code=503, detail="Market service not initialized")
    
    try:
        return market_api.get_price_trends()
    except Exception as e:
        logger.error(f"Error fetching price trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=config['api']['host'],
        port=config['api']['port'],
        reload=config['api']['reload']
    )
