import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "service" in data


@pytest.mark.asyncio
async def test_create_monitor(client):
    response = await client.post(
        "/api/monitors",
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Example"
    assert data["url"] == "https://example.com/"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_monitors(client):
    await client.post(
        "/api/monitors",
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    response = await client.get("/api/monitors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Example"


@pytest.mark.asyncio
async def test_duplicate_monitor_url(client):
    payload = {
        "name": "Example",
        "url": "https://example.com",
    }

    first_response = await client.post(
        "/api/monitors",
        json=payload,
    )

    second_response = await client.post(
        "/api/monitors",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Monitor with this URL already exists"
    )


@pytest.mark.asyncio
async def test_get_missing_monitor(client):
    response = await client.get("/api/monitors/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor(client):
    create_response = await client.post(
        "/api/monitors",
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/monitors/{monitor_id}",
        json={
            "name": "Updated example",
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated example"
    assert data["is_active"] is False
    assert data["url"] == "https://example.com/"


@pytest.mark.asyncio
async def test_delete_monitor(client):
    create_response = await client.post(
        "/api/monitors",
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/monitors/{monitor_id}",
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/monitors/{monitor_id}",
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_history_missing_monitor(client):
    response = await client.get(
        "/api/monitors/999/history",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stats_missing_monitor(client):
    response = await client.get(
        "/api/monitors/999/stats",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_stats_period(client):
    create_response = await client.post(
        "/api/monitors",
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.get(
        f"/api/monitors/{monitor_id}/stats?period=invalid",
    )

    assert response.status_code == 400
    assert "Invalid period" in response.json()["detail"]