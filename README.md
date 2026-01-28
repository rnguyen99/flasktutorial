# Flask Auth Tutorial

A Flask application with JWT authentication, split into two services:

- **Frontend** (`app.py`) -- Serves HTML pages on port 5002
- **API** (`api.py`) -- Handles authentication and user data on port 5001

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask flask-bcrypt flask-jwt-extended flask-cors
```

## Seed the Database

```bash
python seed_users.py
```

## Running

Open two terminals and run each service:

```bash
# Terminal 1 - API server
source .venv/bin/activate
python api.py
```

```bash
# Terminal 2 - Frontend server
source .venv/bin/activate
python app.py
```

Then open http://localhost:5002 in your browser.

## Configuration

The API URL can be configured via environment variable:

```bash
API_BASE_URL=https://api.mysite.com python app.py
```

By default it points to `http://localhost:5001`.
