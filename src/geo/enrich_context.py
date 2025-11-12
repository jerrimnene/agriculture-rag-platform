"""
Context enrichment module for AgriEvidence.
Merges geographic data into prompts and queries for location-aware responses.
"""

from typing import Dict, Optional, List
from .geo_context import GeoContext


class ContextEnricher:
    """Enriches queries and prompts with geographic context."""
    
    def __init__(self):
        """Initialize the context enricher with geo data."""
        self.geo = GeoContext()
    
    def build_agrievidence_prompt(
        self,
        question: str,
        retrieved_chunks: List[Dict],
        district: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> str:
        """
        Build the AgriEvidence prompt with location context.
        
        Args:
            question: User's question
            retrieved_chunks: List of retrieved document chunks from RAG
            district: District name (optional)
            lat: Latitude (optional)
            lon: Longitude (optional)
            
        Returns:
            Complete prompt string with context
        """
        # Get geographic context
        geo_context = self._get_geo_context(district, lat, lon)
        
        # Format retrieved evidence
        evidence_text = self._format_evidence(retrieved_chunks)
        
        # Build location context string
        location_str = self._format_location_context(geo_context)
        
        # Build the prompt
        prompt = f"""You are AgriEvidence, Zimbabwe's national agricultural intelligence assistant.
You use verified research, manuals, and reports to answer farming questions.

[INSTRUCTIONS]
1. Tailor all recommendations to the user's district, province, and natural region.
2. For planting times, ALWAYS use the specific "Maize Planting Window" provided in the location context if available.
3. Do NOT suggest year-round planting for annual crops like maize - follow Zimbabwe's seasonal rainfall patterns.
4. Cite all answers with (Source, Page) format.
5. If available, include document references.
6. If data is general, clearly say: "This is a national-level recommendation; local conditions may vary."
7. Never invent data. Use only verified context or sources.

[CONTEXT EVIDENCE]
{evidence_text}

[LOCATION CONTEXT]
{location_str}

[USER QUESTION]
{question}

Please provide a location-specific answer with proper citations."""
        
        return prompt
    
    def enrich_query_metadata(
        self,
        query: str,
        district: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Enrich query with geographic metadata for filtering.
        
        Args:
            query: Search query
            district: District name (optional)
            lat: Latitude (optional)
            lon: Longitude (optional)
            
        Returns:
            Dictionary with query and metadata
        """
        geo_context = self._get_geo_context(district, lat, lon)
        
        metadata = {
            'query': query,
            'original_query': query
        }
        
        if geo_context:
            metadata['geo_context'] = geo_context
            # Enhance query with location terms for better retrieval
            metadata['query'] = self._enhance_query_with_location(query, geo_context)
        
        return metadata
    
    def _get_geo_context(
        self,
        district: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Optional[Dict]:
        """Get geographic context from district name or coordinates."""
        if district:
            district_info = self.geo.get_district_by_name(district)
            if district_info:
                return self.geo.format_context(district_info)
        elif lat is not None and lon is not None:
            district_info = self.geo.get_district_by_coordinates(lat, lon)
            if district_info:
                return self.geo.format_context(district_info)
        
        return None
    
    def _format_location_context(self, geo_context: Optional[Dict]) -> str:
        """Format geographic context for prompt injection."""
        if not geo_context:
            return "Location: Not specified (providing national-level guidance)"
        
        lines = [
            f"District: {geo_context['district']}, Province: {geo_context['province']}, Region: {geo_context['region']}",
            f"Rainfall: {geo_context['rainfall']} | Soil: {geo_context['soil_type']} | Market: {geo_context['nearest_market']}"
        ]
        
        if 'region_description' in geo_context:
            lines.append(f"Region Type: {geo_context['region_description']}")
        
        if 'recommended_crops' in geo_context:
            crops = ', '.join(geo_context['recommended_crops'])
            lines.append(f"Recommended Crops for Region: {crops}")
        
        if 'growing_season' in geo_context:
            lines.append(f"Growing Season: {geo_context['growing_season']}")
        
        if 'maize_planting_window' in geo_context:
            lines.append(f"Maize Planting Window: {geo_context['maize_planting_window']}")
        
        return '\n'.join(lines)
    
    def _format_evidence(self, retrieved_chunks: List[Dict]) -> str:
        """Format retrieved document chunks as evidence."""
        if not retrieved_chunks:
            return "No specific documents retrieved."
        
        evidence_lines = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get('metadata', {}).get('source', 'Unknown')
            page = chunk.get('metadata', {}).get('page', 'N/A')
            content = chunk.get('content', chunk.get('text', ''))
            
            evidence_lines.append(f"[Source {i}] {source} (Page {page})")
            evidence_lines.append(content)
            evidence_lines.append("")  # Blank line between sources
        
        return '\n'.join(evidence_lines)
    
    def _enhance_query_with_location(self, query: str, geo_context: Dict) -> str:
        """
        Enhance search query with location-specific terms.
        
        This helps retrieve more relevant documents for the specific region.
        """
        region = geo_context.get('region', '')
        district = geo_context.get('district', '')
        
        # Add region type to query for better matching
        enhanced = f"{query} {region} {district}"
        
        return enhanced.strip()


# Convenience function
def enrich_query_context(
    question: str,
    retrieved_chunks: List[Dict],
    district: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> str:
    """
    Convenience function to build enriched prompt.
    
    Args:
        question: User's question
        retrieved_chunks: Retrieved document chunks
        district: District name (optional)
        lat: Latitude (optional)
        lon: Longitude (optional)
        
    Returns:
        Complete enriched prompt
    """
    enricher = ContextEnricher()
    return enricher.build_agrievidence_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
        district=district,
        lat=lat,
        lon=lon
    )
