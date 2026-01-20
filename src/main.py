"""
HR Policy Advisor - Main Application Entry Point.

FastAPI application for AI-powered HR policy design with
Human-in-the-Loop approval workflows.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import (
    HealthResponse,
    RequestLoggingMiddleware,
    companies_router,
    policies_router,
    reviews_router,
)
from src.config import get_settings
from src.services import (
    close_rabbitmq_client,
    close_redis_client,
    get_rabbitmq_client,
    get_redis_client,
)
from src.utils import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    settings = get_settings()

    logger.info(
        "app_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        env=settings.env,
    )

    # Connect to services
    try:
        await get_redis_client()
        logger.info("redis_connected")
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e))

    try:
        await get_rabbitmq_client()
        logger.info("rabbitmq_connected")
    except Exception as e:
        logger.warning("rabbitmq_connection_failed", error=str(e))

    logger.info("app_started")

    yield

    # Shutdown
    logger.info("app_stopping")

    await close_redis_client()
    await close_rabbitmq_client()

    logger.info("app_stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered HR policy design advisor with Human-in-the-Loop",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app.include_router(companies_router, prefix="/api/v1")
    app.include_router(policies_router, prefix="/api/v1")
    app.include_router(reviews_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            environment=settings.env,
        )

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs" if settings.is_development else "disabled",
        }

    return app


# Create the app instance
app = create_app()


def main() -> None:
    """Run the application with uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
