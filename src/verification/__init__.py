"""
Evidence Verification Council (EVC) Tracking Module
Manages verification workflow for agricultural recommendations
"""

from .evc_tracker import (
    EVCTracker,
    Evidence,
    Verifier,
    VerificationHistory,
    VerificationStatus,
    VerifierRole
)

__all__ = [
    'EVCTracker',
    'Evidence',
    'Verifier',
    'VerificationHistory',
    'VerificationStatus',
    'VerifierRole'
]
