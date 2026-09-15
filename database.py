"""
Очень простое хранилище на SQLite (один файл bot.db).
Этого достаточно для старта — не нужно поднимать отдельную базу данных.

Важно: на Railway файловая система по умолчанию не сохраняется между
деплоями (redeploy). Для старта это нормально, но если база вырастет —
подключите Railway Volume (Settings -> Volumes) и укажите путь к bot.db
внутри него. Подробнее в README.md.
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "bot.db"


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                age TEXT,
                experience TEXT,
                goal TEXT,
                bought_guide INTEGER DEFAULT 0,
                subscribed_channel INTEGER DEFAULT 0,
                subscription_until TEXT
            )
        """)
        conn.commit()


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def upsert_user(user_id: int, username: str | None) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username or ""),
        )
        conn.execute(
            "UPDATE users SET username = ? WHERE user_id = ?",
            (username or "", user_id),
        )
        conn.commit()


def save_survey(user_id: int, name: str, age: str, experience: str, goal: str) -> None:
    with _connect() as conn:
        conn.execute(
            """UPDATE users
               SET name = ?, age = ?, experience = ?, goal = ?
               WHERE user_id = ?""",
            (name, age, experience, goal, user_id),
        )
        conn.commit()


def mark_guide_bought(user_id: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE users SET bought_guide = 1 WHERE user_id = ?", (user_id,)
        )
        conn.commit()


def mark_subscribed(user_id: int, until_date: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE users SET subscribed_channel = 1, subscription_until = ? WHERE user_id = ?",
            (until_date, user_id),
        )
        conn.commit()


def get_user(user_id: int) -> sqlite3.Row | None:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()
