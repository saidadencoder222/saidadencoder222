"""
Sends one batch of the campaign: new leads get the initial pitch, leads
past `followup_after_days` with no reply get a single follow-up, capped at
`max_touches` total per lead. Meant to be invoked periodically (e.g. once
a day via cron/systemd timer) rather than looped in-process, so a crash
never means duplicate sends.
"""

from datetime import datetime, timedelta, timezone

from config import CONFIG
from gmail_auth import get_gmail_service
from gmail_sender import send_email
from replies import process_unsubscribe_requests
from storage import (connect, is_unsubscribed, last_sent_at, leads_with_email,
                      record_send, touches_sent)

TEMPLATES = {
    1: "templates/pitch_email.txt",
    2: "templates/followup_email.txt",
}


def _load_template(touch_number: int):
    path = TEMPLATES.get(touch_number)
    if path is None:
        return None, None
    with open(path) as f:
        raw = f.read()
    subject_line, _, body = raw.partition("\n\n")
    subject = subject_line.removeprefix("SUBJECT:").strip()
    return subject, body


def _render(text: str, lead, sender_email: str) -> str:
    return text.format(
        channel_title=lead["title"],
        niche=lead["niche"] or "your niche",
        product_name=CONFIG.product_name,
        product_link=CONFIG.product_link,
        sender_name=CONFIG.sender_name,
    )


def _due_for_next_touch(conn, lead) -> int:
    """Return the touch number to send next, or None if not due yet."""
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

            subject_tpl, body_tpl = _load_template(touch)
            if subject_tpl is None:
                continue

            subject = _render(subject_tpl, lead, sender_email)
            body = _render(body_tpl, lead, sender_email)

            message_id = send_email(
                service,
                to_addr=lead["email"],
                from_name=CONFIG.sender_name,
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
            sent_this_run += 1
            print(f"Sent touch {touch} to {lead['title']} <{lead['email']}>")

    print(f"Done. Sent {sent_this_run} email(s) this run.")
