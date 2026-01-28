import os
import sqlite3
import tempfile
import pytest
import app as app_module
from app import app


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app_module.DATABASE = db_path
    app.config["TESTING"] = True

    conn = sqlite3.connect(db_path)
    conn.execute(
        'CREATE TABLE user (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)'
    )
    conn.execute(
        "INSERT INTO user (username, password, email) VALUES ('username1', 'pass1', 'user1@example.com')"
    )
    conn.execute(
        "INSERT INTO user (username, password, email) VALUES ('username2', 'pass2', 'user2@example.com')"
    )
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


class TestGetUser:
    def test_existing_user(self, client):
        response = client.get("/user/username1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "username1"
        assert data["email"] == "user1@example.com"

    def test_existing_user2(self, client):
        response = client.get("/user/username2")
        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "username2"
        assert data["email"] == "user2@example.com"

    def test_nonexistent_user(self, client):
        response = client.get("/user/unknown")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "User not found"


class TestAuthenticateUser:
    def test_valid_credentials(self, client):
        response = client.post("/user/authenticate", json={
            "username": "username1",
            "password": "pass1",
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Authentication successful"

    def test_wrong_password(self, client):
        response = client.post("/user/authenticate", json={
            "username": "username1",
            "password": "wrongpass",
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Invalid username or password"

    def test_nonexistent_username(self, client):
        response = client.post("/user/authenticate", json={
            "username": "nouser",
            "password": "pass1",
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Invalid username or password"
