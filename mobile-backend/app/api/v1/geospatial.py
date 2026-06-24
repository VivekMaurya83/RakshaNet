from fastapi import APIRouter, Depends
from typing import Dict
from shared.utils import verify_firebase_token
from shared.models import GeoLocation
from app.services.heatmap_service import HeatmapService

router = APIRouter()
heatmap_service = HeatmapService()

@router.post("/report-location")
async def report_crime_location(
    location: GeoLocation,
    crimeType: str,
    user: Dict = Depends(verify_firebase_token)
):
    """
    Ingests crime coordinates and updates analytics heatmaps via the HeatmapService.
    """
    reporter_uid = user.get("uid", "unknown")
    doc_id = heatmap_service.log_report_location(location, crimeType, reporter_uid)
    return {"status": "success", "documentId": doc_id}
