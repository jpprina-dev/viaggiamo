"""Tests for rate limiting on /graphql endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter
from slowapi.util import get_remote_address

import app.main as main_module
from app.main import create_application


@pytest.mark.asyncio
async def test_graphql_rate_limit_returns_429_when_exceeded(monkeypatch):
    """When the rate limit is exceeded, /graphql returns HTTP 429."""
    # Patch the limiter in main's namespace so create_application() picks it up
    test_limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["3/minute"],
    )
    monkeypatch.setattr(main_module, "limiter", test_limiter)

    # Create a fresh app instance so it picks up the patched limiter
    test_app = create_application()

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        query = {"query": "{ __typename }"}
        # 3 requests dentro del límite
        for _ in range(3):
            response = await client.post("/graphql", json=query)
            assert response.status_code == 200

        # 4ta request debería fallar con 429
        response = await client.post("/graphql", json=query)
        assert response.status_code == 429
        assert "rate limit" in response.text.lower()
