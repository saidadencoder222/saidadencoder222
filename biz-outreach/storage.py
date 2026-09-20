import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    place_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    email_source TEXT,
    demo_url TEXT,
    found_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id TEXT NOT NULL REFERENCES leads(place_id),
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


def upsert_lead(conn, *, place_id, name, category, address, phone, email,
                 email_source, demo_url):
    conn.execute(
        """
        INSERT INTO leads (place_id, name, category, address, phone, email, email_source, demo_url, found_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(place_id) DO UPDATE SET
            email=COALESCE(excluded.email, leads.email),
            email_source=COALESCE(excluded.email_source, leads.email_source),
            demo_url=excluded.demo_url
        """,
        (place_id, name, category, address, phone, email, email_source, demo_url, now()),
    )
    conn.commit()


def is_unsubscribed(conn, email: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM unsubscribes WHERE email = ?", (email,)
    ).fetchone()
    return row is not None


def add_unsubscribe(conn, email: str):
    conn.execute(
        "INSERT OR IGNORE INTO unsubscribes (email, unsubscribed_at) VALUES (?, ?)",
        (email, now()),
    )
    conn.commit()


def touches_sent(conn, place_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM sends WHERE place_id = ?", (place_id,)
    ).fetchone()
    return row["c"]


def last_sent_at(conn, place_id: str):
    row = conn.execute(
        "SELECT sent_at FROM sends WHERE place_id = ? ORDER BY sent_at DESC LIMIT 1",
        (place_id,),
    ).fetchone()
    return row["sent_at"] if row else None


def record_send(conn, *, place_id, touch_number, subject, gmail_message_id):
    conn.execute(
        """
        INSERT INTO sends (place_id, touch_number, subject, gmail_message_id, sent_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (place_id, touch_number, subject, gmail_message_id, now()),
    )
    # Committed immediately, not just at the end of the batch's `with connect()`
    # block - a kill/crash mid-batch must never lose the record of a send that
    # actually went out (an email can't be un-sent, so this must survive).
    conn.commit()


def leads_with_email(conn):
    return conn.execute(
        "SELECT * FROM leads WHERE email IS NOT NULL AND email != '' ORDER BY found_at"
    ).fetchall()
