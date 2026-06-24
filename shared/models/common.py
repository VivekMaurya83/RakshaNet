from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GeoLocation(BaseModel):
    latitude: float = Field(..., description="GPS Latitude")
    longitude: float = Field(..., description="GPS Longitude")
    city: Optional[str] = Field(None, description="City name resolved from coordinates")
    state: Optional[str] = Field(None, description="State/Province name")
    zipCode: Optional[str] = Field(None, description="ZIP or PIN code")

class ThreatActor(BaseModel):
    name: Optional[str] = Field(None, description="Name or pseudonyms of the threat actor")
    phone: Optional[str] = Field(None, description="Phone number or spoofed caller ID")
    email: Optional[str] = Field(None, description="Email associated with scammer")
    agencyClaimed: Optional[str] = Field(None, description="Agency claimed by caller, e.g. CBI, Police, Custom")
    ipAddress: Optional[str] = Field(None, description="Suspected IP address of threat actor")

class SystemLog(BaseModel):
    logId: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    service: str  # web-backend, mobile-backend
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
