from typing import Dict, Any, List, Optional
from shared.utils import get_db

class FirestoreRepository:
    def __init__(self):
        self.db = get_db()

    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single document as dictionary."""
        doc_ref = self.db.collection(collection).document(doc_id).get()
        return doc_ref.to_dict() if doc_ref.exists else None

    def create_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Saves a document using a specific ID."""
        self.db.collection(collection).document(doc_id).set(data)

    def add_document(self, collection: str, data: Dict[str, Any]) -> str:
        """Appends document generating auto ID. Returns string ID."""
        _, doc_ref = self.db.collection(collection).add(data)
        return doc_ref.id

    def list_documents(self, collection: str) -> List[Dict[str, Any]]:
        """Lists all items in collection."""
        docs = self.db.collection(collection).stream()
        return [doc.to_dict() for doc in docs]
