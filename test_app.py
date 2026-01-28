import os
import sqlite3
import tempfile
import pytest
import app as app_module
from app import app, bcrypt


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app_module.DATABASE = db_path
    app.config["TESTING"] = True

    hashed_pw1 = bcrypt.generate_password_hash("pass1").decode("utf-8")
    hashed_pw2 = bcrypt.generate_password_hash("pass2").decode("utf-8")

    conn = sqlite3.connect(db_path)
    conn.execute(
        'CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)'
    )
    conn.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        ("username1", hashed_pw1, "user1@example.com"),
    )
    conn.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        ("username2", hashed_pw2, "user2@example.com"),
    )
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def login(client, username, password):
    """Helper to login and return the access token."""
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    return response


class TestLogin:
    def test_valid_credentials(self, client):
        response = login(client, "username1", "pass1")
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data

    def test_wrong_password(self, client):
        response = login(client, "username1", "wrongpass")
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Invalid username or password"

    def test_nonexistent_username(self, client):
        response = login(client, "nouser", "pass1")
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Invalid username or password"


class TestGetUser:
    def test_existing_user(self, client):
        token = login(client, "username1", "pass1").get_json()["access_token"]
        response = client.get(
            "/api/user/username1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "username1"
        assert data["email"] == "user1@example.com"

    def test_existing_user2(self, client):
        token = login(client, "username2", "pass2").get_json()["access_token"]
        response = client.get(
            "/api/user/username2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "username2"
        assert data["email"] == "user2@example.com"

    def test_nonexistent_user(self, client):
        token = login(client, "username1", "pass1").get_json()["access_token"]
        response = client.get(
            "/api/user/unknown",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"] == "Forbidden"

    def test_forbidden_other_user(self, client):
        token = login(client, "username1", "pass1").get_json()["access_token"]
        response = client.get(
            "/api/user/username2",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["error"] == "Forbidden"

    def test_missing_token(self, client):
        response = client.get("/api/user/username1")
        assert response.status_code == 401
