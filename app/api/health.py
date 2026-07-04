from fastapi import APIRouter
from app.schemas.schemas import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API status, database connectivity, and application uptime.",
)
def health_check():
    return HealthService().get_health()
