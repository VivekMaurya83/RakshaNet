from fastapi import APIRouter, Depends
from typing import Dict
from shared.utils import verify_firebase_token
from shared.models import NetworkGraphPayload, FraudNode, FraudEdge
from app.services.graph_service import GraphService

router = APIRouter()
graph_service = GraphService()

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
