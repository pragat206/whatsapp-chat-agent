"""Tests for health check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient):
    response = await client.get("/api/v1/live")
    assert response.status_code == 200
    assert response.json()["alive"] is True
