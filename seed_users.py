import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT NOT NULL
)
""")

users = [
    ("username1", "pass1", "user1@example.com"),
    ("username2", "pass2", "user2@example.com")
]

for u, p, e in users:
    hashed = bcrypt.generate_password_hash(p).decode()
    cur.execute("INSERT OR IGNORE INTO users (username, password, email) VALUES (?, ?, ?)",
                (u, hashed, e))

conn.commit()
conn.close()
print("Users seeded.")
