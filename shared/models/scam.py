from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .common import GeoLocation, ThreatActor

class RiskAnalysis(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Risk Score from 0 (Safe) to 100 (Immediate Danger)")
    riskLevel: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    keyIdentifiers: List[str] = Field(default_factory=list, description="Scam triggers, e.g. 'cbi_claim', 'crypto_payment'")
    summary: str = Field(..., description="Gemini-generated summary of why this is/isn't flagged")

class ScamReport(BaseModel):
    reportId: str = Field(..., description="Unique ID for the scam report")
    reporterUid: str = Field(..., description="Firebase UID of reporting user")
    scamType: str = Field(..., description="Type of scam, e.g. 'digital_arrest', 'phishing'")
    threatActor: ThreatActor = Field(default_factory=ThreatActor)
    
    # Firebase Storage Integrations
    audioStoragePath: Optional[str] = Field(None, description="Storage bucket path, e.g., audio/REPORT_123.mp3")
    audioUrl: Optional[str] = Field(None, description="Signed download URL of call audio")
    screenshotStoragePath: Optional[str] = Field(None, description="Storage bucket path for screenshot")
    screenshotUrl: Optional[str] = Field(None, description="Signed download URL of screenshot")
    
    transcript: Optional[str] = Field(None, description="Transcript of calls or SMS message bodies")
    riskAnalysis: RiskAnalysis
    location: Optional[GeoLocation] = None
    status: str = Field("pending_investigation", description="Status: pending_investigation, verified, archived")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
