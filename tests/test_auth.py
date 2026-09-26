import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "new@example.com",
        "password": "password123",
    }

    first_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    second_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "User with this email already exists"
    )


@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_me(client, auth_headers):
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_monitors_without_token(client):
    response = await client.get("/api/monitors")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_with_invalid_token(client):
    response = await client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"


@pytest.mark.asyncio
async def test_me_with_token_for_missing_user(client):
    from app.core.security import create_access_token

    token = create_access_token(999999)

    response = await client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"