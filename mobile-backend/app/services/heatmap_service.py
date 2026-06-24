from datetime import datetime
from shared.models import GeoLocation
from app.repositories.firestore_repository import FirestoreRepository

class HeatmapService:
    def __init__(self):
        self.firestore_repo = FirestoreRepository()

    def log_report_location(
        self,
        location: GeoLocation,
        crime_type: str,
        reporter_uid: str
    ) -> str:
        """Saves physical safety coordinate pins to update heatmaps."""
        data = {
            "reportedBy": reporter_uid,
            "crimeType": crime_type,
            "geopoint": {"latitude": location.latitude, "longitude": location.longitude},
            "timestamp": datetime.utcnow().isoformat()
        }
        doc_id = self.firestore_repo.add_document("crime_locations", data)
        return doc_id
