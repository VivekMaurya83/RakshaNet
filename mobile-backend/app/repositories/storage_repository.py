from shared.utils import upload_audio, generate_signed_url, delete_file

class StorageRepository:
    def upload_call_recording(self, file_bytes: bytes, report_id: str) -> str:
        """Saves recorded call audio files inside audio/ folder."""
        path = f"audio/{report_id}/recording.mp3"
        return upload_audio(file_bytes, path)

    def get_download_link(self, storage_path: str) -> str:
        return generate_signed_url(storage_path)
