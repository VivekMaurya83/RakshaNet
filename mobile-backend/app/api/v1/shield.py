from fastapi import APIRouter, Depends, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
from shared.utils import verify_firebase_token
from app.services.scam_service import ScamService
import logging

router = APIRouter()
scam_service = ScamService()

@router.post("/upload")
async def upload_suspicious_audio(
    audio: UploadFile = File(...),
    callerId: str = Form(...),
    user: Dict = Depends(verify_firebase_token)
):
    """
    Uploader route forwarding requests to ScamService.
    """
    audio_bytes = await audio.read()
    reporter_uid = user.get("uid", "unknown")
    result = await scam_service.analyze_call_audio(audio_bytes, callerId, reporter_uid)
    return result

@router.websocket("/stream")
async def suspicious_stream_listener(websocket: WebSocket):
    """
    WebSocket streaming endpoint.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Live monitoring logic mockup
            await websocket.send_json({
                "liveTranscript": data,
                "warningFlag": "cbi" in data.lower(),
                "scamLikelihood": 85.0 if "cbi" in data.lower() else 10.0
            })
    except WebSocketDisconnect:
        pass
