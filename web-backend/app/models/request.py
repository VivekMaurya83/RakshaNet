from pydantic import BaseModel

class CurrencyAnalysisRequest(BaseModel):
    # Currently, requests are handled via multipart/form-data.
    pass

class CurrencyReportRequest(BaseModel):
    scanId: str
    imagePath: str
    prediction: str
    confidence: float
