"""
Extended API Endpoints for Phase 2/3 Features
Includes endpoints for External Sync, EVC Tracking, and Historical Archive
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# EXTERNAL DATA SYNC ENDPOINTS
# ============================================================================

class SyncRequest(BaseModel):
    """Request to sync external data."""
    source_data: Dict
    

def add_sync_endpoints(app, data_sync):
    """Add external data sync endpoints to FastAPI app."""
    
    @app.get("/api/sync/status")
    async def get_sync_status():
        """Get sync status for all sources."""
        if data_sync is None:
            raise HTTPException(status_code=503, detail="Data sync not initialized")
        
        try:
            status = data_sync.get_sync_status()
            return {
                "status": "ok",
                "sources": status
            }
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/sync/{source}")
    async def sync_source(source: str, request: SyncRequest):
        """Sync data from a specific source."""
        if data_sync is None:
            raise HTTPException(status_code=503, detail="Data sync not initialized")
        
        try:
            from src.external.data_sync import DataSource
            
            # Map source string to enum
            source_enum = DataSource(source.lower())
            
            # Perform sync
            record = data_sync.sync_source(source_enum, request.source_data)
            
            return {
                "status": record.status,
                "source": record.source,
                "records_new": record.records_new,
                "records_updated": record.records_updated,
                "duration_seconds": record.duration_seconds,
                "next_sync": record.next_sync
            }
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
        except Exception as e:
            logger.error(f"Error syncing source {source}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/sync/data/{data_type}")
    async def get_synced_data_by_type(data_type: str):
        """Get all synced data of a specific type."""
        if data_sync is None:
            raise HTTPException(status_code=503, detail="Data sync not initialized")
        
        try:
            data = data_sync.get_data_by_type(data_type)
            return {
                "data_type": data_type,
                "count": len(data),
                "data": [entry.to_dict() for entry in data]
            }
        except Exception as e:
            logger.error(f"Error getting synced data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/sync/statistics")
    async def get_sync_statistics():
        """Get overall sync statistics."""
        if data_sync is None:
            raise HTTPException(status_code=503, detail="Data sync not initialized")
        
        try:
            stats = data_sync.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting sync statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EVIDENCE VERIFICATION COUNCIL (EVC) ENDPOINTS
# ============================================================================

class VerifierRegistration(BaseModel):
    """Request to register a new verifier."""
    name: str
    role: str
    organization: str
    credentials: List[str]
    specializations: List[str]
    email: str


class EvidenceSubmission(BaseModel):
    """Request to submit new evidence."""
    title: str
    content: str
    evidence_type: str
    submitted_by: str
    crop: Optional[str] = None
    topic: Optional[str] = None
    natural_regions: Optional[List[str]] = None
    source_document: Optional[str] = None
    source_organization: Optional[str] = None
    validity_period_months: int = 12


class EvidenceReview(BaseModel):
    """Request to review evidence."""
    verifier_id: str
    approve: bool
    comments: Optional[str] = None
    changes_requested: Optional[List[str]] = None


def add_evc_endpoints(app, evc_tracker):
    """Add EVC tracking endpoints to FastAPI app."""
    
    @app.post("/api/evc/verifiers/register")
    async def register_verifier(request: VerifierRegistration):
        """Register a new verifier."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            verifier = evc_tracker.register_verifier(
                name=request.name,
                role=request.role,
                organization=request.organization,
                credentials=request.credentials,
                specializations=request.specializations,
                email=request.email
            )
            
            return {
                "status": "registered",
                "verifier": verifier.to_dict()
            }
        except Exception as e:
            logger.error(f"Error registering verifier: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/evc/verifiers")
    async def list_verifiers():
        """List all registered verifiers."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            verifiers = [v.to_dict() for v in evc_tracker.verifiers_db.values()]
            return {
                "total": len(verifiers),
                "verifiers": verifiers
            }
        except Exception as e:
            logger.error(f"Error listing verifiers: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/evc/verifiers/{verifier_id}/statistics")
    async def get_verifier_statistics(verifier_id: str):
        """Get statistics for a specific verifier."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            stats = evc_tracker.get_verifier_statistics(verifier_id)
            if not stats:
                raise HTTPException(status_code=404, detail="Verifier not found")
            return stats
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting verifier statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/evc/evidence/submit")
    async def submit_evidence(request: EvidenceSubmission):
        """Submit new evidence for verification."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            evidence = evc_tracker.submit_evidence(
                title=request.title,
                content=request.content,
                evidence_type=request.evidence_type,
                submitted_by=request.submitted_by,
                crop=request.crop,
                topic=request.topic,
                natural_regions=request.natural_regions,
                source_document=request.source_document,
                source_organization=request.source_organization,
                validity_period_months=request.validity_period_months
            )
            
            return {
                "status": "submitted",
                "evidence": evidence.to_dict()
            }
        except Exception as e:
            logger.error(f"Error submitting evidence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/evc/evidence/{evidence_id}")
    async def get_evidence(evidence_id: str):
        """Get specific evidence by ID."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            evidence = evc_tracker.get_evidence(evidence_id)
            if not evidence:
                raise HTTPException(status_code=404, detail="Evidence not found")
            return evidence.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting evidence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/evc/evidence/status/{status}")
    async def get_evidence_by_status(status: str):
        """Get all evidence with specific status."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            evidence_list = evc_tracker.get_evidence_by_status(status)
            return {
                "status": status,
                "count": len(evidence_list),
                "evidence": [e.to_dict() for e in evidence_list]
            }
        except Exception as e:
            logger.error(f"Error getting evidence by status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/evc/evidence/{evidence_id}/review")
    async def review_evidence(evidence_id: str, request: EvidenceReview):
        """Review evidence."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            success = evc_tracker.review_evidence(
                evidence_id=evidence_id,
                verifier_id=request.verifier_id,
                approve=request.approve,
                comments=request.comments,
                changes_requested=request.changes_requested
            )
            
            if not success:
                raise HTTPException(status_code=404, detail="Evidence or verifier not found")
            
            return {
                "status": "reviewed",
                "evidence_id": evidence_id,
                "approved": request.approve
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reviewing evidence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/evc/evidence/{evidence_id}/approve")
    async def approve_evidence(evidence_id: str, approver_id: str):
        """Give final approval to evidence."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            success = evc_tracker.approve_evidence(evidence_id, approver_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Evidence or approver not found")
            
            return {
                "status": "approved",
                "evidence_id": evidence_id
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error approving evidence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/evc/statistics")
    async def get_evc_statistics():
        """Get overall EVC system statistics."""
        if evc_tracker is None:
            raise HTTPException(status_code=503, detail="EVC tracker not initialized")
        
        try:
            stats = evc_tracker.get_system_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting EVC statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HISTORICAL DATA ARCHIVE ENDPOINTS
# ============================================================================

class DataPointSubmission(BaseModel):
    """Request to add a historical data point."""
    category: str
    timestamp: str
    value: float
    unit: str
    crop: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict] = None


class TrendRequest(BaseModel):
    """Request for trend analysis."""
    category: str
    crop: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class YearComparisonRequest(BaseModel):
    """Request for year-over-year comparison."""
    category: str
    year1: int
    year2: int
    crop: Optional[str] = None
    location: Optional[str] = None
    aggregation: str = "average"


def add_historical_endpoints(app, historical_archive):
    """Add historical archive endpoints to FastAPI app."""
    
    @app.post("/api/historical/add")
    async def add_data_point(request: DataPointSubmission):
        """Add a historical data point."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            from src.historical.archive import DataCategory
            
            category = DataCategory(request.category.lower())
            
            success = historical_archive.add_data_point(
                category=category,
                timestamp=request.timestamp,
                value=request.value,
                unit=request.unit,
                crop=request.crop,
                location=request.location,
                metadata=request.metadata
            )
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to add data point")
            
            return {
                "status": "added",
                "category": request.category,
                "timestamp": request.timestamp
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")
        except Exception as e:
            logger.error(f"Error adding data point: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/historical/trend")
    async def analyze_trend(request: TrendRequest):
        """Analyze trend in historical data."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            from src.historical.archive import DataCategory
            
            category = DataCategory(request.category.lower())
            
            trend = historical_archive.analyze_trend(
                category=category,
                crop=request.crop,
                location=request.location,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            if not trend:
                raise HTTPException(status_code=404, detail="Insufficient data for trend analysis")
            
            return trend.to_dict()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/historical/compare")
    async def compare_years(request: YearComparisonRequest):
        """Compare data between two years."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            from src.historical.archive import DataCategory
            
            category = DataCategory(request.category.lower())
            
            comparison = historical_archive.compare_year_over_year(
                category=category,
                year1=request.year1,
                year2=request.year2,
                crop=request.crop,
                location=request.location,
                aggregation=request.aggregation
            )
            
            if not comparison:
                raise HTTPException(status_code=404, detail="Insufficient data for comparison")
            
            return comparison.to_dict()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error comparing years: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/historical/anomalies")
    async def detect_anomalies(
        category: str,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        threshold: float = 2.0
    ):
        """Detect anomalies in historical data."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            from src.historical.archive import DataCategory
            
            cat = DataCategory(category.lower())
            
            anomalies = historical_archive.detect_anomalies(
                category=cat,
                crop=crop,
                location=location,
                start_date=start_date,
                end_date=end_date,
                threshold_stdev=threshold
            )
            
            return {
                "category": category,
                "count": len(anomalies),
                "anomalies": [a.to_dict() for a in anomalies]
            }
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/historical/seasonal")
    async def get_seasonal_pattern(
        category: str,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        years: int = 3
    ):
        """Get seasonal pattern for data."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            from src.historical.archive import DataCategory
            
            cat = DataCategory(category.lower())
            
            pattern = historical_archive.get_seasonal_pattern(
                category=cat,
                crop=crop,
                location=location,
                years=years
            )
            
            return {
                "category": category,
                "years_analyzed": years,
                "monthly_averages": pattern
            }
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        except Exception as e:
            logger.error(f"Error getting seasonal pattern: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/historical/statistics")
    async def get_historical_statistics():
        """Get historical archive statistics."""
        if historical_archive is None:
            raise HTTPException(status_code=503, detail="Historical archive not initialized")
        
        try:
            stats = historical_archive.get_statistics()
            return stats
        except Exception as e:
            logger.error(f"Error getting historical statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
