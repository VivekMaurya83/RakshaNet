from fastapi import APIRouter
from .network import router as network_router
from .evidence import router as evidence_router
from .analytics import router as analytics_router
from .currency import router as currency_router

api_router = APIRouter()

api_router.include_router(network_router, prefix="/network", tags=["Network Graph Analysis"])
api_router.include_router(evidence_router, prefix="/evidence", tags=["Forensic Evidence Package"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Dashboard Metrics"])
api_router.include_router(currency_router, prefix="/currency", tags=["Banknote Scan"])
