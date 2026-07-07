def _token_for(client, username: str, password: str) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]


def test_list_logs_requires_auth(client):
    response = client.get("/logs")
    assert response.status_code == 401


def test_viewer_can_list_logs(client):
    token = _token_for(client, "viewer", "123456")
    response = client.get("/logs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_viewer_cannot_download(client):
    token = _token_for(client, "viewer", "123456")
    response = client.get("/logs/access.log", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_can_download(client):
    token = _token_for(client, "admin", "123456")
    response = client.get("/logs/access.log", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
