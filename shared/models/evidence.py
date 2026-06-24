from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EvidencePackage(BaseModel):
    packageId: str = Field(..., description="Unique Evidence ID")
    associatedReports: List[str] = Field(..., description="Scam report IDs aggregated in this package")
    generatedBy: str = Field(..., description="Firebase UID of the officer compiling this")
    
    # Firebase Storage Integrations
    pdfStoragePath: str = Field(..., description="Storage bucket path, e.g. evidence_pdfs/EVIDENCE_333.pdf")
    pdfUrl: str = Field(..., description="Signed download URL of evidence PDF")
    
    fileHash: str = Field(..., description="SHA-256 hash to ensure tamper-proofing")
    status: str = Field("sealed", description="Status of evidence: draft, sealed, or tampered")
    remarks: Optional[str] = Field(None, description="Notes from the compiling officer")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    sealedAt: Optional[datetime] = Field(None, description="Timestamp when evidence was hashes and sealed")
