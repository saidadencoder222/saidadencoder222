"""
Sends one batch/one email of the campaign. Each pitch links to a hosted,
personalized interactive tool (built by build_proposal_page.py) rather
than a generic pitch - the tool's actual quiz result is the proof of
value, not a promise of one.
"""

import hashlib
import random
import time
from datetime import datetime, timedelta, timezone

from config import CONFIG
from gmail_auth import get_gmail_service
from gmail_sender import send_email
from replies import process_unsubscribe_requests
from storage import (connect, is_unsubscribed, last_sent_at, leads_with_email,
                      record_send, touches_sent)

PROPOSAL_PAGE_URL = "https://saidadencoder222.github.io/saidadencoder222/toolkit-outreach/pages/tool.html"

PITCH_VARIANTS = [
    "templates/pitch_email_a.txt",
    "templates/pitch_email_b.txt",
    "templates/pitch_email_c.txt",
]


def _proposal_url(channel_id: str) -> str:
    return f"{PROPOSAL_PAGE_URL}?id={channel_id}"


def _pitch_template_for(channel_id: str) -> str:
    digest = hashlib.sha256(channel_id.encode()).hexdigest()
    return PITCH_VARIANTS[int(digest, 16) % len(PITCH_VARIANTS)]


def _load_template(touch_number: int, channel_id: str = None):
    if touch_number == 1:
        path = _pitch_template_for(channel_id)
    elif touch_number == 2:
        path = "templates/followup_email.txt"
    else:
        return None, None
    with open(path) as f:
        raw = f.read()
    subject_line, _, body = raw.partition("\n\n")
    subject = subject_line.removeprefix("SUBJECT:").strip()
    return subject, body


def _render(text: str, lead, sender_email: str) -> str:
    hook = lead["hook"] if "hook" in lead.keys() else None
    hook_line = f"One thing I noticed on your site: {hook}. " if hook else ""
    return text.format(
        channel_title=lead["title"],
        niche=lead["niche"] or "your niche",
        sender_name=CONFIG.sender_name,
        proposal_url=_proposal_url(lead["channel_id"]),
        hook_line=hook_line,
    )


def _due_for_next_touch(conn, lead) -> int:
    sent = touches_sent(conn, lead["channel_id"])
    if sent >= CONFIG.max_touches:
        return None
    if sent == 0:
        return 1
    last = last_sent_at(conn, lead["channel_id"])
    last_dt = datetime.fromisoformat(last)
    if datetime.now(timezone.utc) - last_dt < timedelta(days=CONFIG.followup_after_days):
        return None
    return sent + 1


def send_one_pending(sender_email: str):
    """Sends exactly one due lead's email and returns info, or None if
    nothing is currently due. Driven by a scheduled wake-up per send
    rather than an in-process sleep loop."""
    service = get_gmail_service()

    unsub_count = process_unsubscribe_requests(service, CONFIG.db_path)
    if unsub_count:
        print(f"Recorded {unsub_count} unsubscribe(s).")

    with connect(CONFIG.db_path) as conn:
        for lead in leads_with_email(conn):
            if is_unsubscribed(conn, lead["email"]):
                continue
            touch = _due_for_next_touch(conn, lead)
            if touch is None:
                continue

            subject_tpl, body_tpl = _load_template(touch, lead["channel_id"])
            if subject_tpl is None:
                continue

            subject = _render(subject_tpl, lead, sender_email)
            body = _render(body_tpl, lead, sender_email)

            message_id = send_email(
                service,
                to_addr=lead["email"],
                from_name=f"{CONFIG.sender_name} <{sender_email}>",
                subject=subject,
                body=body,
                reply_to=sender_email,
            )
            record_send(
                conn,
                channel_id=lead["channel_id"],
                touch_number=touch,
                subject=subject,
                gmail_message_id=message_id,
            )
            print(f"[{datetime.now(timezone.utc).isoformat()}] Sent touch {touch} to {lead['title']} <{lead['email']}>")
            return {"title": lead["title"], "email": lead["email"], "touch": touch}

    return None


def run_campaign_batch(sender_email: str, count: int = None, window_end: datetime = None):
    service = get_gmail_service()

    unsub_count = process_unsubscribe_requests(service, CONFIG.db_path)
    if unsub_count:
        print(f"Recorded {unsub_count} unsubscribe(s).")

    limit = count if count is not None else CONFIG.daily_send_limit

    sent_this_run = 0
    with connect(CONFIG.db_path) as conn:
        pending = [
            lead for lead in leads_with_email(conn)
            if not is_unsubscribed(conn, lead["email"]) and _due_for_next_touch(conn, lead) is not None
        ][:limit]

        for i, lead in enumerate(pending):
            touch = _due_for_next_touch(conn, lead)
            if touch is None:
                continue
            subject_tpl, body_tpl = _load_template(touch, lead["channel_id"])
            if subject_tpl is None:
                continue
            subject = _render(subject_tpl, lead, sender_email)
            body = _render(body_tpl, lead, sender_email)
            message_id = send_email(
                service, to_addr=lead["email"],
                from_name=f"{CONFIG.sender_name} <{sender_email}>",
                subject=subject, body=body, reply_to=sender_email,
            )
            record_send(conn, channel_id=lead["channel_id"], touch_number=touch,
                        subject=subject, gmail_message_id=message_id)
            sent_this_run += 1
            print(f"Sent touch {touch} to {lead['title']} <{lead['email']}>")
            remaining = len(pending) - (i + 1)
            if remaining > 0:
                time.sleep(random.uniform(300, 600))

    print(f"Done. Sent {sent_this_run} email(s) this run.")
