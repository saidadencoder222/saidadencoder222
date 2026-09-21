"""Sends the outreach email pointing at the hosted proposal page.

Defaults to dry-run: prints the message instead of sending, so nothing goes
out until GMAIL_ADDRESS / GMAIL_APP_PASSWORD are set AND dry_run=False is
passed explicitly.
"""
import os
import smtplib
from email.mime.text import MIMEText

SUBJECT_TEMPLATE = "A few growth gaps I found on {channel_title}"

BODY_TEMPLATE = """Hi{greeting_name},

I went through {channel_title}'s content and put together a short teardown
of a few things that are likely capping revenue right now, plus what I'd
fix first.

It's here: {proposal_url}

No pitch in this email — just have a look and see if it's useful.

{sender_name}
"""


def build_message(to_email: str, channel_title: str, proposal_url: str,
                   sender_name: str, sender_email: str, greeting_name: str = "") -> MIMEText:
    body = BODY_TEMPLATE.format(
        greeting_name=f" {greeting_name}" if greeting_name else "",
        channel_title=channel_title,
        proposal_url=proposal_url,
        sender_name=sender_name,
    )
    msg = MIMEText(body)
    msg["Subject"] = SUBJECT_TEMPLATE.format(channel_title=channel_title)
    msg["From"] = sender_email
    msg["To"] = to_email
    return msg


def send_email(to_email: str, channel_title: str, proposal_url: str,
                sender_name: str, greeting_name: str = "", dry_run: bool = True) -> None:
    gmail_address = os.environ.get("GMAIL_ADDRESS", "")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    msg = build_message(to_email, channel_title, proposal_url, sender_name,
                         gmail_address or "you@example.com", greeting_name)

    if dry_run or not gmail_address or not gmail_app_password:
        print("--- DRY RUN (no email sent) ---")
        print(msg.as_string())
        print("--------------------------------")
        return

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_email], msg.as_string())
    print(f"Sent to {to_email}")
