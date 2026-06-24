from shared.models import NetworkGraphPayload, FraudNode, FraudEdge
from app.repositories.graph_repository import GraphRepository

class GraphService:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def get_react_flow_network(self) -> NetworkGraphPayload:
        """Loads and returns the network nodes and edges from Firestore."""
        nodes = self.graph_repo.get_nodes()
        edges = self.graph_repo.get_edges()
        return NetworkGraphPayload(nodes=nodes, edges=edges)

    def add_node(self, node: FraudNode) -> FraudNode:
        """Upserts a fraud node."""
        self.graph_repo.upsert_node(node)
        return node

    def add_edge(self, edge: FraudEdge) -> FraudEdge:
        """Adds a graph relationship edge link."""
        self.graph_repo.create_edge(edge)
        return edge
