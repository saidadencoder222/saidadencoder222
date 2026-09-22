import base64
import mimetypes
import os
from email.message import EmailMessage


def send_email(service, *, to_addr: str, from_name: str, subject: str, body: str,
                reply_to: str = None, attachments: list = None) -> str:
    """Send one email via the Gmail API. Returns the Gmail message id."""
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = subject
    if from_name:
        msg["From"] = from_name
    if reply_to:
        msg["Reply-To"] = reply_to
    # Lets mail clients render a one-click unsubscribe affordance in
    # addition to the reply-based opt-out described in the email body.
    if reply_to:
        msg["List-Unsubscribe"] = f"<mailto:{reply_to}?subject=UNSUBSCRIBE>"
    msg.set_content(body)

    for path in attachments or []:
        ctype, _ = mimetypes.guess_type(path)
        maintype, subtype = (ctype.split("/", 1) if ctype else ("application", "octet-stream"))
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype,
                filename=os.path.basename(path),
            )

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent["id"]
