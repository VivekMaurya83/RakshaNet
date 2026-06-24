from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List, Dict
from pydantic import BaseModel
from shared.utils import verify_firebase_token
from shared.models import EvidencePackage
from app.services.evidence_service import EvidenceService

router = APIRouter()
evidence_service = EvidenceService()

class EvidenceRequest(BaseModel):
    reportIds: List[str]
    remarks: str

@router.post("/generate", response_model=EvidencePackage, status_code=201)
async def generate_evidence_package(
    payload: EvidenceRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(verify_firebase_token)
):
    """
    Compiles selected scam logs into a single forensic PDF, uploads to Storage,
    seals with SHA-256 hash, and logs Firestore metadata.
    """
    officer_uid = user.get("uid", "unknown")
    package = await evidence_service.compile_forensic_evidence(
        payload.reportIds,
        payload.remarks,
        officer_uid
    )
    return package
