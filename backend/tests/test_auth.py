def test_login_success(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "123456"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_password(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401
