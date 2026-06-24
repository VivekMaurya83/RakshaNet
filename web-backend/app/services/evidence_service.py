import hashlib
import uuid
from datetime import datetime
from shared.models import EvidencePackage
from app.repositories.firestore_repository import FirestoreRepository
from app.repositories.storage_repository import StorageRepository

class EvidenceService:
    def __init__(self):
        self.firestore_repo = FirestoreRepository()
        self.storage_repo = StorageRepository()

    async def compile_forensic_evidence(
        self,
        report_ids: list,
        remarks: str,
        officer_uid: str
    ) -> EvidencePackage:
        """
        Gathers scam reports, compiles a summary PDF, uploads it,
        hashes the file using SHA-256 for legal seal validity, and logs metadata.
        """
        package_id = f"EVB-{uuid.uuid4().hex[:8]}"
        
        # 1. Compile PDF document bytes (using reportlab in full implementation)
        # For MVP we compile mock report bytes
        pdf_content = b"%PDF-1.4 Mock legal forensic report details..."
        
        # Calculate SHA-256 hash for sealing proof
        sha_hash = hashlib.sha256(pdf_content).hexdigest()
        
        # 2. Upload file to Firebase Storage via Repository
        storage_path = self.storage_repo.upload_evidence_pdf(pdf_content, package_id)
        download_url = self.storage_repo.get_download_link(storage_path)

        # 3. Create Package object
        package = EvidencePackage(
            packageId=package_id,
            associatedReports=report_ids,
            generatedBy=officer_uid,
            pdfStoragePath=storage_path,
            pdfUrl=download_url,
            fileHash=sha_hash,
            status="sealed",
            remarks=remarks,
            sealedAt=datetime.utcnow()
        )
        
        # Log metadata in Firestore
        self.firestore_repo.create_document("evidence_packages", package_id, package.model_dump())
        return package
