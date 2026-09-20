import base64
from email.message import EmailMessage


def send_email(service, *, to_addr: str, from_name: str, subject: str, body: str,
                reply_to: str = None) -> str:
    """Send one email via the Gmail API. Returns the Gmail message id."""
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = subject
    if from_name:
        msg["From"] = from_name
    if reply_to:
        msg["Reply-To"] = reply_to
        msg["List-Unsubscribe"] = f"<mailto:{reply_to}?subject=UNSUBSCRIBE>"
    msg.set_content(body)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent["id"]
