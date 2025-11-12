"""
Evidence Verification Council (EVC) Tracking System
Manages verification workflow for agricultural recommendations and data
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Verification status for agricultural evidence."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class VerifierRole(Enum):
    """Roles of verifiers in the council."""
    EXTENSION_OFFICER = "extension_officer"
    RESEARCH_SCIENTIST = "research_scientist"
    AGRITEX_SPECIALIST = "agritex_specialist"
    ACADEMIC = "academic"
    FIELD_COORDINATOR = "field_coordinator"
    SENIOR_REVIEWER = "senior_reviewer"


@dataclass
class Verifier:
    """Verifier credentials and information."""
    id: str
    name: str
    role: str
    organization: str
    credentials: List[str]
    specializations: List[str]  # e.g., maize_production, soil_science
    email: str
    active: bool = True
    verified_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class VerificationHistory:
    """Single verification action in the workflow."""
    verifier_id: str
    verifier_name: str
    action: str  # submitted, reviewed, approved, rejected, revised
    timestamp: str
    status: str
    comments: Optional[str] = None
    changes_requested: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Evidence:
    """Agricultural evidence requiring verification."""
    id: str
    title: str
    content: str
    evidence_type: str  # recommendation, policy, research_finding, advisory
    crop: Optional[str] = None
    topic: Optional[str] = None  # planting, fertilizer, pest_control, etc.
    natural_regions: Optional[List[str]] = None
    source_document: Optional[str] = None
    source_organization: Optional[str] = None
    submitted_by: Optional[str] = None
    submitted_date: Optional[str] = None
    status: str = VerificationStatus.DRAFT.value
    current_version: int = 1
    verification_history: List[VerificationHistory] = field(default_factory=list)
    assigned_verifiers: List[str] = field(default_factory=list)
    approval_date: Optional[str] = None
    expiry_date: Optional[str] = None
    validity_period_months: int = 12
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        """Initialize dates if not provided."""
        if not self.submitted_date:
            self.submitted_date = datetime.now().isoformat()
        if not self.expiry_date and self.approval_date:
            self.expiry_date = (
                datetime.fromisoformat(self.approval_date) + 
                timedelta(days=30 * self.validity_period_months)
            ).isoformat()
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['verification_history'] = [h.to_dict() for h in self.verification_history]
        return result


class EVCTracker:
    """Main Evidence Verification Council tracking system."""
    
    def __init__(self, storage_path: str = "./data/evc"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.evidence_store = self.storage_path / "evidence.json"
        self.verifiers_store = self.storage_path / "verifiers.json"
        self.workflow_log = self.storage_path / "workflow_log.json"
        
        # Load data
        self.evidence_db: Dict[str, Evidence] = self._load_evidence()
        self.verifiers_db: Dict[str, Verifier] = self._load_verifiers()
        self.workflow_history: List[Dict] = self._load_workflow_log()
        
        logger.info(f"EVC Tracker initialized with {len(self.evidence_db)} evidence items")
    
    def _load_evidence(self) -> Dict[str, Evidence]:
        """Load evidence database."""
        if self.evidence_store.exists():
            with open(self.evidence_store, 'r') as f:
                data = json.load(f)
                db = {}
                for eid, edata in data.items():
                    # Convert verification_history back to objects
                    history = [VerificationHistory(**h) for h in edata.get('verification_history', [])]
                    edata['verification_history'] = history
                    db[eid] = Evidence(**edata)
                return db
        return {}
    
    def _save_evidence(self):
        """Save evidence database."""
        data = {eid: ev.to_dict() for eid, ev in self.evidence_db.items()}
        with open(self.evidence_store, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_verifiers(self) -> Dict[str, Verifier]:
        """Load verifiers database."""
        if self.verifiers_store.exists():
            with open(self.verifiers_store, 'r') as f:
                data = json.load(f)
                return {vid: Verifier(**vdata) for vid, vdata in data.items()}
        return {}
    
    def _save_verifiers(self):
        """Save verifiers database."""
        data = {vid: v.to_dict() for vid, v in self.verifiers_db.items()}
        with open(self.verifiers_store, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_workflow_log(self) -> List[Dict]:
        """Load workflow history log."""
        if self.workflow_log.exists():
            with open(self.workflow_log, 'r') as f:
                return json.load(f)
        return []
    
    def _save_workflow_log(self):
        """Save workflow history log."""
        with open(self.workflow_log, 'w') as f:
            json.dump(self.workflow_history, f, indent=2)
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_suffix = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"{prefix}_{timestamp}_{hash_suffix}"
    
    def register_verifier(
        self,
        name: str,
        role: str,
        organization: str,
        credentials: List[str],
        specializations: List[str],
        email: str
    ) -> Verifier:
        """Register a new verifier."""
        verifier_id = self._generate_id("VRF")
        
        verifier = Verifier(
            id=verifier_id,
            name=name,
            role=role,
            organization=organization,
            credentials=credentials,
            specializations=specializations,
            email=email,
            active=True,
            verified_count=0
        )
        
        self.verifiers_db[verifier_id] = verifier
        self._save_verifiers()
        
        logger.info(f"Registered verifier: {name} ({verifier_id})")
        return verifier
    
    def submit_evidence(
        self,
        title: str,
        content: str,
        evidence_type: str,
        submitted_by: str,
        crop: Optional[str] = None,
        topic: Optional[str] = None,
        natural_regions: Optional[List[str]] = None,
        source_document: Optional[str] = None,
        source_organization: Optional[str] = None,
        validity_period_months: int = 12,
        metadata: Optional[Dict] = None
    ) -> Evidence:
        """Submit new evidence for verification."""
        evidence_id = self._generate_id("EV")
        
        evidence = Evidence(
            id=evidence_id,
            title=title,
            content=content,
            evidence_type=evidence_type,
            crop=crop,
            topic=topic,
            natural_regions=natural_regions,
            source_document=source_document,
            source_organization=source_organization,
            submitted_by=submitted_by,
            submitted_date=datetime.now().isoformat(),
            status=VerificationStatus.SUBMITTED.value,
            validity_period_months=validity_period_months,
            metadata=metadata
        )
        
        # Add submission to history
        evidence.verification_history.append(VerificationHistory(
            verifier_id=submitted_by,
            verifier_name=submitted_by,
            action="submitted",
            timestamp=datetime.now().isoformat(),
            status=VerificationStatus.SUBMITTED.value,
            comments="Evidence submitted for verification"
        ))
        
        self.evidence_db[evidence_id] = evidence
        self._save_evidence()
        
        # Log to workflow
        self.workflow_history.append({
            'evidence_id': evidence_id,
            'action': 'submitted',
            'timestamp': datetime.now().isoformat(),
            'by': submitted_by
        })
        self._save_workflow_log()
        
        logger.info(f"Evidence submitted: {title} ({evidence_id})")
        return evidence
    
    def assign_verifiers(self, evidence_id: str, verifier_ids: List[str]) -> bool:
        """Assign verifiers to evidence."""
        if evidence_id not in self.evidence_db:
            logger.error(f"Evidence not found: {evidence_id}")
            return False
        
        evidence = self.evidence_db[evidence_id]
        
        # Validate verifiers exist
        for vid in verifier_ids:
            if vid not in self.verifiers_db:
                logger.error(f"Verifier not found: {vid}")
                return False
        
        evidence.assigned_verifiers = verifier_ids
        evidence.status = VerificationStatus.IN_REVIEW.value
        
        # Add to history
        evidence.verification_history.append(VerificationHistory(
            verifier_id="system",
            verifier_name="System",
            action="assigned",
            timestamp=datetime.now().isoformat(),
            status=VerificationStatus.IN_REVIEW.value,
            comments=f"Assigned to {len(verifier_ids)} verifier(s)"
        ))
        
        self._save_evidence()
        logger.info(f"Assigned {len(verifier_ids)} verifiers to {evidence_id}")
        return True
    
    def review_evidence(
        self,
        evidence_id: str,
        verifier_id: str,
        approve: bool,
        comments: Optional[str] = None,
        changes_requested: Optional[List[str]] = None
    ) -> bool:
        """Verifier reviews evidence."""
        if evidence_id not in self.evidence_db:
            logger.error(f"Evidence not found: {evidence_id}")
            return False
        
        if verifier_id not in self.verifiers_db:
            logger.error(f"Verifier not found: {verifier_id}")
            return False
        
        evidence = self.evidence_db[evidence_id]
        verifier = self.verifiers_db[verifier_id]
        
        # Check if verifier is assigned
        if verifier_id not in evidence.assigned_verifiers:
            logger.warning(f"Verifier {verifier_id} not assigned to {evidence_id}")
        
        action = "approved" if approve else "changes_requested"
        
        # Add review to history
        evidence.verification_history.append(VerificationHistory(
            verifier_id=verifier_id,
            verifier_name=verifier.name,
            action=action,
            timestamp=datetime.now().isoformat(),
            status=evidence.status,
            comments=comments,
            changes_requested=changes_requested
        ))
        
        # Update verifier stats
        if approve:
            verifier.verified_count += 1
        
        self._save_evidence()
        self._save_verifiers()
        
        logger.info(f"Verifier {verifier.name} {action} evidence {evidence_id}")
        return True
    
    def approve_evidence(self, evidence_id: str, approver_id: str) -> bool:
        """Final approval of evidence."""
        if evidence_id not in self.evidence_db:
            logger.error(f"Evidence not found: {evidence_id}")
            return False
        
        if approver_id not in self.verifiers_db:
            logger.error(f"Approver not found: {approver_id}")
            return False
        
        evidence = self.evidence_db[evidence_id]
        approver = self.verifiers_db[approver_id]
        
        # Check if approver has senior role
        if approver.role not in [VerifierRole.SENIOR_REVIEWER.value, VerifierRole.AGRITEX_SPECIALIST.value]:
            logger.warning(f"Approver {approver.name} may not have authority for final approval")
        
        evidence.status = VerificationStatus.APPROVED.value
        evidence.approval_date = datetime.now().isoformat()
        
        # Calculate expiry date
        evidence.expiry_date = (
            datetime.now() + timedelta(days=30 * evidence.validity_period_months)
        ).isoformat()
        
        # Add approval to history
        evidence.verification_history.append(VerificationHistory(
            verifier_id=approver_id,
            verifier_name=approver.name,
            action="approved",
            timestamp=datetime.now().isoformat(),
            status=VerificationStatus.APPROVED.value,
            comments="Evidence approved for publication"
        ))
        
        approver.verified_count += 1
        
        self._save_evidence()
        self._save_verifiers()
        
        logger.info(f"✓ Evidence {evidence_id} approved by {approver.name}")
        return True
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Get evidence by ID."""
        return self.evidence_db.get(evidence_id)
    
    def get_evidence_by_status(self, status: str) -> List[Evidence]:
        """Get all evidence with specific status."""
        return [ev for ev in self.evidence_db.values() if ev.status == status]
    
    def get_evidence_by_verifier(self, verifier_id: str) -> List[Evidence]:
        """Get evidence assigned to a verifier."""
        return [ev for ev in self.evidence_db.values() if verifier_id in ev.assigned_verifiers]
    
    def get_expired_evidence(self) -> List[Evidence]:
        """Get evidence that has expired."""
        now = datetime.now()
        expired = []
        
        for evidence in self.evidence_db.values():
            if evidence.expiry_date and evidence.status == VerificationStatus.APPROVED.value:
                expiry = datetime.fromisoformat(evidence.expiry_date)
                if now > expiry:
                    # Mark as expired
                    evidence.status = VerificationStatus.EXPIRED.value
                    expired.append(evidence)
        
        if expired:
            self._save_evidence()
        
        return expired
    
    def get_verifier_statistics(self, verifier_id: str) -> Dict:
        """Get statistics for a verifier."""
        if verifier_id not in self.verifiers_db:
            return {}
        
        verifier = self.verifiers_db[verifier_id]
        assigned = len(self.get_evidence_by_verifier(verifier_id))
        pending_review = len([
            ev for ev in self.get_evidence_by_verifier(verifier_id)
            if ev.status == VerificationStatus.IN_REVIEW.value
        ])
        
        return {
            'name': verifier.name,
            'role': verifier.role,
            'organization': verifier.organization,
            'total_verified': verifier.verified_count,
            'currently_assigned': assigned,
            'pending_review': pending_review,
            'specializations': verifier.specializations
        }
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics."""
        status_counts = {}
        for status in VerificationStatus:
            status_counts[status.value] = len(self.get_evidence_by_status(status.value))
        
        evidence_by_type = {}
        for ev in self.evidence_db.values():
            evidence_by_type[ev.evidence_type] = evidence_by_type.get(ev.evidence_type, 0) + 1
        
        return {
            'total_evidence': len(self.evidence_db),
            'total_verifiers': len(self.verifiers_db),
            'active_verifiers': len([v for v in self.verifiers_db.values() if v.active]),
            'by_status': status_counts,
            'by_type': evidence_by_type,
            'expired_count': len(self.get_expired_evidence())
        }


if __name__ == "__main__":
    # Test EVC Tracker
    evc = EVCTracker()
    
    print("\n=== EVC TRACKER TEST ===\n")
    
    # Register verifiers
    print("1. Registering verifiers...")
    v1 = evc.register_verifier(
        name="Dr. John Mapfumo",
        role=VerifierRole.RESEARCH_SCIENTIST.value,
        organization="ICRISAT Zimbabwe",
        credentials=["PhD Agronomy", "15 years experience"],
        specializations=["maize_production", "soil_fertility"],
        email="j.mapfumo@icrisat.org"
    )
    
    v2 = evc.register_verifier(
        name="Ms. Grace Moyo",
        role=VerifierRole.AGRITEX_SPECIALIST.value,
        organization="AGRITEX Mashonaland",
        credentials=["MSc Agriculture", "AGRITEX Certified"],
        specializations=["extension_services", "farmer_training"],
        email="g.moyo@agritex.gov.zw"
    )
    
    print(f"✓ Registered: {v1.name}, {v2.name}\n")
    
    # Submit evidence
    print("2. Submitting evidence...")
    ev1 = evc.submit_evidence(
        title="Maize Planting Guidelines for Natural Region II",
        content="Farmers should plant maize between October 15 and November 15 after receiving 50mm cumulative rainfall...",
        evidence_type="recommendation",
        submitted_by="system",
        crop="maize",
        topic="planting",
        natural_regions=["II", "IIA"],
        source_organization="AGRITEX",
        validity_period_months=12
    )
    print(f"✓ Evidence submitted: {ev1.id}\n")
    
    # Assign verifiers
    print("3. Assigning verifiers...")
    evc.assign_verifiers(ev1.id, [v1.id, v2.id])
    print(f"✓ Assigned verifiers to {ev1.id}\n")
    
    # Review
    print("4. Verifiers reviewing...")
    evc.review_evidence(ev1.id, v1.id, approve=True, comments="Scientific evidence supports this recommendation")
    evc.review_evidence(ev1.id, v2.id, approve=True, comments="Aligns with field experience")
    print(f"✓ Reviews complete\n")
    
    # Approve
    print("5. Final approval...")
    evc.approve_evidence(ev1.id, v2.id)
    print(f"✓ Evidence approved\n")
    
    # Statistics
    print("=== SYSTEM STATISTICS ===")
    stats = evc.get_system_statistics()
    print(f"Total Evidence: {stats['total_evidence']}")
    print(f"Total Verifiers: {stats['total_verifiers']}")
    print(f"By Status: {stats['by_status']}")
    print(f"By Type: {stats['by_type']}")
    
    print("\n=== VERIFIER STATS ===")
    v1_stats = evc.get_verifier_statistics(v1.id)
    print(f"{v1_stats['name']}:")
    print(f"  Verified: {v1_stats['total_verified']}")
    print(f"  Pending: {v1_stats['pending_review']}")
