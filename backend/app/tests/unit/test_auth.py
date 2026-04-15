"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "testadmin@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "testadmin@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "testpass123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testadmin@example.com"
    assert data["full_name"] == "Test Admin"


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No Bearer token


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_user):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "testadmin@example.com", "password": "testpass123"},
    )
    refresh = login_res.json()["refresh_token"]

    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()
