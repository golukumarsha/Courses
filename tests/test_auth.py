"""
tests/test_auth.py
Authentication endpoints ke tests
"""
import pytest


class TestRegister:
    """POST /auth/register"""

    def test_register_success(self, client):
        res = client.post("/auth/register", json={
            "username": "newuser1",
            "email":    "newuser1@example.com",
            "password": "NewUser@123",
            "role":     "user"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "newuser1"
        assert data["email"] == "newuser1@example.com"
        assert data["role"] == "user"
        assert "id" in data

    def test_register_admin(self, client):
        res = client.post("/auth/register", json={
            "username": "adminuser2",
            "email":    "adminuser2@example.com",
            "password": "Admin@1234",
            "role":     "admin"
        })
        assert res.status_code == 200
        assert res.json()["role"] == "admin"

    def test_register_duplicate_email(self, client):
        payload = {
            "username": "dupuser",
            "email":    "dup@example.com",
            "password": "Dup@12345",
            "role":     "user"
        }
        client.post("/auth/register", json=payload)
        res = client.post("/auth/register",
                          json={**payload, "username": "dupuser2"})
        assert res.status_code == 400
        assert "email" in res.json()["detail"].lower()

    def test_register_duplicate_username(self, client):
        payload = {
            "username": "sameuser",
            "email":    "sameuser@example.com",
            "password": "Same@12345",
            "role":     "user"
        }
        client.post("/auth/register", json=payload)
        res = client.post("/auth/register",
                          json={**payload, "email": "different@example.com"})
        assert res.status_code == 400
        assert "username" in res.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        res = client.post("/auth/register", json={
            "username": "baduser",
            "email":    "not-an-email",
            "password": "Bad@12345",
            "role":     "user"
        })
        assert res.status_code == 422

    def test_register_weak_password(self, client):
        res = client.post("/auth/register", json={
            "username": "weakpass",
            "email":    "weakpass@example.com",
            "password": "123",       # too short, no uppercase, no special
            "role":     "user"
        })
        assert res.status_code == 422

    def test_register_invalid_role(self, client):
        res = client.post("/auth/register", json={
            "username": "badrole",
            "email":    "badrole@example.com",
            "password": "Bad@12345",
            "role":     "superuser"
        })
        assert res.status_code == 422

    def test_register_missing_fields(self, client):
        res = client.post("/auth/register", json={"username": "onlyname"})
        assert res.status_code == 422


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client):
        # Register first
        client.post("/auth/register", json={
            "username": "loginuser",
            "email":    "loginuser@example.com",
            "password": "Login@1234",
            "role":     "user"
        })
        res = client.post("/auth/login", json={
            "email":    "loginuser@example.com",
            "password": "Login@1234"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "loginuser"
        assert data["role"] == "user"

    def test_login_wrong_password(self, client):
        res = client.post("/auth/login", json={
            "email":    "testadmin@example.com",
            "password": "WrongPass@999"
        })
        assert res.status_code == 401

    def test_login_wrong_email(self, client):
        res = client.post("/auth/login", json={
            "email":    "nobody@example.com",
            "password": "Any@12345"
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/auth/login", json={"email": "test@test.com"})
        assert res.status_code == 422


class TestMe:
    """GET /auth/me"""

    def test_get_me_success(self, client, user_headers):
        res = client.get("/auth/me", headers=user_headers)
        assert res.status_code == 200
        data = res.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data

    def test_get_me_no_token(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 403

    def test_get_me_invalid_token(self, client):
        res = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert res.status_code == 401


class TestGetAllUsers:
    """GET /auth/users"""

    def test_admin_can_get_users(self, client, admin_headers):
        res = client.get("/auth/users", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_user_cannot_get_users(self, client, user_headers):
        res = client.get("/auth/users", headers=user_headers)
        assert res.status_code == 403
