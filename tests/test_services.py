from uuid import UUID

from fastapi.testclient import TestClient


def _create_payload(name: str, owner: str = "Team A") -> dict[str, object]:
    return {
        "name": name,
        "owner_team": owner,
        "tier": "gold",
        "lifecycle": "production",
        "endpoints": ["https://example.com/api"],
        "tags": ["payments", "critical"],
    }


def test_create_and_get_service(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/api/v1/services", json=_create_payload("billing"), headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    service_id = data["id"]

    get_response = client.get(f"/api/v1/services/{service_id}", headers=auth_headers)
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["name"] == "billing"
    assert fetched["owner_team"] == "Team A"
    UUID(service_id)


def test_update_and_delete_service(client: TestClient, auth_headers: dict[str, str]) -> None:
    create = client.post("/api/v1/services", json=_create_payload("payments"), headers=auth_headers)
    service_id = create.json()["id"]

    update_payload = {"owner_team": "Team B", "lifecycle": "deprecated"}
    update_resp = client.put(
        f"/api/v1/services/{service_id}", json=update_payload, headers=auth_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["owner_team"] == "Team B"
    assert update_resp.json()["lifecycle"] == "deprecated"

    delete_resp = client.delete(f"/api/v1/services/{service_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    missing = client.get(f"/api/v1/services/{service_id}", headers=auth_headers)
    assert missing.status_code == 404


def test_list_filters_and_search(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/api/v1/services", json=_create_payload("billing", "FinOps"), headers=auth_headers)
    client.post(
        "/api/v1/services",
        json={
            "name": "analytics",
            "owner_team": "Data",
            "tier": "silver",
            "lifecycle": "production",
            "endpoints": ["https://example.com/analytics"],
            "tags": ["reporting"],
        },
        headers=auth_headers,
    )

    list_resp = client.get(
        "/api/v1/services",
        params={"owner_team": "FinOps"},
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "billing"

    search_resp = client.get(
        "/api/v1/services",
        params={"search": "report"},
        headers=auth_headers,
    )
    assert search_resp.status_code == 200
    search_payload = search_resp.json()
    assert search_payload["total"] == 1
    assert search_payload["items"][0]["name"] == "analytics"


def test_auth_required(client: TestClient) -> None:
    response = client.get("/api/v1/services")
    assert response.status_code == 401
