from fastapi import APIRouter, Depends, File, UploadFile
from typing import Dict
from shared.utils import verify_firebase_token
from app.services.deepfake_service import DeepfakeService

router = APIRouter()
deepfake_service = DeepfakeService()

@router.post("/analyze-deepfake")
async def analyze_voice_recording(
    audio: UploadFile = File(...),
    user: Dict = Depends(verify_firebase_token)
):
    """
    Ingests recorded voice audio file, classifies voice features using the
    centralized ONNX model inside services, and returns a synthetic clone score.
    """
    audio_bytes = await audio.read()
    verdict = await deepfake_service.detect_voice_deepfake(audio_bytes)
    return verdict
