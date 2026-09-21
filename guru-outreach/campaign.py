"""
Sends one batch: new leads get the initial audit pitch, leads past
`followup_after_days` with no reply get a single follow-up, capped at
`max_touches` total per lead. Safe to kill/resume - every send commits
immediately (see storage.py), never just at the end of a batch.
"""

import hashlib
import os
import random
import time
from datetime import datetime, timedelta, timezone

import generate_audit
from config import CONFIG
from gmail_auth import get_gmail_service
from gmail_sender import send_email
from personalize import get_palette_accent
from replies import process_unsubscribe_requests
from storage import (connect, is_unsubscribed, last_sent_at, leads_with_email,
                      record_send, touches_sent)

GENERATED_DIR = os.path.join("assets", "generated")

PITCH_VARIANTS = [
    "templates/pitch_email_a.txt",
    "templates/pitch_email_b.txt",
    "templates/pitch_email_c.txt",
]


def _personalized_pdf_path(lead) -> str:
    os.makedirs(GENERATED_DIR, exist_ok=True)
    path = os.path.join(GENERATED_DIR, f"{lead['channel_id']}.pdf")
    if not os.path.exists(path):
        accent = get_palette_accent(lead["channel_id"])
        generate_audit.build(path, lead=lead, accent_color=accent)
    return path


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
    return text.format(
        channel_title=lead["title"],
        sender_name=CONFIG.sender_name,
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


def run_campaign_batch(sender_email: str):
    service = get_gmail_service()

    unsub_count = process_unsubscribe_requests(service, CONFIG.db_path)
    if unsub_count:
        print(f"Recorded {unsub_count} unsubscribe(s).")

    sent_this_run = 0
    with connect(CONFIG.db_path) as conn:
        for lead in leads_with_email(conn):
            if sent_this_run >= CONFIG.daily_send_limit:
                break
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
                attachments=[_personalized_pdf_path(lead)],
            )
            record_send(
                conn,
                channel_id=lead["channel_id"],
                touch_number=touch,
                subject=subject,
                gmail_message_id=message_id,
            )
            sent_this_run += 1
            print(f"Sent touch {touch} to {lead['title']} <{lead['email']}>")

            if sent_this_run < CONFIG.daily_send_limit:
                time.sleep(random.uniform(600, 1200))  # 10-20 min apart, ~10 over a few hours

    print(f"Done. Sent {sent_this_run} email(s) this run.")
