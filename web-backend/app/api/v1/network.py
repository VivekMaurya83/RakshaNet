from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from typing import Dict
import os
from shared.utils import verify_firebase_token
from shared.models import NetworkGraphPayload, FraudNode, FraudEdge
from app.services.graph_service import GraphService

router = APIRouter()
graph_service = GraphService()

@router.get("/sigma-graph")
async def get_sigma_graph():
    """
    Serves the precomputed network graph layout directly from disk.
    """
    file_path = os.path.join(
        os.path.dirname(__file__), 
        "../../features/fraud_network/processed/sigma_graph.json"
    )
    if not os.path.exists(file_path):
        return {"error": "Graph file not precomputed yet"}
    return FileResponse(file_path, media_type="application/json")

@router.get("/graph", response_model=NetworkGraphPayload)
async def get_fraud_graph(
    minRiskScore: float = 50.0,
    user: Dict = Depends(verify_firebase_token)
):
    """
    Retrieves nodes and link edges from Firestore, formatted for React Flow canvas.
    """
    return graph_service.get_react_flow_network()

@router.post("/node", response_model=FraudNode)
async def add_fraud_node(
    node: FraudNode,
    user: Dict = Depends(verify_firebase_token)
):
    """Adds a fraud node via the Service Layer."""
    return graph_service.add_node(node)

@router.post("/edge", response_model=FraudEdge)
async def add_fraud_edge(
    edge: FraudEdge,
    user: Dict = Depends(verify_firebase_token)
):
    """Adds a network link connection via the Service Layer."""
    return graph_service.add_edge(edge)

@router.get("/cross-state-linkages")
async def get_cross_state_linkages():
    """
    Returns correlated inter-state fraud syndicates linked by behavioral fingerprints and device signatures.
    """
    return [
        {
            "id": "syn_001",
            "name": "Mewat-Jammu Gateway Linker",
            "confidence": 94,
            "modus_operandi": "Part-time Job Telegram Task Scam",
            "indicators": ["Same Phone IMEI", "SBI Mule Account Branch Matches", "Identical 6-Hop Transaction Routing Pacing"],
            "incidents": [
                {
                    "state": "Maharashtra",
                    "date": "2026-06-12",
                    "volume": "₹45.6L",
                    "main_ip": "192.168.4.12",
                    "device_signature": "Xiaomi Redmi Note 10 (MIUI v13)",
                    "complaints": 18
                },
                {
                    "state": "Telangana",
                    "date": "2026-06-28",
                    "volume": "₹28.4L",
                    "main_ip": "192.168.4.15",
                    "device_signature": "Xiaomi Redmi Note 10 (MIUI v13)",
                    "complaints": 12
                },
                {
                    "state": "Karnataka",
                    "date": "2026-07-01",
                    "volume": "₹18.2L",
                    "main_ip": "192.168.4.92",
                    "device_signature": "Xiaomi Redmi Note 10 (MIUI v13)",
                    "complaints": 9
                }
            ]
        },
        {
            "id": "syn_002",
            "name": "Noida Digital Arrest Syndicate",
            "confidence": 89,
            "modus_operandi": "Digital Arrest (CBI/TRAI Impersonation)",
            "indicators": ["Voice ID match on victim recordings", "Same hosting IP subnet range", "Rented corporate current bank accounts"],
            "incidents": [
                {
                    "state": "Delhi",
                    "date": "2026-05-18",
                    "volume": "₹92.0L",
                    "main_ip": "103.45.2.11",
                    "device_signature": "Asterisk VoIP SIP Gateway",
                    "complaints": 34
                },
                {
                    "state": "Tamil Nadu",
                    "date": "2026-06-05",
                    "volume": "₹74.5L",
                    "main_ip": "103.45.2.18",
                    "device_signature": "Asterisk VoIP SIP Gateway",
                    "complaints": 21
                }
            ]
        },
        {
            "id": "syn_003",
            "name": "Mewat Military Deposit Mimics",
            "confidence": 86,
            "modus_operandi": "Fake Army Listing/OLX Deposit Fraud",
            "indicators": ["Virtual SIM WhatsApp Numbers", "Same ATM coordinates for cash withdrawals (Alwar border)"],
            "incidents": [
                {
                    "state": "Rajasthan",
                    "date": "2026-06-15",
                    "volume": "₹12.3L",
                    "main_ip": "172.16.8.22",
                    "device_signature": "Realme 9 Pro (Android 12)",
                    "complaints": 15
                },
                {
                    "state": "Haryana",
                    "date": "2026-06-22",
                    "volume": "₹15.8L",
                    "main_ip": "172.16.8.29",
                    "device_signature": "Realme 9 Pro (Android 12)",
                    "complaints": 19
                }
            ]
        }
    ]

@router.post("/issue-interstate-alert")
async def issue_interstate_alert(payload: dict):
    """
    Simulates sending collaborative alert directives across state police departments.
    """
    syndicate_name = payload.get("syndicate_name", "Unknown")
    states = payload.get("states", [])
    return {
        "success": True,
        "message": f"Successfully issued Inter-State collaborative alert directive for '{syndicate_name}' to police departments in: {', '.join(states)}"
    }

