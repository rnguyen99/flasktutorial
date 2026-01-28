'''
Flask application for tutorial purposes.
user service module. it has two endpoints:
- /user/<username> : GET method to fetch user details by username.
- /user/authenticate : POST method to authenticate user with username and password.
I have the user table store the user in the sqlite users.db 
database with fields: id, username, password, email.
'''

import sqlite3
from flask import Flask, request, jsonify, g, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

DATABASE = "users.db"

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "change-this-secret-in-prod"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ---------------------
# Database helpers
# ---------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_user_by_username(username: str):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

def get_user_by_id(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

# ---------------------
# Web pages
# ---------------------
@app.route("/")
def home():
    # JWT apps can't check auth here unless token is sent
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------------
# API endpoints
# ---------------------
@app.route("/api/auth/login", methods=["POST"])
def login_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    row = get_user_by_username(username)
    if not row or not bcrypt.check_password_hash(row["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=str(row["id"]))
    return jsonify(access_token=token), 200

@app.route("/api/user/<username>")
@jwt_required()
def get_user_api(username):
    user_id = get_jwt_identity()
    row = get_user_by_id(int(user_id))

    if not row:
        return jsonify({"error": "User not found"}), 404

    if row["username"] != username:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({
        "id": row["id"],
        "username": row["username"],
        "email": row["email"]
    })

if __name__ == "__main__":
    app.run(debug=True)
