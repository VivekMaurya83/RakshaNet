import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.currency_service import CurrencyService
from app.models.response import CurrencyAnalysisResponse, CurrencyReportResponse
from app.models.request import CurrencyReportRequest

router = APIRouter()
currency_service = CurrencyService()

# Validation parameters
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes
ALLOWED_MIMETYPES = {"image/jpeg", "image/jpg", "image/png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=CurrencyAnalysisResponse)
async def analyze_currency_note(
    image: UploadFile = File(...)
):
    """
    POST /api/v1/currency/analyze
    
    Accepts a banknote photo via multipart/form-data, validates file specifications,
    processes it through the service layer, and returns the classification results.
    """
    logger.info(f"Received currency note scan request: {image.filename}")
    
    # 1. Validate file extension
    filename = image.filename or ""
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected scan with unsupported extension: {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Only JPG, JPEG, and PNG are allowed."
        )
        
    # 2. Validate MIME type
    if image.content_type not in ALLOWED_MIMETYPES:
        logger.warning(f"Rejected scan with unsupported content-type: {image.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type '{image.content_type}'. Please upload an image/jpeg or image/png."
        )
        
    # 3. Validate file size (check if it exceeds the limit)
    content = await image.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        logger.warning("Rejected scan: File size exceeds the maximum limit of 5MB.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded image exceeds the maximum allowed file size of 5MB."
        )
        
    # Reset file read pointer after size check
    await image.seek(0)
    
    try:
        result = currency_service.analyze_banknote(image)
        return result
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Inference pipeline execution failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the banknote image: {str(e)}"
        )

@router.post("/report", response_model=CurrencyReportResponse)
async def report_suspicious_note(
    request_body: CurrencyReportRequest
):
    """
    POST /api/v1/currency/report
    
    Accepts report metadata, copies the temporary image, and saves the report locally.
    """
    logger.info(f"Received suspicious note report request for scanId: {request_body.scanId}")
    try:
        response = currency_service.create_local_report(
            scan_id=request_body.scanId,
            image_path_str=request_body.imagePath,
            prediction=request_body.prediction,
            confidence=request_body.confidence
        )
        return response
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Failed to submit local report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit local report: {str(e)}"
        )
