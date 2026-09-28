from contextlib import contextmanager
import sqlite3
from pathlib import Path

from .config import get_settings


def _db_path() -> str:
    url = get_settings().database_url

    if not url.startswith("sqlite:///"):
        raise ValueError(
            "This demo uses SQLite. "
            "Set DATABASE_URL=sqlite:///./pocketsmart.db"
        )

    return url.replace("sqlite:///", "", 1)


def init_db() -> None:
    path = Path(_db_path())

    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(_db_path())

    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    finally:
        conn.close()