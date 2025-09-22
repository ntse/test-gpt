from fastapi.testclient import TestClient


def test_csv_import_create_and_update(client: TestClient, auth_headers: dict[str, str]) -> None:
    csv_data = (
        "name,owner_team,tier,lifecycle,endpoints,tags,id\n"
        "billing,FinOps,gold,production,https://example.com/api,critical;,\n"
    )

    response = client.post(
        "/api/v1/services/import",
        files={"file": ("services.csv", csv_data, "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 202
    result = response.json()
    assert result == {"created": 1, "updated": 0, "errors": [], "total_rows": 1}

    update_csv = (
        "name,owner_team,tier,lifecycle,endpoints,tags,id\n"
        "billing,Platform,gold,preprod,https://example.com/api,critical;billing;,\n"
    )

    update_resp = client.post(
        "/api/v1/services/import",
        files={"file": ("services.csv", update_csv, "text/csv")},
        headers=auth_headers,
    )
    assert update_resp.status_code == 202
    update_result = update_resp.json()
    assert update_result == {"created": 0, "updated": 1, "errors": [], "total_rows": 1}

    fetch = client.get("/api/v1/services", headers=auth_headers)
    assert fetch.status_code == 200
    data = fetch.json()
    assert data["items"][0]["owner_team"] == "Platform"
    assert "billing" in data["items"][0]["tags"]


def test_csv_import_invalid_column(client: TestClient, auth_headers: dict[str, str]) -> None:
    csv_data = (
        "name,owner_team,tier,lifecycle,endpoints,tags,unexpected\n"
        "billing,FinOps,gold,production,https://example.com/api,critical;,oops\n"
    )
    response = client.post(
        "/api/v1/services/import",
        files={"file": ("services.csv", csv_data, "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Unknown columns" in response.json()["detail"]
