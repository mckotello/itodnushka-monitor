import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "service" in data


@pytest.mark.asyncio
async def test_create_monitor(client, auth_headers):
    response = await client.post(
        "/api/monitors",
        headers=auth_headers,
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
async def test_list_monitors(client, auth_headers):
    await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    response = await client.get(
        "/api/monitors",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Example"


@pytest.mark.asyncio
async def test_duplicate_monitor_url(client, auth_headers):
    payload = {
        "name": "Example",
        "url": "https://example.com",
    }

    first_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json=payload,
    )

    second_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Monitor with this URL already exists"
    )


@pytest.mark.asyncio
async def test_get_missing_monitor(client, auth_headers):
    response = await client.get(
        "/api/monitors/999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitor not found"


@pytest.mark.asyncio
async def test_update_monitor(client, auth_headers):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/monitors/{monitor_id}",
        headers=auth_headers,
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
async def test_delete_monitor(client, auth_headers):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/monitors/{monitor_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/monitors/{monitor_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_history_missing_monitor(client, auth_headers):
    response = await client.get(
        "/api/monitors/999/history",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stats_missing_monitor(client, auth_headers):
    response = await client.get(
        "/api/monitors/999/stats",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_stats_period(client, auth_headers):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.get(
        f"/api/monitors/{monitor_id}/stats?period=invalid",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Invalid period" in response.json()["detail"]


@pytest.mark.asyncio
async def test_history_status_filter(client, db_session, auth_headers):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Example",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    from app.models.monitor import CheckResult

    db_session.add_all(
        [
            CheckResult(
                monitor_id=monitor_id,
                status="up",
                status_code=200,
                response_time_ms=100,
            ),
            CheckResult(
                monitor_id=monitor_id,
                status="down",
                status_code=500,
                response_time_ms=300,
            ),
        ]
    )

    await db_session.commit()

    response = await client.get(
        f"/api/monitors/{monitor_id}/history"
        "?status_filter=down",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "down"
    assert data[0]["status_code"] == 500

@pytest.mark.asyncio
async def test_user_cannot_see_other_users_monitor(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Private monitor",
            "url": "https://example.com",
        },
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    response = await client.get(
        f"/api/monitors/{monitor_id}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_list_contains_only_own_monitors(
    client,
    auth_headers,
    second_auth_headers,
):
    await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "User 1 monitor",
            "url": "https://example.com",
        },
    )

    await client.post(
        "/api/monitors",
        headers=second_auth_headers,
        json={
            "name": "User 2 monitor",
            "url": "https://example.org",
        },
    )

    first_response = await client.get(
        "/api/monitors",
        headers=auth_headers,
    )

    second_response = await client.get(
        "/api/monitors",
        headers=second_auth_headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_monitors = first_response.json()
    second_monitors = second_response.json()

    assert len(first_monitors) == 1
    assert first_monitors[0]["name"] == "User 1 monitor"

    assert len(second_monitors) == 1
    assert second_monitors[0]["name"] == "User 2 monitor"


@pytest.mark.asyncio
async def test_user_cannot_update_other_users_monitor(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Private monitor",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/monitors/{monitor_id}",
        headers=second_auth_headers,
        json={
            "name": "Hacked monitor",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_other_users_monitor(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "Private monitor",
            "url": "https://example.com",
        },
    )

    monitor_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/monitors/{monitor_id}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

    owner_response = await client.get(
        f"/api/monitors/{monitor_id}",
        headers=auth_headers,
    )

    assert owner_response.status_code == 200

@pytest.mark.asyncio
async def test_different_users_can_use_same_monitor_url(
    client,
    auth_headers,
    second_auth_headers,
):
    first_response = await client.post(
        "/api/monitors",
        headers=auth_headers,
        json={
            "name": "User 1",
            "url": "https://example.com",
        },
    )

    second_response = await client.post(
        "/api/monitors",
        headers=second_auth_headers,
        json={
            "name": "User 2",
            "url": "https://example.com",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert (
        first_response.json()["id"]
        != second_response.json()["id"]
    )