'''
Flask application for tutorial purposes.
user service module. it has two endpoints:
- /user/<username> : GET method to fetch user details by username.
- /user/authenticate : POST method to authenticate user with username and password.
I have the user table store the user in the sqlite users.db 
database with fields: id, username, password, email.
'''
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

DATABASE = "users.db"

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"

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

def get_user_by_username(username):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

def get_user_by_id(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

# ---------------------
# Flask-Login user
# ---------------------
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = str(id)
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(user_id)
    if row:
        return User(row["id"], row["username"], row["email"])
    return None

# ---------------------
# Web pages
# ---------------------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        row = get_user_by_username(username)
        if row and bcrypt.check_password_hash(row["password"], password):
            user = User(row["id"], row["username"], row["email"])
            login_user(user)
            return redirect(url_for("dashboard"))
        error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user.username)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

# ---------------------
# API endpoints
# ---------------------
@app.route("/api/user/<username>")
@login_required
def get_user_api(username):
    if current_user.username != username:
        return jsonify({"error": "Forbidden"}), 403

    row = get_user_by_username(username)
    if not row:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": row["id"],
        "username": row["username"],
        "email": row["email"]
    })

if __name__ == "__main__":
    app.run(debug=True)
