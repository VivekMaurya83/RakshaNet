from shared.utils import upload_audio, upload_image, upload_pdf, delete_file, generate_signed_url

class StorageRepository:
    def upload_screenshot_file(self, file_bytes: bytes, report_id: str) -> str:
        """Saves case chat/evidence screenshots to screenshots/ folder."""
        path = f"screenshots/{report_id}.png"
        return upload_image(file_bytes, path)

    def upload_banknote_file(self, file_bytes: bytes, scan_id: str) -> str:
        """Saves scanned note photos to currency-images/ folder."""
        path = f"currency-images/{scan_id}/note.jpg"
        return upload_image(file_bytes, path)

    def upload_evidence_pdf(self, file_bytes: bytes, evidence_id: str) -> str:
        """Saves generated briefs to evidence-pdfs/ folder."""
        path = f"evidence-pdfs/{evidence_id}/report.pdf"
        return upload_pdf(file_bytes, path)

    def get_download_link(self, storage_path: str) -> str:
        """Generates signed access URL."""
        return generate_signed_url(storage_path)

    def remove_file(self, storage_path: str) -> bool:
        """Deletes file from bucket."""
        return delete_file(storage_path)
