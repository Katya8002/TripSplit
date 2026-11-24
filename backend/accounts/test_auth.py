import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
ME_URL = "/api/auth/me/"


@pytest.fixture
def api():
    return APIClient()


def test_register_hashes_password(api, db):
    response = api.post(
        REGISTER_URL,
        {"username": "anna", "email": "a@a.com", "password": "StrongPass123"},
        format="json",
    )
    assert response.status_code == 201
    assert "password" not in response.data
    user = User.objects.get(username="anna")
    assert user.password != "StrongPass123"
    assert user.check_password("StrongPass123")


def test_register_rejects_weak_password(api, db):
    response = api.post(
        REGISTER_URL, {"username": "anna", "password": "123"}, format="json"
    )
    assert response.status_code == 400


def test_login_returns_tokens(api, db):
    User.objects.create_user(username="anna", password="StrongPass123")
    response = api.post(
        LOGIN_URL, {"username": "anna", "password": "StrongPass123"}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_me_requires_token(api, db):
    assert api.get(ME_URL).status_code == 401


def test_me_with_token(api, db):
    User.objects.create_user(username="anna", password="StrongPass123")
    tokens = api.post(
        LOGIN_URL, {"username": "anna", "password": "StrongPass123"}, format="json"
    ).data
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api.get(ME_URL)
    assert response.status_code == 200
    assert response.data["username"] == "anna"