from fastapi import APIRouter
from .shield import router as shield_router
from .geospatial import router as geospatial_router
from .deepfake import router as deepfake_router

api_router = APIRouter()

api_router.include_router(shield_router, prefix="/shield", tags=["Shield Live Monitor"])
api_router.include_router(geospatial_router, prefix="/geospatial", tags=["Geospatial Crimes"])
api_router.include_router(deepfake_router, prefix="/deepfake", tags=["Deepfake Classifier"])
