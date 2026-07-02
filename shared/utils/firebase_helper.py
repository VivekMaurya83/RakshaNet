import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

# Token Bearer setup
security_agent = HTTPBearer()

def initialize_firebase() -> firebase_admin.App:
    """Initializes Firebase Admin SDK using application credentials or defaults."""
    try:
        # Check if already initialized to avoid ValueError
        return firebase_admin.get_app()
    except ValueError:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            return firebase_admin.initialize_app(cred)
        else:
            # In debug mode, if no credentials file exists, do not try default credentials
            # as it can block/hang attempting to contact the GCP metadata server.
            if os.getenv("DEBUG") == "True":
                print("WARNING: Running in DEBUG mode without Firebase credentials file. Using mock services.")
                return None
            # Fallback to default credentials (useful for server environments e.g., GCP)
            return firebase_admin.initialize_app()

def get_db() -> Any:
    """Returns Firestore Client. Falls back to a mock client in DEBUG mode if credentials are missing."""
    try:
        app = initialize_firebase()
        if app is None:
            raise ValueError("Firebase app not initialized")
        return firestore.client()
    except Exception as e:
        if os.getenv("DEBUG") == "True":
            # Return a mock Firestore Client for local integration testing
            class MockDocument:
                def set(self, *args, **kwargs): pass
                def get(self, *args, **kwargs):
                    class MockSnapshot:
                        exists = False
                        def to_dict(self): return None
                    return MockSnapshot()
            class MockCollection:
                def document(self, *args, **kwargs):
                    return MockDocument()
                def add(self, *args, **kwargs):
                    class MockDocRef:
                        id = "MOCK_AUTO_DOC_ID"
                    return None, MockDocRef()
                def stream(self):
                    return []
            class MockFirestoreClient:
                def collection(self, *args, **kwargs):
                    return MockCollection()
            return MockFirestoreClient()
        raise e

async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security_agent)
) -> Dict[str, Any]:
    """
    Middleware dependency to verify incoming Firebase Auth JWT.
    Returns decoded user token dictionary. Bypasses check if DEBUG=True.
    """
    if os.getenv("DEBUG") == "True":
        return {
            "uid": "MOCK_USER_12345",
            "email": "test.officer@gov.in",
            "role": "analyst"
        }

    initialize_firebase()
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired authentication credentials. Error: {str(e)}"
        )
