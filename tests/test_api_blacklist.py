"""Tests HTTP: health, autenticación, POST y GET de blacklist."""

import json


def test_health_returns_200_and_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok"}


def test_post_without_bearer_returns_401(client):
    response = client.post(
        "/blacklists",
        data=json.dumps({"email": "a@b.com", "app_uuid": "550e8400-e29b-41d4-a716-446655440000"}),
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Token de autorización requerido"


def test_post_with_invalid_token_returns_401(client, auth_headers):
    bad_headers = {**auth_headers, "Authorization": "Bearer wrong-token"}
    response = client.post(
        "/blacklists",
        json={
            "email": "user@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
        },
        headers=bad_headers,
    )
    assert response.status_code == 401
    assert response.get_json()["msg"] == "Token inválido"


def test_post_valid_body_returns_201(client, auth_headers):
    response = client.post(
        "/blacklists",
        json={
            "email": "newuser@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440001",
            "blocked_reason": "spam",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.get_json()["msg"] == "El email fue agregado a la lista negra"


def test_post_duplicate_email_returns_409(client, auth_headers):
    body = {
        "email": "dup@example.com",
        "app_uuid": "550e8400-e29b-41d4-a716-446655440002",
    }
    r1 = client.post("/blacklists", json=body, headers=auth_headers)
    assert r1.status_code == 201
    r2 = client.post("/blacklists", json=body, headers=auth_headers)
    assert r2.status_code == 409
    assert r2.get_json()["msg"] == "El email ya existe en la lista negra"


def test_post_invalid_email_returns_400_with_errors(client, auth_headers):
    response = client.post(
        "/blacklists",
        json={
            "email": "not-an-email",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440003",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["msg"] == "Datos de entrada inválidos"
    assert "errors" in data
    assert "email" in data["errors"]


def test_post_missing_required_fields_returns_400(client, auth_headers):
    response = client.post(
        "/blacklists",
        json={"email": "only@email.com"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["msg"] == "Datos de entrada inválidos"
    assert "errors" in data
    assert "app_uuid" in data["errors"]


def test_post_blocked_reason_over_255_returns_400(client, auth_headers):
    response = client.post(
        "/blacklists",
        json={
            "email": "long@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440004",
            "blocked_reason": "x" * 256,
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["msg"] == "Datos de entrada inválidos"
    assert "errors" in data
    assert "blocked_reason" in data["errors"]


def test_get_email_not_in_list_returns_blacklisted_false(client, auth_headers):
    response = client.get(
        "/blacklists/absent@example.com",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["blacklisted"] is False
    assert data["blocked_reason"] is None


def test_get_email_after_post_returns_blacklisted_true_and_reason(client, auth_headers):
    email = "listed@example.com"
    reason = "fraude"
    client.post(
        "/blacklists",
        json={
            "email": email,
            "app_uuid": "550e8400-e29b-41d4-a716-446655440005",
            "blocked_reason": reason,
        },
        headers=auth_headers,
    )
    response = client.get(f"/blacklists/{email}", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["blacklisted"] is True
    assert data["blocked_reason"] == reason
