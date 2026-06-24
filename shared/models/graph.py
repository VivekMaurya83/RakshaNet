from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NodePosition(BaseModel):
    x: float = Field(0.0, description="Horizontal coordinate on React Flow canvas")
    y: float = Field(0.0, description="Vertical coordinate on React Flow canvas")

class FraudNode(BaseModel):
    id: str = Field(..., description="Unique node identifier (Match React Flow 'id')")
    type: str = Field("default", description="React Flow node visual type: input, output, default")
    data: Dict[str, Any] = Field(..., description="Payload data: label, riskScore, etc.")
    position: NodePosition = Field(default_factory=NodePosition)
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class FraudEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier (Match React Flow 'id')")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge display label")
    type: str = Field("smoothstep", description="React Flow connector type: straight, smoothstep, etc.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Metadata: weight, lastObserved")
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class NetworkGraphPayload(BaseModel):
    nodes: List[FraudNode]
    edges: List[FraudEdge]
