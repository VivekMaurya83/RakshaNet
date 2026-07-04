from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from shared.utils import initialize_firebase

from fastapi.middleware.gzip import GZipMiddleware

# Init Firebase Admin SDK
initialize_firebase()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="RakshaNet Web Analytical Backend Service (Hackathon MVP)",
    version="1.0.0",
    debug=settings.DEBUG
)

# Gzip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "healthy",
        "version": "1.0.0"
    }
