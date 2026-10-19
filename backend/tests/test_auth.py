"""Testi prijave (/api/auth/login) in podatkov o prijavljenem uporabniku (/api/auth/me)."""
from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token, decode_token

from app.extensions import db
from app.models import User


def login(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password})


# --- prijava ---


def test_login_returns_token_and_user(client, make_user, password):
    make_user("admin", is_admin=True)

    response = login(client, "admin", password)
    body = response.get_json()

    assert response.status_code == 200
    assert body["access_token"]
    assert body["user"]["username"] == "admin"
    assert body["user"]["is_admin"] is True
    assert "password" not in str(body)


@pytest.mark.parametrize("is_admin", [True, False])
def test_login_token_contains_identity_and_admin_claim(app, client, make_user, password, is_admin):
    user_id = make_user("uporabnik", is_admin=is_admin)

    token = login(client, "uporabnik", password).get_json()["access_token"]
    with app.app_context():
        claims = decode_token(token)

    assert claims["sub"] == str(user_id)
    assert claims["is_admin"] is is_admin


def test_login_wrong_password_and_unknown_user_give_same_error(client, make_user):
    make_user("admin")

    wrong_password = login(client, "admin", "napacno-geslo")
    unknown_user = login(client, "ne-obstaja", "napacno-geslo")

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.get_json() == unknown_user.get_json()


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"username": "admin"},
        {"password": "geslo1234"},
        {"username": "", "password": ""},
        {"username": 1, "password": 2},
        [],
        "besedilo",
    ],
)
def test_login_rejects_bad_input(client, body):
    response = client.post("/api/auth/login", json=body)

    assert response.status_code == 400


def test_login_rejects_non_json_body(client):
    response = client.post("/api/auth/login", data="abc", content_type="text/plain")

    assert response.status_code == 400


# --- /api/auth/me ---


def test_me_returns_logged_in_user(client, make_user, password):
    make_user("admin", is_admin=True)
    token = login(client, "admin", password).get_json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.get_json()["username"] == "admin"
    assert response.get_json()["is_admin"] is True


def test_me_requires_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"})

    assert response.status_code == 401


def test_me_rejects_expired_token(app, client, make_user):
    user_id = make_user("admin")
    with app.app_context():
        token = create_access_token(str(user_id), expires_delta=timedelta(seconds=-1))

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_rejects_token_of_deleted_user(app, client, make_user, auth_headers):
    user_id = make_user("janez")
    headers = auth_headers(user_id)
    with app.app_context():
        db.session.delete(db.session.get(User, user_id))
        db.session.commit()

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
