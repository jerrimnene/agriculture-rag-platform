"""
Complete District Profile Endpoints
Provides comprehensive district information including profiles, markets, crops, and profitability
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging

from src.embeddings.vector_store import VectorStore
from src.geo.geo_context import GeoContext
from src.profitability.margin_calculator import GrossMarginCalculator
from src.markets.market_api import MarketPricesAPI

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/districts-complete", tags=["district-profiles"])


def add_complete_district_endpoints(app, vector_store: VectorStore):
    """
    Add comprehensive district profile endpoints to the FastAPI app.
    
    Provides:
    - Complete district profile (all data in one response)
    - District-specific Q&A
    - Market information per district
    - Profitability calculations per district
    - Crop recommendations per district
    """
    from src.agents.rag_agent import AgricultureRAGAgent
    import yaml
    from pathlib import Path
    
    # Load config for RAG agent
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    geo_context = GeoContext()
    margin_calc = GrossMarginCalculator()
    market_api = MarketPricesAPI()
    rag_agent = AgricultureRAGAgent(
        vector_store=vector_store,
        llm_model=config['llm']['model'],
        llm_base_url=config['llm']['base_url']
    )
    
    @app.get("/api/district/{district_name}/complete-profile")
    async def get_complete_district_profile(district_name: str):
        """
        Get COMPLETE district profile with ALL available information:
        - Basic information (province, natural region, rainfall, population)
        - Agricultural profile (main crops, yields, soil types)
        - Market information (local markets, prices, where to sell)
        - Irrigation schemes
        - Challenges and opportunities
        - Profitability estimates for main crops
        - Weather data
        """
        try:
            # 1. Get geographic context
            district_info = geo_context.get_district_by_name(district_name)
            if not district_info:
                raise HTTPException(status_code=404, detail=f"District '{district_name}' not found")
            
            # 2. Search vector database for district profile data
            profile_query = f"{district_name} district profile agriculture crops markets irrigation opportunities challenges"
            profile_results = vector_store.search(
                query=profile_query,
                top_k=10,
                filter_metadata={'source': 'zimbabwe_district_profiles'}
            )
            
            # Extract comprehensive profile information
            profile_text = ""
            for result in profile_results[:5]:
                profile_text += result['content'] + "\n\n"
            
            # Parse profile text to extract key information
            def parse_district_profile(text):
                """Extract structured data from district profile text"""
                import re
                
                crops = []
                challenges = []
                opportunities = []
                
                # Extract crops from Enterprise section
                enterprise_match = re.search(r'\*\*Enterprise:\*\*\s*([^\n]+)', text)
                if enterprise_match:
                    crop_text = enterprise_match.group(1)
                    # Extract crop names (remove descriptive text)
                    crop_parts = crop_text.split(';')
                    for part in crop_parts:
                        # Get main nouns/crops
                        words = part.replace(',', ' ').split()
                        for word in words:
                            word = word.strip('.')
                            if len(word) > 3 and word.lower() not in ['high', 'value', 'allow', 'dairy']:
                                if not any(char.isdigit() for char in word):
                                    crops.append(word.lower())
                
                # Extract challenges
                challenges_match = re.search(r'\*\*Challenges:\*\*\s*([^\n]+)', text)
                if challenges_match:
                    chal_text = challenges_match.group(1)
                    challenges = [c.strip() for c in chal_text.split(';') if c.strip()]
                
                # Extract opportunities  
                opps_match = re.search(r'\*\*Opportunities:\*\*\s*([^\n]+)', text)
                if opps_match:
                    opp_text = opps_match.group(1)
                    opportunities = [o.strip() for o in opp_text.split(';') if o.strip()]
                
                return {
                    'main_crops': crops[:6] if crops else [],  # Top 6 crops
                    'main_challenges': challenges[:4] if challenges else [],  # Top 4 challenges
                    'opportunities': opportunities[:3] if opportunities else []  # Top 3 opportunities
                }
            
            parsed_profile = parse_district_profile(profile_text)
            
            # 3. Get market information
            try:
                market_data = market_api.get_district_prices(district_name)
            except:
                market_data = {"markets": [], "note": "No market data available"}
            
            # 4. Get all markets in the system
            try:
                all_markets = market_api.get_all_markets()
                district_markets = [m for m in all_markets.get('markets', []) 
                                  if district_name.lower() in m.get('location', '').lower()]
            except:
                district_markets = []
            
            # 5. Calculate profitability for main crops
            # Use parsed crops if available, otherwise use defaults
            main_crops_to_calc = parsed_profile.get('main_crops', [])[:3] if parsed_profile.get('main_crops') else ['maize', 'sorghum', 'groundnuts', 'cotton']
            # Add common crops for comparison
            main_crops_to_calc.extend(['maize', 'tobacco', 'cotton'])
            main_crops_to_calc = list(set(main_crops_to_calc))  # Remove duplicates
            
            profitability_data = []
            
            for crop in main_crops_to_calc:
                try:
                    margin = margin_calc.calculate_margin(crop, district_name)
                    profitability_data.append({
                        'crop': crop,
                        'gross_margin': round(margin.gross_margin, 2),
                        'profit_margin_percentage': round(margin.profit_margin_percentage, 2),
                        'expected_yield': margin.yield_tonnes_per_ha
                    })
                except:
                    pass
            
            # Sort by gross margin
            profitability_data.sort(key=lambda x: x.get('gross_margin', 0), reverse=True)
            
            # Determine best crop for display
            # For specialty crop districts (Region I/II), use actual main crop instead of calculator
            best_crop_calc = profitability_data[0]['crop'] if profitability_data else "Data pending"
            main_crops_list = parsed_profile.get('main_crops', [])
            # If first crop is specialty (not in basic calculator), use it
            if main_crops_list and main_crops_list[0] not in ['maize', 'sorghum', 'groundnuts', 'cotton', 'tobacco']:
                best_crop_display = main_crops_list[0]
            else:
                best_crop_display = best_crop_calc
            
            # 6. Compile complete response
            response = {
                "district": district_name,
                "status": "complete_profile",
                
                # Geographic Information
                "geographic_info": {
                    "province": district_info.get('province'),
                    "natural_region": district_info.get('region'),
                    "rainfall_mm": district_info.get('rainfall'),
                    "soil_type": district_info.get('soil_type'),
                    "coordinates": district_info.get('coordinates', {}),
                    "altitude": district_info.get('altitude')
                },
                
                # Comprehensive Profile (from new district profile data)
                "agricultural_profile": {
                    "profile_text": profile_text[:2000] if profile_text else "Profile data being compiled...",
                    "source_count": len(profile_results),
                    "data_sources": [r.get('metadata', {}).get('source') for r in profile_results[:3]]
                },
                
                # Market Information
                "markets": {
                    "local_markets": district_markets,
                    "nearby_selling_points": market_data.get('markets', []),
                    "market_count": len(district_markets),
                    "price_data": market_data
                },
                
                # Where to Sell Produce
                "selling_locations": {
                    "local": [
                        f"{district_name} local market",
                        f"{district_name} growth point",
                        f"{district_name} service centre"
                    ],
                    "regional": [
                        f"{district_info.get('province')} provincial markets",
                        "GMB (Grain Marketing Board) depots",
                        "Contract farming off-takers"
                    ],
                    "national": [
                        "Mbare Musika (Harare)",
                        "Bulawayo markets",
                        "Export markets via Zimbabwe Trade (ZimTrade)"
                    ]
                },
                
                # Profitability Analysis
                "profitability": {
                    "top_crops_by_profit": profitability_data,
                    "note": "Gross margin calculations based on current prices and typical yields"
                },
                
                # Quick Facts
                "quick_facts": {
                    "best_crop_for_profit": best_crop_display,
                    "main_crops": main_crops_list,
                    "main_challenges": parsed_profile.get('main_challenges', []),
                    "opportunities": parsed_profile.get('opportunities', [])
                }
            }
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting complete district profile: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/api/district/{district_name}/ask")
    async def ask_district_question(district_name: str, question: str):
        """
        Ask any question about a specific district.
        All answers are contextualized to the district using RAG agent.
        
        Examples:
        - "What crops grow here?"
        - "Where can I sell my maize?"
        - "What are the main challenges?"
        - "Which crop is most profitable?"
        - "When do we plant maize?"
        """
        try:
            # Use RAG agent to get proper answer with district context
            contextualized_query = f"For {district_name} district in Zimbabwe: {question}"
            
            result = rag_agent.query(
                user_query=contextualized_query,
                district=district_name
            )
            
            # Format sources with full metadata
            sources = []
            for source in result.get('sources', [])[:5]:
                metadata = source.get('metadata', {})
                sources.append({
                    'content': source.get('content', '')[:200],
                    'metadata': {
                        'category': metadata.get('category', 'general'),
                        'district': metadata.get('district', district_name),
                        'source': metadata.get('source', 'Unknown'),
                        'source_file': metadata.get('source_file', ''),
                        'url': metadata.get('url', '')
                    }
                })
            
            return {
                "district": district_name,
                "question": question,
                "answer": result.get('response', 'No answer available'),
                "sources": sources,
                "source_count": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error answering district question: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/api/district/{district_name}/markets")
    async def get_district_markets_complete(district_name: str):
        """
        Get comprehensive market information for a district including:
        - Local markets
        - Nearby selling points
        - Current prices
        - Export opportunities
        - Contract farming opportunities
        """
        try:
            # Get market data
            try:
                market_data = market_api.get_district_prices(district_name)
            except:
                market_data = {}
            
            # Get district info for province
            district_info = geo_context.get_district_by_name(district_name)
            province = district_info.get('province', 'Unknown') if district_info else 'Unknown'
            
            return {
                "district": district_name,
                "province": province,
                
                # Local Markets
                "local_markets": {
                    "growth_points": [f"{district_name} Growth Point"],
                    "service_centres": [f"{district_name} Service Centre"],
                    "weekly_markets": [f"{district_name} Weekly Market (check local schedule)"]
                },
                
                # Commodity Prices
                "current_prices": market_data.get('prices', {}),
                
                # Where to Sell
                "selling_options": {
                    "local": {
                        "description": "Sell directly in your district",
                        "locations": [
                            f"{district_name} local market",
                            f"{district_name} growth point traders",
                            "Local agro-dealers and shops"
                        ],
                        "advantages": ["Lower transport cost", "Immediate payment", "Know your buyers"]
                    },
                    "regional": {
                        "description": "Sell in nearby towns or provincial centers",
                        "locations": [
                            f"{province} provincial markets",
                            "GMB (Grain Marketing Board) depots",
                            "Cold Storage Commission (livestock)"
                        ],
                        "advantages": ["Higher prices", "Larger volumes", "Quality grading"]
                    },
                    "national": {
                        "description": "Access national and export markets",
                        "locations": [
                            "Mbare Musika (Harare)",
                            "Bulawayo markets",
                            "Zimbabwe Mercantile Exchange (ZMX)",
                            "Tobacco auction floors",
                            "Cotton ginneries"
                        ],
                        "advantages": ["Best prices", "Export opportunities", "Contract farming"]
                    },
                    "contract_farming": {
                        "description": "Pre-arranged buyers for your produce",
                        "options": [
                            "Tobacco: TSL, Tian-Ze, BAT",
                            "Cotton: Cottco, Cargill",
                            "Soya: Oil expressers",
                            "Horticulture: Export pack-houses"
                        ],
                        "advantages": ["Guaranteed market", "Input financing", "Technical support"]
                    }
                },
                
                # Transport Options
                "transport_tips": [
                    "Group produce with other farmers to reduce cost",
                    "Use GMB trucks when available",
                    "Check for transport subsidies from agricultural programs",
                    "Consider storage to sell when prices are better"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting district markets: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/api/district/{district_name}/profitability-comparison")
    async def compare_district_profitability(
        district_name: str,
        crops: Optional[List[str]] = None
    ):
        """
        Compare profitability of different crops in a specific district.
        Shows which crops are most profitable to grow.
        """
        try:
            if not crops:
                crops = ['maize', 'sorghum', 'groundnuts', 'cotton', 'tobacco', 'soya']
            
            comparison = []
            
            for crop in crops:
                try:
                    margin = margin_calc.calculate_margin(crop, district_name)
                    comparison.append({
                        'crop': crop,
                        'gross_margin_per_ha': round(margin.gross_margin, 2),
                        'profit_margin_percentage': round(margin.profit_margin_percentage, 2),
                        'expected_yield_tonnes_per_ha': margin.yield_tonnes_per_ha,
                        'gross_income_per_ha': round(margin.gross_income, 2),
                        'total_costs_per_ha': round(margin.total_variable_costs, 2),
                        'recommendation': "Highly Profitable" if margin.profit_margin_percentage > 50 else 
                                        "Moderately Profitable" if margin.profit_margin_percentage > 30 else
                                        "Low Profitability"
                    })
                except Exception as e:
                    logger.warning(f"Could not calculate margin for {crop} in {district_name}: {e}")
            
            # Sort by gross margin
            comparison.sort(key=lambda x: x['gross_margin_per_ha'], reverse=True)
            
            return {
                "district": district_name,
                "analysis_date": "Current prices and yields",
                "crops_analyzed": len(comparison),
                "profitability_ranking": comparison,
                "top_recommendation": comparison[0] if comparison else None,
                "note": "Profitability varies with market prices, input costs, and actual yields. Use this as a guide."
            }
            
        except Exception as e:
            logger.error(f"Error comparing profitability: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info("✓ Complete district profile endpoints registered")
