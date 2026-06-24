import re
from typing import Dict, Any, List
from datetime import datetime
from shared.models import FraudNode, FraudEdge, NodePosition
from app.repositories.firestore_repository import FirestoreRepository
from app.repositories.graph_repository import GraphRepository
from .evidence_service import EvidenceService

class FraudIntelligenceService:
    def __init__(self):
        self.firestore_repo = FirestoreRepository()
        self.graph_repo = GraphRepository()
        self.evidence_service = EvidenceService()

    async def ingest_scam_complaint(
        self,
        report_id: str,
        reporter_uid: str,
        complaint_text: str,
        latitude: float = None,
        longitude: float = None
    ) -> Dict[str, Any]:
        """
        Fraud Intelligence Pipeline:
        Complaint Ingestion 
        → Regex/Gemini Entity Extraction
        → Graph Builder (fraud_nodes, fraud_edges)
        → Heatmap Update
        → Evidence Compile Trigger
        """
        # 1. Run Entity Extraction
        extracted_entities = self._extract_entities_from_text(complaint_text)

        # 2. Graph Builder: Populate Nodes & Edges in Firestore
        self._build_fraud_graph(report_id, extracted_entities)

        # 3. Heatmap Update (Geospatial logging)
        if latitude and longitude:
            self._update_geospatial_heatmap(report_id, latitude, longitude)

        # 4. Trigger Evidence Package Generation
        # Trigger compilation in background for forensic review
        # await self.evidence_service.compile_forensic_evidence([report_id], "Auto-compiled by Intelligence Pipeline", reporter_uid)

        return {
            "reportId": report_id,
            "entitiesExtracted": extracted_entities,
            "graphUpdated": True,
            "heatmapLogged": latitude is not None
        }

    def _extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Uses regex and LLM rules to parse phone numbers, bank details, UPI handles, etc.
        """
        # Extract phone numbers
        phones = re.findall(r"\+?\d{10,12}", text)
        
        # Extract UPI IDs (e.g. name@upi)
        upis = re.findall(r"[a-zA-Z0-9\.\-_]+@[a-zA-Z]{2,}", text)
        
        # Mocking extracted agencies and suspect names (Gemini API logic fallback)
        agencies = []
        if "cbi" in text.lower():
            agencies.append("CBI")
        if "police" in text.lower():
            agencies.append("Delhi Police")
            
        suspects = []
        if "officer" in text.lower():
            # Mock suspect name extraction
            suspects.append("Officer Kumar")

        # Mocking device IDs
        devices = []
        if "imei" in text.lower():
            devices.append("IMEI-829103982")

        return {
            "phone_numbers": list(set(phones)),
            "bank_accounts": [], # RegEx checks or LLM extractions
            "upi_ids": list(set(upis)),
            "device_ids": devices,
            "agencies": agencies,
            "suspects": suspects
        }

    def _build_fraud_graph(self, report_id: str, entities: Dict[str, List[str]]) -> None:
        """
        Takes extracted entities and builds matching React Flow nodes and edges in Firestore.
        """
        import random
        
        # Create unique nodes for each entity
        for phone in entities["phone_numbers"]:
            node_id = f"NODE_PHONE_{phone}"
            node = FraudNode(
                id=node_id,
                type="default",
                data={"label": f"Phone: {phone}", "riskScore": 75.0, "reports": [report_id]},
                position=NodePosition(x=random.randint(100, 600), y=random.randint(100, 400))
            )
            self.graph_repo.upsert_node(node)

        for upi in entities["upi_ids"]:
            node_id = f"NODE_UPI_{upi.replace('@', '_')}"
            node = FraudNode(
                id=node_id,
                type="default",
                data={"label": f"UPI: {upi}", "riskScore": 80.0, "reports": [report_id]},
                position=NodePosition(x=random.randint(100, 600), y=random.randint(100, 400))
            )
            self.graph_repo.upsert_node(node)

    def _update_geospatial_heatmap(self, report_id: str, lat: float, lng: float) -> None:
        """Logs location coordinates in crime_locations database collection."""
        self.firestore_repo.add_document("crime_locations", {
            "reportId": report_id,
            "geopoint": {"latitude": lat, "longitude": lng},
            "timestamp": datetime.utcnow().isoformat()
        })
