import time
from fastapi import FastAPI, Request
from app.api import claims, customers, health, reports, upload
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.core.logging import get_logger, setup_logging
from app.models.database import Base, engine

setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-quality REST API for processing insurance claim data.",
        version="1.0.0",
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info("%s %s %d %.2fms", request.method, request.url.path, response.status_code, duration)
        return response

    app.include_router(upload.router)
    app.include_router(claims.router)
    app.include_router(customers.router)
    app.include_router(reports.router)
    app.include_router(health.router)

    return app


app = create_app()
