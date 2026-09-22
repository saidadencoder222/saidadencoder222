import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    channel_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    email TEXT,
    niche TEXT,
    tool_type TEXT,
    subscriber_count INTEGER,
    channel_url TEXT,
    thumbnail_url TEXT,
    found_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT NOT NULL REFERENCES leads(channel_id),
    touch_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    gmail_message_id TEXT,
    sent_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unsubscribes (
    email TEXT PRIMARY KEY,
    unsubscribed_at TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_lead(conn, *, channel_id, title, email, niche, tool_type, subscriber_count,
                 channel_url, thumbnail_url=None):
    conn.execute(
        """
        INSERT INTO leads (channel_id, title, email, niche, tool_type, subscriber_count,
                            channel_url, thumbnail_url, found_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id) DO UPDATE SET
            email=COALESCE(excluded.email, leads.email),
            subscriber_count=excluded.subscriber_count,
            thumbnail_url=COALESCE(excluded.thumbnail_url, leads.thumbnail_url)
        """,
        (channel_id, title, email, niche, tool_type, subscriber_count, channel_url,
         thumbnail_url, now()),
    )
    conn.commit()


def is_unsubscribed(conn, email: str) -> bool:
    row = conn.execute("SELECT 1 FROM unsubscribes WHERE email = ?", (email,)).fetchone()
    return row is not None


def add_unsubscribe(conn, email: str):
    conn.execute(
        "INSERT OR IGNORE INTO unsubscribes (email, unsubscribed_at) VALUES (?, ?)",
        (email, now()),
    )
    conn.commit()


def touches_sent(conn, channel_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM sends WHERE channel_id = ?", (channel_id,)
    ).fetchone()
    return row["c"]


def last_sent_at(conn, channel_id: str):
    row = conn.execute(
        "SELECT sent_at FROM sends WHERE channel_id = ? ORDER BY sent_at DESC LIMIT 1",
        (channel_id,),
    ).fetchone()
    return row["sent_at"] if row else None


def record_send(conn, *, channel_id, touch_number, subject, gmail_message_id):
    conn.execute(
        """
        INSERT INTO sends (channel_id, touch_number, subject, gmail_message_id, sent_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (channel_id, touch_number, subject, gmail_message_id, now()),
    )
    conn.commit()


def leads_with_email(conn):
    return conn.execute(
        "SELECT * FROM leads WHERE email IS NOT NULL AND email != '' ORDER BY found_at"
    ).fetchall()
