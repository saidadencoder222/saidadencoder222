"""
Scans the inbox for opt-out requests (subject containing UNSUBSCRIBE, or
anything landed in Spam from an address we emailed) and records them so
the campaign never emails that address again.
"""

import re

from storage import add_unsubscribe, connect

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _sender_email(headers) -> str:
    from_header = next((h["value"] for h in headers if h["name"] == "From"), "")
    match = EMAIL_RE.search(from_header)
    return match.group(0) if match else None


def process_unsubscribe_requests(service, db_path: str) -> int:
    query = 'subject:UNSUBSCRIBE OR in:spam'
    resp = service.users().messages().list(userId="me", q=query, maxResults=100).execute()
    message_ids = [m["id"] for m in resp.get("messages", [])]

    count = 0
    with connect(db_path) as conn:
        for msg_id in message_ids:
            msg = service.users().messages().get(
                userId="me", id=msg_id, format="metadata",
                metadataHeaders=["From"],
            ).execute()
            email = _sender_email(msg.get("payload", {}).get("headers", []))
            if email:
                add_unsubscribe(conn, email)
                count += 1

    return count
