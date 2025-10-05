"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.graphql.context import get_context
from app.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # GraphQL endpoint
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Viaggiamo API - MVP de Carpooling"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
