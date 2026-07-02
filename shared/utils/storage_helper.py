import os
from firebase_admin import storage
from datetime import timedelta
from typing import Optional
from .firebase_helper import initialize_firebase

def get_bucket():
    """Initializes Firebase Admin SDK if not already done, and returns default storage bucket. Falls back to a mock in DEBUG mode."""
    try:
        app = initialize_firebase()
        if app is None:
            raise ValueError("Firebase app not initialized")
        return storage.bucket()
    except Exception as e:
        if os.getenv("DEBUG") == "True":
            # Return a mock Storage bucket for local integration testing
            class MockBlob:
                def __init__(self, path):
                    self.path = path
                def upload_from_string(self, *args, **kwargs): pass
                def delete(self, *args, **kwargs): pass
                def generate_signed_url(self, *args, **kwargs):
                    return f"https://firebasestorage.googleapis.com/mock-bucket/{self.path}"
            class MockBucket:
                def blob(self, path):
                    return MockBlob(path)
            return MockBucket()
        raise e

def upload_file(
    file_bytes: bytes,
    storage_path: str,
    content_type: str
) -> str:
    """
    Core upload handler. Stores raw file bytes inside Firebase Storage.
    Returns path references.
    """
    bucket = get_bucket()
    blob = bucket.blob(storage_path)
    blob.upload_from_string(file_bytes, content_type=content_type)
    return storage_path

def upload_audio(file_bytes: bytes, storage_path: str) -> str:
    """Uploads call transcript sound recordings."""
    return upload_file(file_bytes, storage_path, "audio/mpeg")

def upload_image(file_bytes: bytes, storage_path: str) -> str:
    """Uploads banknote check visual files or screenshots."""
    return upload_file(file_bytes, storage_path, "image/png")

def upload_pdf(file_bytes: bytes, storage_path: str) -> str:
    """Uploads legally sealed forensic package PDFs."""
    return upload_file(file_bytes, storage_path, "application/pdf")

def delete_file(storage_path: str) -> bool:
    """Removes file blob from Storage path."""
    try:
        bucket = get_bucket()
        blob = bucket.blob(storage_path)
        blob.delete()
        return True
    except Exception:
        return False

def generate_signed_url(storage_path: str, expiration_seconds: int = 3600) -> str:
    """
    Generates a secure, temporary, public download link for the given Storage path.
    """
    bucket = get_bucket()
    blob = bucket.blob(storage_path)
    # Generate signed URL
    return blob.generate_signed_url(
        expiration=timedelta(seconds=expiration_seconds),
        method="GET"
    )
