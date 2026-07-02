from pydantic import BaseModel
from typing import List

class CurrencyAnalysisResponse(BaseModel):
    prediction: str  # "Counterfeit" or "Genuine"
    confidence: float
    explanation: str
    detectedFeatures: List[str]
    canReport: bool
    scanId: str
    imagePath: str

class CurrencyReportResponse(BaseModel):
    status: str
    reportId: str
    savedLocally: bool
