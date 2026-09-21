"""Orchestrates: prospects.csv -> YouTube audit -> proposal page -> email.

Usage:
    python src/main.py data/prospects.csv --send   # actually sends emails
    python src/main.py data/prospects.csv          # dry-run, prints emails
"""
import argparse
import csv
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_client import get_client, resolve_channel_id, get_channel_data  # noqa: E402
from audit import run_audit  # noqa: E402
from proposal import render_proposal, slugify  # noqa: E402
from emailer import send_email  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load_social_proof() -> list[dict]:
    path = ROOT / "data" / "social_proof.yaml"
    if not path.exists():
        path = ROOT / "data" / "social_proof.example.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prospects_csv")
    parser.add_argument("--send", action="store_true", help="actually send emails instead of dry-run")
    parser.add_argument("--sender-name", default=os.environ.get("SENDER_NAME", "Your Name"))
    parser.add_argument("--booking-link", default=os.environ.get("BOOKING_LINK", "https://example.com/book"))
    parser.add_argument("--cta-text", default="Book a 15-min call")
    args = parser.parse_args()

    load_dotenv()
    pages_base_url = os.environ.get("PAGES_BASE_URL", "").rstrip("/")
    if not pages_base_url:
        print("Warning: PAGES_BASE_URL is not set in .env — proposal links will be placeholders until you push to GitHub Pages.")

    youtube = get_client()
    social_proof = load_social_proof()

    with open(args.prospects_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            channel_handle = row["channel"].strip()
            email = row["email"].strip()
            greeting_name = row.get("greeting_name", "").strip()

            print(f"\n=== Processing {channel_handle} ===")
            channel_id = resolve_channel_id(youtube, channel_handle)
            channel = get_channel_data(youtube, channel_id)
            findings = run_audit(channel)
            print(f"Found {len(findings)} weak points for {channel['title']}")

            out_path = render_proposal(
                channel=channel,
                findings=findings,
                social_proof=social_proof,
                sender_name=args.sender_name,
                booking_link=args.booking_link,
                cta_text=args.cta_text,
            )
            slug = slugify(channel["title"])
            proposal_url = f"{pages_base_url}/proposals/{slug}/" if pages_base_url else f"file://{out_path}"
            print(f"Rendered: {out_path}")
            print(f"Proposal URL: {proposal_url}")

            send_email(
                to_email=email,
                channel_title=channel["title"],
                proposal_url=proposal_url,
                sender_name=args.sender_name,
                greeting_name=greeting_name,
                dry_run=not args.send,
            )


if __name__ == "__main__":
    main()
