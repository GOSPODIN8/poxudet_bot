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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_date TEXT,
                topic TEXT,
                text TEXT,
                image_path TEXT,
                status TEXT DEFAULT 'pending',
                kind TEXT DEFAULT 'daily',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # На случай, если таблица уже существовала до добавления этой колонки
        cols = [row[1] for row in conn.execute("PRAGMA table_info(drafts)")]
        if "kind" not in cols:
            conn.execute("ALTER TABLE drafts ADD COLUMN kind TEXT DEFAULT 'daily'")
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


# ---------- Драфты постов (ежедневных и еженедельной программы) ----------

def create_draft(post_date: str, topic: str, text: str, image_path: str | None,
                  kind: str = "daily") -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO drafts (post_date, topic, text, image_path, status, kind) "
            "VALUES (?, ?, ?, ?, 'pending', ?)",
            (post_date, topic, text, image_path, kind),
        )
        conn.commit()
        return cur.lastrowid


def update_draft(draft_id: int, text: str, image_path: str | None) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE drafts SET text = ?, image_path = ? WHERE id = ?",
            (text, image_path, draft_id),
        )
        conn.commit()


def set_draft_status(draft_id: int, status: str) -> None:
    with _connect() as conn:
        conn.execute("UPDATE drafts SET status = ? WHERE id = ?", (status, draft_id))
        conn.commit()


def get_draft(draft_id: int) -> sqlite3.Row | None:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        return cur.fetchone()


def get_approved_draft_for_date(post_date: str, kind: str = "daily") -> sqlite3.Row | None:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM drafts WHERE post_date = ? AND kind = ? AND status = 'approved' "
            "ORDER BY id DESC LIMIT 1",
            (post_date, kind),
        )
        return cur.fetchone()
