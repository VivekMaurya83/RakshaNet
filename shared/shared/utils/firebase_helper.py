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
            # Fallback to default credentials (useful for server environments e.g., GCP)
            return firebase_admin.initialize_app()

def get_db() -> firestore.firestore.Client:
    """Returns Firestore Client."""
    initialize_firebase()
    return firestore.client()

async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security_agent)
) -> Dict[str, Any]:
    """
    Middleware dependency to verify incoming Firebase Auth JWT.
    Returns decoded user token dictionary.
    """
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
