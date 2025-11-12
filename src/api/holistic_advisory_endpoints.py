"""
Holistic Advisory API Endpoints
Integrates district context, profitability analysis, and adaptive recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
import logging

from src.district.district_context import DistrictContextEngine
from src.profitability.margin_calculator import GrossMarginCalculator
from src.recommendations.adaptive_engine import AdaptiveRecommendationEngine

logger = logging.getLogger(__name__)

# Initialize engines
district_engine = DistrictContextEngine()
margin_calculator = GrossMarginCalculator()
recommendation_engine = AdaptiveRecommendationEngine()

router = APIRouter(prefix="/advisory", tags=["holistic-advisory"])


@router.get("/districts")
async def list_districts():
    """List all available districts."""
    try:
        districts = district_engine.list_all_districts()
        return {
            "districts": districts,
            "count": len(districts)
        }
    except Exception as e:
        logger.error(f"Error listing districts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/district/{district}")
async def get_district_overview(district: str):
    """Get comprehensive overview for a district."""
    try:
        overview = district_engine.get_district_overview(district)
        if "error" in overview:
            raise HTTPException(status_code=404, detail=overview["error"])
        return overview
    except Exception as e:
        logger.error(f"Error getting district overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/district/{district}/cited")
async def get_district_cited(district: str):
    """Get district data with full citations and evidence."""
    try:
        # Get cited data
        cited_data = district_engine.district_cited_data.get(district)
        if not cited_data:
            raise HTTPException(status_code=404, detail=f"No cited data for district {district}")
        
        # Get evidence
        evidence = district_engine.district_evidence.get(district, {})
        
        # Combine into response
        return {
            "district": cited_data.get('name'),
            "rainfall": cited_data.get('rainfall'),
            "soil_types": cited_data.get('soil_types'),
            "crops": cited_data.get('crops'),
            "markets": cited_data.get('markets'),
            "population": cited_data.get('population'),
            "metadata": cited_data.get('extraction_metadata'),
            "citations": evidence.get('extractions', []),
            "pdf_source": evidence.get('pdf'),
            "total_citations": len(evidence.get('extractions', []))
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cited district data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/district/{district}/viable-crops")
async def get_viable_crops(district: str):
    """Get viable crop recommendations for a district."""
    try:
        viable = district_engine.get_viable_crops(district)
        if not viable:
            raise HTTPException(status_code=404, detail=f"No data for district {district}")
        return {
            "district": district,
            "viable_crops": viable
        }
    except Exception as e:
        logger.error(f"Error getting viable crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/margin/{crop}/{district}")
async def get_margin_analysis(
    crop: str,
    district: str,
    yield_per_ha: Optional[float] = Query(None, description="Override yield in tonnes/ha"),
    price_per_tonne: Optional[float] = Query(None, description="Override price in ZWL")
):
    """Get gross margin analysis for a crop in a district."""
    try:
        margin = margin_calculator.calculate_margin(
            crop=crop,
            district=district,
            yield_tonnes_per_ha=yield_per_ha,
            price_per_tonne=price_per_tonne
        )
        return margin.to_dict()
    except Exception as e:
        logger.error(f"Error calculating margin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-crops/{district}")
async def compare_crops(district: str, crops: List[str]):
    """Compare margins across multiple crops in a district."""
    try:
        if not crops:
            raise HTTPException(status_code=400, detail="No crops provided")
        
        comparison = margin_calculator.compare_crops(district, crops)
        return {
            "district": district,
            "comparison": comparison,
            "best_crop": comparison[0] if comparison else None
        }
    except Exception as e:
        logger.error(f"Error comparing crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakeven/{crop}/{district}")
async def get_breakeven(crop: str, district: str):
    """Get breakeven analysis for a crop in a district."""
    try:
        analysis = margin_calculator.get_breakeven_analysis(crop, district)
        return analysis
    except Exception as e:
        logger.error(f"Error getting breakeven analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/{crop}")
async def get_cost_breakdown(crop: str):
    """Get detailed cost breakdown for a crop."""
    try:
        breakdown = margin_calculator.get_cost_breakdown(crop)
        return breakdown
    except Exception as e:
        logger.error(f"Error getting cost breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/{crop}/{district}")
async def scenario_analysis(crop: str, district: str, scenarios: List[Dict]):
    """Analyze different yield/price scenarios."""
    try:
        results = margin_calculator.scenario_analysis(crop, district, scenarios)
        return {
            "crop": crop,
            "district": district,
            "scenarios": results
        }
    except Exception as e:
        logger.error(f"Error running scenario analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/holistic/{crop}/{district}")
async def get_holistic_advisory(crop: str, district: str):
    """
    Get comprehensive holistic advisory covering:
    - What to plant and why
    - Costs and profitability
    - Market opportunities
    - Challenges and mitigation
    - Alternative strategies
    - Supply chain options
    - Nearby city opportunities
    """
    try:
        # Get all required data
        overview = district_engine.get_district_overview(district)
        if "error" in overview:
            raise HTTPException(status_code=404, detail=overview["error"])
        
        market_info = district_engine.get_market_recommendations(district, crop)
        difficulty = district_engine.get_difficulty_assessment(district)
        margin_info = margin_calculator.calculate_margin(crop, district).to_dict()
        
        # Generate holistic advisory
        advisory = recommendation_engine.generate_holistic_advisory(
            crop=crop,
            district=district,
            difficulty_level=difficulty.get("difficulty_level", "low"),
            challenges=difficulty.get("primary_challenges", []),
            market_info=market_info,
            margin_info=margin_info
        )
        
        return advisory
    except Exception as e:
        logger.error(f"Error generating holistic advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advisory-summary/{crop}/{district}")
async def get_advisory_summary(crop: str, district: str):
    """Get a brief advisory summary (short version of holistic advisory)."""
    try:
        holistic = await get_holistic_advisory(crop, district)
        
        # Extract key points for summary
        summary = {
            "district": district,
            "crop": crop,
            "recommendation": holistic.get("holistic_assessment"),
            "viability_score": holistic.get("viability_score"),
            "profitability": holistic["costs_and_profitability"].get("recommendation"),
            "gross_margin": holistic["costs_and_profitability"].get("gross_margin"),
            "key_challenges": holistic.get("key_challenges", [])[:3],  # Top 3
            "top_mitigation": holistic.get("mitigation_strategies", [])[:2],  # Top 2
            "investment_level": holistic.get("investment_requirement"),
            "expected_return": holistic.get("expected_return")
        }
        
        return summary
    except Exception as e:
        logger.error(f"Error generating advisory summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/{district}/{crop}")
async def get_market_strategy(district: str, crop: str):
    """Get market strategy and sales recommendations for a crop in a district."""
    try:
        market_info = district_engine.get_market_recommendations(district, crop)
        difficulty = district_engine.get_difficulty_assessment(district)
        supply_chain = recommendation_engine._get_supply_chain_options(district, market_info)
        nearby = recommendation_engine._get_nearby_city_opportunities(district)
        
        return {
            "district": district,
            "crop": crop,
            "local_market_info": market_info,
            "supply_chain_options": supply_chain,
            "nearby_city_opportunities": nearby
        }
    except Exception as e:
        logger.error(f"Error getting market strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/difficulty/{district}")
async def get_difficulty_assessment(district: str):
    """Get farming difficulty assessment for a district."""
    try:
        assessment = district_engine.get_difficulty_assessment(district)
        return assessment
    except Exception as e:
        logger.error(f"Error getting difficulty assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasonal-calendar/{district}")
async def get_seasonal_calendar(district: str):
    """Get seasonal farming calendar for a district."""
    try:
        calendar = district_engine.get_seasonal_calendar(district)
        return calendar
    except Exception as e:
        logger.error(f"Error getting seasonal calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nearby-districts/{district}")
async def get_nearby_districts(district: str):
    """Get nearby districts for supply chain optimization."""
    try:
        nearby = district_engine.get_nearby_districts(district)
        return {
            "district": district,
            "nearby_districts": nearby
        }
    except Exception as e:
        logger.error(f"Error getting nearby districts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch query endpoint
@router.post("/batch-advisory")
async def get_batch_advisory(queries: List[Dict]):
    """
    Process multiple advisory queries at once.
    
    Expected format:
    [
        {"crop": "maize", "district": "Harare"},
        {"crop": "millet", "district": "Binga"}
    ]
    """
    try:
        results = []
        
        for query in queries:
            crop = query.get("crop")
            district = query.get("district")
            
            if not crop or not district:
                results.append({
                    "crop": crop,
                    "district": district,
                    "error": "Missing crop or district"
                })
                continue
            
            try:
                advisory = await get_holistic_advisory(crop, district)
                results.append(advisory)
            except Exception as e:
                results.append({
                    "crop": crop,
                    "district": district,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "count": len(results),
            "successful": len([r for r in results if "error" not in r])
        }
    except Exception as e:
        logger.error(f"Error processing batch advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def add_holistic_advisory_endpoints(app):
    """Add holistic advisory endpoints to the FastAPI app."""
    app.include_router(router)
