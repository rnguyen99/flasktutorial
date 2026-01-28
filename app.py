'''
Frontend server for the Flask tutorial app.
Serves HTML pages on port 5000.
API endpoints are in api.py (port 5001).
'''

import os
from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)
app.config["API_BASE_URL"] = os.environ.get("API_BASE_URL", "http://localhost:5001")

@app.context_processor
def inject_config():
    return {"api_base_url": app.config["API_BASE_URL"]}

# ---------------------
# Web pages
# ---------------------
@app.route("/")
def home():
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, port=5002)
