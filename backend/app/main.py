"""Main FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.core.database import create_tables
from app.graphql.context import get_context
from app.graphql.mock_context import get_mock_context
from app.graphql.schema import schema

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    if settings.USE_MOCK_DATA:
        logger.info("🚀 Starting Viaggiamo API in MOCK DATA mode")
        logger.info(f"📁 Mock data path: {settings.MOCK_DATA_PATH}")
    else:
        logger.info("🚀 Starting Viaggiamo API in DATABASE mode")
        await create_tables()
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
    )

    # CORS middleware - must be added BEFORE routes
    cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Choose context getter based on mock data setting
    context_getter = get_mock_context if settings.USE_MOCK_DATA else get_context

    # GraphQL endpoint with dependency injection context
    # graphiql=True enables the GraphQL IDE
    graphql_app = GraphQLRouter(
        schema,
        context_getter=context_getter,
        graphql_ide="graphiql",
    )
    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Viaggiamo GraphQL API - MVP de Carpooling"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
