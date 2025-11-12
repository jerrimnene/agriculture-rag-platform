"""
Enhanced Citation Engine for Agriculture RAG Platform
Provides proper source attribution with organization names, document titles, and PDF links
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationEngine:
    """Manages citations with enhanced metadata and confidence scoring."""
    
    # Organization mappings for better display
    ORGANIZATION_PATTERNS = {
        'ICRISAT': ['icrisat', 'international crops research'],
        'FAO': ['fao', 'food and agriculture organization'],
        'World Bank': ['world bank', 'wb'],
        'USAID': ['usaid', 'us agency'],
        'IFAD': ['ifad', 'international fund'],
        'WFP': ['wfp', 'world food programme'],
        'CGIAR': ['cgiar', 'consultative group'],
        'AGRITEX': ['agritex', 'agricultural technical'],
        'AMA': ['ama', 'agricultural marketing authority'],
        'Zimbabwe Ministry': ['ministry', 'government of zimbabwe', 'govt'],
    }
    
    # Source quality tiers for confidence scoring
    SOURCE_QUALITY = {
        'tier1': ['icrisat', 'fao', 'world bank', 'cgiar', 'ifpri'],  # International research
        'tier2': ['usaid', 'ifad', 'wfp', 'agritex', 'ama'],  # Development agencies
        'tier3': ['ministry', 'local', 'farmer'],  # Local sources
    }
    
    def __init__(self):
        self.citations_cache = {}
    
    def extract_organization(self, filename: str, content: str = "") -> str:
        """Extract organization name from filename or content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check filename and content against patterns
        for org, patterns in self.ORGANIZATION_PATTERNS.items():
            for pattern in patterns:
                if pattern in filename_lower or pattern in content_lower:
                    return org
        
        return "Unknown Organization"
    
    def extract_document_title(self, filename: str, metadata: Dict) -> str:
        """Extract a readable document title."""
        # Remove file extension and clean up
        title = Path(filename).stem
        
        # Replace underscores and dashes with spaces
        title = title.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def get_pdf_link(self, filename: str, metadata: Dict) -> Optional[str]:
        """Generate or retrieve PDF link for the document."""
        # Check if metadata contains a URL
        if 'url' in metadata:
            return metadata['url']
        
        if 'source_path' in metadata:
            return f"file://{metadata['source_path']}"
        
        # If no direct link, return a placeholder
        return None
    
    def calculate_source_quality(self, organization: str, metadata: Dict) -> str:
        """Calculate source quality tier."""
        org_lower = organization.lower()
        
        for tier in ['tier1', 'tier2', 'tier3']:
            for source in self.SOURCE_QUALITY[tier]:
                if source in org_lower:
                    return tier
        
        return 'tier3'
    
    def calculate_confidence_score(
        self,
        sources: List[Dict],
        agreement_score: float = 0.8
    ) -> Dict:
        """
        Calculate confidence score for an answer based on:
        - Source quality (tier)
        - Number of sources
        - Recency of sources
        - Agreement between sources
        """
        if not sources:
            return {
                'score': 0.0,
                'rating': 'No Sources',
                'explanation': 'No sources found to support this answer.'
            }
        
        # Quality score (0-40 points)
        tier_scores = {'tier1': 40, 'tier2': 30, 'tier3': 20}
        quality_score = 0
        for source in sources:
            org = source.get('organization', '')
            tier = self.calculate_source_quality(org, source.get('metadata', {}))
            quality_score = max(quality_score, tier_scores[tier])
        
        # Quantity score (0-20 points)
        quantity_score = min(len(sources) * 5, 20)
        
        # Recency score (0-20 points) - placeholder, would need actual dates
        recency_score = 15  # Default moderate score
        
        # Agreement score (0-20 points)
        agreement_points = agreement_score * 20
        
        # Total score
        total_score = quality_score + quantity_score + recency_score + agreement_points
        total_score = min(total_score, 100)
        
        # Rating
        if total_score >= 80:
            rating = 'High Confidence'
            color = 'green'
        elif total_score >= 60:
            rating = 'Moderate Confidence'
            color = 'orange'
        else:
            rating = 'Low Confidence'
            color = 'red'
        
        # Explanation
        explanation = self._generate_confidence_explanation(
            len(sources), quality_score, agreement_score
        )
        
        return {
            'score': round(total_score, 1),
            'rating': rating,
            'color': color,
            'explanation': explanation,
            'breakdown': {
                'source_quality': quality_score,
                'number_of_sources': quantity_score,
                'recency': recency_score,
                'agreement': agreement_points
            }
        }
    
    def _generate_confidence_explanation(
        self,
        num_sources: int,
        quality_score: float,
        agreement_score: float
    ) -> str:
        """Generate human-readable explanation of confidence."""
        parts = []
        
        if quality_score >= 35:
            parts.append("high-quality international research organizations")
        elif quality_score >= 25:
            parts.append("reputable development agencies")
        else:
            parts.append("local sources")
        
        parts.append(f"{num_sources} source{'s' if num_sources != 1 else ''}")
        
        if agreement_score >= 0.8:
            parts.append("with strong agreement")
        elif agreement_score >= 0.6:
            parts.append("with moderate agreement")
        else:
            parts.append("with some variation")
        
        return f"Based on {parts[1]} from {parts[0]} {parts[2]}."
    
    def format_citations(
        self,
        sources: List[Dict],
        include_confidence: bool = True
    ) -> Dict:
        """
        Format citations with enhanced metadata.
        
        Returns:
            Dict with formatted citations and confidence score
        """
        formatted_sources = []
        
        for idx, source in enumerate(sources, 1):
            metadata = source.get('metadata', {})
            content = source.get('content', '')
            
            # Extract information
            filename = metadata.get('filename', 'Unknown Document')
            organization = self.extract_organization(filename, content)
            title = self.extract_document_title(filename, metadata)
            pdf_link = self.get_pdf_link(filename, metadata)
            page = metadata.get('page', None)
            
            # Create citation
            citation = {
                'number': idx,
                'organization': organization,
                'title': title,
                'filename': filename,
                'pdf_link': pdf_link,
                'page': page,
                'display': self._format_citation_display(
                    idx, organization, title, pdf_link, page
                ),
                'relevance_score': source.get('similarity_score', 0.0),
                'quality_tier': self.calculate_source_quality(organization, metadata)
            }
            
            formatted_sources.append(citation)
        
        result = {
            'sources': formatted_sources,
            'total_sources': len(formatted_sources)
        }
        
        # Add confidence score
        if include_confidence:
            result['confidence'] = self.calculate_confidence_score(sources)
        
        return result
    
    def _format_citation_display(
        self,
        number: int,
        organization: str,
        title: str,
        pdf_link: Optional[str],
        page: Optional[int]
    ) -> str:
        """Format citation for display."""
        citation = f"[{number}] {organization} – {title}"
        
        if page:
            citation += f" (p. {page})"
        
        if pdf_link:
            citation += f" [PDF: {pdf_link}]"
        
        return citation
    
    def generate_inline_citations(self, text: str, sources: List[Dict]) -> str:
        """Add inline citation numbers to text based on relevance."""
        # This is a simplified version - could be enhanced with NLP
        # to match specific statements to specific sources
        if not sources:
            return text
        
        # Add citation at the end for now
        citation_nums = [f"[{i}]" for i in range(1, len(sources) + 1)]
        return f"{text} {' '.join(citation_nums)}"


if __name__ == "__main__":
    # Test the citation engine
    engine = CitationEngine()
    
    # Mock sources
    test_sources = [
        {
            'content': 'Maize production guidelines...',
            'metadata': {
                'filename': 'ICRISAT_maize_production_2023.pdf',
                'page': 15,
                'source_path': '/path/to/doc.pdf'
            },
            'similarity_score': 0.92
        },
        {
            'content': 'FAO recommendations...',
            'metadata': {
                'filename': 'FAO_crop_protection_guide.pdf',
                'page': 42
            },
            'similarity_score': 0.85
        }
    ]
    
    result = engine.format_citations(test_sources)
    print("Formatted Citations:")
    for source in result['sources']:
        print(source['display'])
    
    print("\nConfidence Score:", result['confidence'])
