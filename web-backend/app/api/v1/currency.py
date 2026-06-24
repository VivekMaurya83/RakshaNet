from fastapi import APIRouter, Depends, File, UploadFile, Form
from typing import Dict, Optional
from shared.utils import verify_firebase_token
from shared.models import CurrencyScan
from app.services.currency_service import CurrencyService

router = APIRouter()
currency_service = CurrencyService()

@router.post("/scan", response_model=CurrencyScan)
async def scan_banknote(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    user: Dict = Depends(verify_firebase_token)
):
    """
    Ingests photo of note, delegates to CurrencyService to execute OpenCV/ONNX pipelines,
    and returns analyzed scan results.
    """
    image_bytes = await image.read()
    analyst_uid = user.get("uid", "unknown")
    
    # Process scan via Service Layer
    scan_doc = await currency_service.analyze_banknote(image_bytes, analyst_uid)
    return scan_doc
