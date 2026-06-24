from typing import List
from shared.models import FraudNode, FraudEdge
from .firestore_repository import FirestoreRepository

class GraphRepository:
    def __init__(self):
        self.firestore = FirestoreRepository()

    def get_nodes(self) -> List[FraudNode]:
        """Fetches all fraud nodes."""
        data = self.firestore.list_documents("fraud_nodes")
        return [FraudNode(**item) for item in data]

    def get_edges(self) -> List[FraudEdge]:
        """Fetches all edges."""
        data = self.firestore.list_documents("fraud_edges")
        return [FraudEdge(**item) for item in data]

    def upsert_node(self, node: FraudNode) -> None:
        """Saves node to collection."""
        self.firestore.create_document("fraud_nodes", node.id, node.model_dump())

    def create_edge(self, edge: FraudEdge) -> None:
        """Saves edge link to collection."""
        self.firestore.create_document("fraud_edges", edge.id, edge.model_dump())
