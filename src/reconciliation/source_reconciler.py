"""
Multi-Source Reconciliation System
Detects and reconciles conflicting recommendations from different agricultural sources
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceAuthority:
    """Defines authority levels for different source types."""
    
    # Authority scoring (0-100)
    AUTHORITY_SCORES = {
        # Tier 1: International Research (90-100)
        'icrisat': 95,
        'cgiar': 95,
        'fao': 90,
        'ifpri': 90,
        'world bank': 85,
        
        # Tier 2: Regional/National Research (70-85)
        'agritex': 85,  # Local extension = high authority for Zimbabwe
        'ama': 80,      # Agricultural Marketing Authority
        'timb': 80,     # Tobacco Board
        'university': 75,
        'research station': 75,
        
        # Tier 3: Development Agencies (60-75)
        'usaid': 70,
        'ifad': 70,
        'wfp': 65,
        
        # Tier 4: Other (40-60)
        'ngo': 50,
        'farmer group': 45,
        'commercial': 40,
    }
    
    # Geographic specificity bonus
    GEOGRAPHIC_BONUS = {
        'zimbabwe': 20,
        'southern africa': 15,
        'sadc': 15,
        'africa': 10,
        'sub-saharan africa': 10,
        'global': 0
    }
    
    # Recency bonus (years old)
    RECENCY_BONUS = {
        0: 15,   # Current year
        1: 12,   # 1 year old
        2: 8,    # 2 years old
        3: 5,    # 3 years old
        4: 2,    # 4 years old
        5: 0,    # 5+ years old
    }
    
    @classmethod
    def calculate_authority(
        cls,
        organization: str,
        geographic_scope: Optional[str] = None,
        year: Optional[int] = None
    ) -> int:
        """Calculate total authority score for a source."""
        # Base authority
        org_lower = organization.lower()
        base_score = 40  # Default
        
        for key, score in cls.AUTHORITY_SCORES.items():
            if key in org_lower:
                base_score = score
                break
        
        # Geographic bonus
        geo_bonus = 0
        if geographic_scope:
            geo_lower = geographic_scope.lower()
            for key, bonus in cls.GEOGRAPHIC_BONUS.items():
                if key in geo_lower:
                    geo_bonus = bonus
                    break
        
        # Recency bonus
        recency_bonus = 0
        if year:
            current_year = datetime.now().year
            years_old = current_year - year
            recency_bonus = cls.RECENCY_BONUS.get(
                min(years_old, 5), 0
            )
        
        total = min(base_score + geo_bonus + recency_bonus, 100)
        return total


class RecommendationExtractor:
    """Extracts actionable recommendations from text."""
    
    # Recommendation patterns
    RECOMMENDATION_PATTERNS = [
        r'should\s+(\w+(?:\s+\w+){1,8})',
        r'recommended?\s+to\s+(\w+(?:\s+\w+){1,8})',
        r'advise[ds]?\s+to\s+(\w+(?:\s+\w+){1,8})',
        r'suggest[s]?\s+(\w+(?:\s+\w+){1,8})',
        r'plant(?:ing)?\s+(\w+(?:\s+\w+){1,5})\s+(?:in|during|between)',
        r'apply\s+(\w+(?:\s+\w+){1,5})',
        r'use\s+(\w+(?:\s+\w+){1,5})',
        r'avoid\s+(\w+(?:\s+\w+){1,5})',
        r'(?:do not|don\'t)\s+(\w+(?:\s+\w+){1,5})',
    ]
    
    # Topic keywords for categorization
    TOPIC_KEYWORDS = {
        'planting_time': ['plant', 'sow', 'seeding', 'planting time', 'planting window', 'planting season'],
        'fertilizer': ['fertilizer', 'fertiliser', 'nutrient', 'npk', 'manure', 'compost'],
        'pest_control': ['pest', 'disease', 'insect', 'fungus', 'spray', 'pesticide'],
        'irrigation': ['water', 'irrigation', 'rainfall', 'moisture', 'drip'],
        'variety': ['variety', 'cultivar', 'breed', 'hybrid', 'strain'],
        'spacing': ['spacing', 'density', 'population', 'plant per'],
        'harvest': ['harvest', 'reap', 'mature', 'maturity'],
        'storage': ['storage', 'store', 'preserve', 'keep'],
    }
    
    @classmethod
    def extract_recommendations(cls, text: str) -> List[Dict]:
        """Extract recommendations from text."""
        recommendations = []
        
        for pattern in cls.RECOMMENDATION_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rec_text = match.group(1).strip()
                
                # Categorize by topic
                topic = cls._categorize_recommendation(text, rec_text)
                
                recommendations.append({
                    'text': rec_text,
                    'topic': topic,
                    'context': match.group(0),
                    'full_sentence': cls._extract_sentence(text, match.start())
                })
        
        return recommendations
    
    @classmethod
    def _categorize_recommendation(cls, full_text: str, rec_text: str) -> str:
        """Categorize recommendation by topic."""
        combined = (full_text + " " + rec_text).lower()
        
        topic_scores = {}
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    @classmethod
    def _extract_sentence(cls, text: str, position: int) -> str:
        """Extract full sentence containing the match."""
        # Find sentence boundaries
        start = text.rfind('.', 0, position) + 1
        end = text.find('.', position)
        
        if end == -1:
            end = len(text)
        
        return text[start:end].strip()


class ConflictDetector:
    """Detects conflicts between recommendations."""
    
    # Conflict indicators
    CONFLICT_KEYWORDS = {
        'timing': ['before', 'after', 'early', 'late', 'november', 'december', 'october'],
        'quantity': ['more', 'less', 'increase', 'reduce', 'kg', 'litre', 'gram'],
        'method': ['spray', 'broadcast', 'band', 'foliar', 'drip', 'flood'],
        'negation': ['avoid', 'do not', 'don\'t', 'never', 'not recommended'],
    }
    
    @classmethod
    def detect_conflicts(
        cls,
        recommendations: List[Dict],
        threshold: float = 0.6
    ) -> List[Dict]:
        """Detect conflicting recommendations."""
        conflicts = []
        
        # Group by topic
        by_topic = defaultdict(list)
        for rec in recommendations:
            by_topic[rec['topic']].append(rec)
        
        # Check for conflicts within each topic
        for topic, recs in by_topic.items():
            if len(recs) < 2:
                continue
            
            for i, rec1 in enumerate(recs):
                for rec2 in recs[i+1:]:
                    similarity = cls._calculate_semantic_overlap(
                        rec1['text'], rec2['text']
                    )
                    
                    has_conflict = cls._has_conflicting_indicators(
                        rec1['full_sentence'], rec2['full_sentence']
                    )
                    
                    if similarity > threshold and has_conflict:
                        conflicts.append({
                            'topic': topic,
                            'recommendation_1': rec1,
                            'recommendation_2': rec2,
                            'conflict_type': cls._identify_conflict_type(
                                rec1['full_sentence'], rec2['full_sentence']
                            ),
                            'severity': 'high' if similarity > 0.8 else 'moderate'
                        })
        
        return conflicts
    
    @classmethod
    def _calculate_semantic_overlap(cls, text1: str, text2: str) -> float:
        """Calculate semantic overlap between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @classmethod
    def _has_conflicting_indicators(cls, sent1: str, sent2: str) -> bool:
        """Check if sentences have conflicting indicators."""
        s1_lower = sent1.lower()
        s2_lower = sent2.lower()
        
        # Check for timing conflicts
        if any(kw in s1_lower for kw in cls.CONFLICT_KEYWORDS['timing']):
            if any(kw in s2_lower for kw in cls.CONFLICT_KEYWORDS['timing']):
                # Both mention timing - might conflict
                return True
        
        # Check for negation conflicts
        negation_in_1 = any(kw in s1_lower for kw in cls.CONFLICT_KEYWORDS['negation'])
        negation_in_2 = any(kw in s2_lower for kw in cls.CONFLICT_KEYWORDS['negation'])
        
        if negation_in_1 != negation_in_2:
            # One says "do", other says "don't"
            return True
        
        # Check for quantity conflicts
        if 'more' in s1_lower and 'less' in s2_lower:
            return True
        if 'increase' in s1_lower and ('reduce' in s2_lower or 'decrease' in s2_lower):
            return True
        
        return False
    
    @classmethod
    def _identify_conflict_type(cls, sent1: str, sent2: str) -> str:
        """Identify the type of conflict."""
        s1 = sent1.lower()
        s2 = sent2.lower()
        
        if any(kw in s1 for kw in cls.CONFLICT_KEYWORDS['timing']):
            return 'timing'
        
        if any(kw in s1 for kw in cls.CONFLICT_KEYWORDS['quantity']):
            return 'quantity'
        
        if any(kw in s1 for kw in cls.CONFLICT_KEYWORDS['method']):
            return 'method'
        
        negation1 = any(kw in s1 for kw in cls.CONFLICT_KEYWORDS['negation'])
        negation2 = any(kw in s2 for kw in cls.CONFLICT_KEYWORDS['negation'])
        
        if negation1 != negation2:
            return 'recommendation_vs_warning'
        
        return 'general'


class SourceReconciler:
    """Main reconciliation engine."""
    
    def __init__(self):
        self.authority_calculator = SourceAuthority()
        self.extractor = RecommendationExtractor()
        self.conflict_detector = ConflictDetector()
    
    def reconcile_sources(
        self,
        sources: List[Dict],
        query: str
    ) -> Dict:
        """
        Reconcile potentially conflicting sources.
        
        Args:
            sources: List of source documents with metadata
            query: Original user query
            
        Returns:
            Reconciliation result with conflicts and recommendations
        """
        logger.info(f"Reconciling {len(sources)} sources for query: {query}")
        
        # Step 1: Extract recommendations from each source
        source_recommendations = []
        for source in sources:
            recs = self.extractor.extract_recommendations(source['content'])
            
            for rec in recs:
                rec['source'] = source['metadata'].get('filename', 'Unknown')
                rec['organization'] = source['metadata'].get('organization', 'Unknown')
                rec['authority_score'] = self.authority_calculator.calculate_authority(
                    organization=rec['organization'],
                    geographic_scope=source['metadata'].get('geographic_scope'),
                    year=source['metadata'].get('year')
                )
            
            source_recommendations.extend(recs)
        
        if not source_recommendations:
            return {
                'has_conflicts': False,
                'consensus_recommendations': [],
                'conflicts': [],
                'message': 'No specific recommendations extracted from sources'
            }
        
        # Step 2: Detect conflicts
        conflicts = self.conflict_detector.detect_conflicts(source_recommendations)
        
        # Step 3: Build consensus
        consensus = self._build_consensus(source_recommendations, conflicts)
        
        # Step 4: Format results
        result = {
            'has_conflicts': len(conflicts) > 0,
            'total_sources': len(sources),
            'total_recommendations': len(source_recommendations),
            'conflicts_found': len(conflicts),
            'consensus_recommendations': consensus,
            'conflicts': self._format_conflicts(conflicts),
            'summary': self._generate_summary(conflicts, consensus)
        }
        
        return result
    
    def _build_consensus(
        self,
        recommendations: List[Dict],
        conflicts: List[Dict]
    ) -> List[Dict]:
        """Build consensus recommendations."""
        # Group by topic
        by_topic = defaultdict(list)
        for rec in recommendations:
            by_topic[rec['topic']].append(rec)
        
        consensus = []
        
        for topic, recs in by_topic.items():
            if not recs:
                continue
            
            # Find if this topic has conflicts
            topic_conflicts = [c for c in conflicts if c['topic'] == topic]
            
            if not topic_conflicts:
                # No conflict - use highest authority source
                best_rec = max(recs, key=lambda r: r['authority_score'])
                consensus.append({
                    'topic': topic,
                    'recommendation': best_rec['full_sentence'],
                    'source': best_rec['source'],
                    'authority_score': best_rec['authority_score'],
                    'confidence': 'high',
                    'supporting_sources': len(recs)
                })
            else:
                # Has conflict - provide balanced view
                # Sort by authority
                sorted_recs = sorted(recs, key=lambda r: r['authority_score'], reverse=True)
                top_2 = sorted_recs[:2]
                
                consensus.append({
                    'topic': topic,
                    'recommendation': self._create_balanced_recommendation(top_2),
                    'source': f"Synthesized from {len(top_2)} sources",
                    'authority_score': sum(r['authority_score'] for r in top_2) / len(top_2),
                    'confidence': 'moderate',
                    'supporting_sources': len(recs),
                    'note': f"Sources disagree on {topic}. Recommendation based on highest authority sources."
                })
        
        return sorted(consensus, key=lambda c: c['authority_score'], reverse=True)
    
    def _create_balanced_recommendation(self, recommendations: List[Dict]) -> str:
        """Create a balanced recommendation from conflicting sources."""
        if len(recommendations) == 0:
            return "Insufficient data for recommendation"
        
        if len(recommendations) == 1:
            return recommendations[0]['full_sentence']
        
        # Prioritize higher authority, but acknowledge alternative
        primary = recommendations[0]
        secondary = recommendations[1]
        
        balanced = (
            f"{primary['source']} (authority: {primary['authority_score']}) recommends: "
            f"{primary['text']}. However, {secondary['source']} suggests: {secondary['text']}. "
            f"Consider local conditions and consult extension services for your specific situation."
        )
        
        return balanced
    
    def _format_conflicts(self, conflicts: List[Dict]) -> List[Dict]:
        """Format conflicts for display."""
        formatted = []
        
        for conflict in conflicts:
            rec1 = conflict['recommendation_1']
            rec2 = conflict['recommendation_2']
            
            formatted.append({
                'topic': conflict['topic'],
                'conflict_type': conflict['conflict_type'],
                'severity': conflict['severity'],
                'source_1': {
                    'organization': rec1['organization'],
                    'recommendation': rec1['full_sentence'],
                    'authority': rec1.get('authority_score', 0)
                },
                'source_2': {
                    'organization': rec2['organization'],
                    'recommendation': rec2['full_sentence'],
                    'authority': rec2.get('authority_score', 0)
                },
                'display': self._format_conflict_display(rec1, rec2, conflict)
            })
        
        return formatted
    
    def _format_conflict_display(self, rec1: Dict, rec2: Dict, conflict: Dict) -> str:
        """Format conflict for human-readable display."""
        topic = conflict['topic'].replace('_', ' ').title()
        
        display = f"⚠️ **Source Disagreement on {topic}**\\n\\n"
        display += f"**{rec1['organization']}** (authority: {rec1.get('authority_score', 0)}):\\n"
        display += f"  {rec1['full_sentence']}\\n\\n"
        display += f"**{rec2['organization']}** (authority: {rec2.get('authority_score', 0)}):\\n"
        display += f"  {rec2['full_sentence']}\\n\\n"
        
        # Add recommendation
        if rec1.get('authority_score', 0) > rec2.get('authority_score', 0):
            display += f"**Recommendation**: Prioritize {rec1['organization']} guidance as it has higher authority for this region. "
        elif rec2.get('authority_score', 0) > rec1.get('authority_score', 0):
            display += f"**Recommendation**: Prioritize {rec2['organization']} guidance as it has higher authority for this region. "
        else:
            display += f"**Recommendation**: Both sources have equal authority. "
        
        display += "Consult local AGRITEX for your specific conditions."
        
        return display
    
    def _generate_summary(self, conflicts: List[Dict], consensus: List[Dict]) -> str:
        """Generate a summary of the reconciliation."""
        if not conflicts:
            return (
                f"✅ All {len(consensus)} sources are in agreement. "
                f"Recommendations are consistent and reliable."
            )
        
        high_severity = sum(1 for c in conflicts if c['severity'] == 'high')
        moderate_severity = len(conflicts) - high_severity
        
        summary = f"⚠️ Found {len(conflicts)} disagreement(s) across sources "
        summary += f"({high_severity} high severity, {moderate_severity} moderate). "
        summary += f"Balanced recommendations provided based on source authority and local relevance."
        
        return summary


if __name__ == "__main__":
    # Test the reconciliation system
    reconciler = SourceReconciler()
    
    # Mock conflicting sources
    test_sources = [
        {
            'content': "AGRITEX recommends planting maize in October to early November for best yields in Natural Region II.",
            'metadata': {
                'filename': 'agritex_planting_guide.pdf',
                'organization': 'AGRITEX',
                'geographic_scope': 'Zimbabwe',
                'year': 2024
            }
        },
        {
            'content': "FAO suggests that maize planting should occur from mid-November to December to avoid early season dry spells.",
            'metadata': {
                'filename': 'fao_crop_calendar.pdf',
                'organization': 'FAO',
                'geographic_scope': 'Southern Africa',
                'year': 2023
            }
        },
        {
            'content': "ICRISAT research indicates farmers should wait for at least 50mm cumulative rainfall before planting maize.",
            'metadata': {
                'filename': 'icrisat_research_2024.pdf',
                'organization': 'ICRISAT',
                'geographic_scope': 'Sub-Saharan Africa',
                'year': 2024
            }
        }
    ]
    
    result = reconciler.reconcile_sources(test_sources, "When should I plant maize?")
    
    print("=== RECONCILIATION RESULT ===")
    print(f"\nSummary: {result['summary']}")
    print(f"\nConflicts Found: {result['conflicts_found']}")
    
    if result['conflicts']:
        print("\n=== CONFLICTS ===")
        for conflict in result['conflicts']:
            print(f"\n{conflict['display']}")
    
    print("\n=== CONSENSUS RECOMMENDATIONS ===")
    for rec in result['consensus_recommendations']:
        print(f"\n{rec['topic'].upper()}:")
        print(f"  {rec['recommendation']}")
        print(f"  Confidence: {rec['confidence']}, Authority: {rec['authority_score']}")
