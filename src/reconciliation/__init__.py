"""
Multi-Source Reconciliation Module
Handles conflict detection and resolution between agricultural sources
"""

from .source_reconciler import (
    SourceReconciler,
    SourceAuthority,
    RecommendationExtractor,
    ConflictDetector
)

__all__ = [
    'SourceReconciler',
    'SourceAuthority',
    'RecommendationExtractor',
    'ConflictDetector'
]
