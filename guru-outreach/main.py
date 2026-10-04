import argparse

from config import CONFIG
from generate_audit import build_observations
from storage import connect, upsert_lead
from youtube_leads import find_gurus

# Mega-channels obviously don't need an unsolicited "growth audit" pitch,
# and channels under the floor usually aren't running a real business yet.
MIN_SUBS = 5000
MAX_SUBS = 300000


def cmd_find_leads(args):
    if not CONFIG.youtube_api_key:
        raise SystemExit("Set YOUTUBE_API_KEY in .env first.")

    candidates = find_gurus(
        CONFIG.youtube_api_key, args.query, max_results=args.max,
        min_subscribers=MIN_SUBS, max_subscribers=MAX_SUBS,
    )

    # Strategic targeting: only keep channels where the audit found a real,
    # computed gap - not everyone in the subscriber range. A channel with
    # consistent posting, a bio link, and healthy view ratios gets skipped
    # rather than sent a forced "looks solid" pitch.
    leads = [c for c in candidates if build_observations(c)]

    with connect(CONFIG.db_path) as conn:
        for lead in leads:
            upsert_lead(
                conn,
                channel_id=lead["channel_id"],
                title=lead["title"],
                email=lead["email"],
                niche=args.query,
                subscriber_count=lead["subscriber_count"],
                channel_url=lead["channel_url"],
                thumbnail_url=lead["thumbnail_url"],
                avg_recent_views=lead["avg_recent_views"],
                upload_gap_days_avg=lead["upload_gap_days_avg"],
                upload_gap_days_stdev=lead["upload_gap_days_stdev"],
                has_link_in_bio=int(lead["has_link_in_bio"]),
            )

    with_email = sum(1 for lead in leads if lead["email"])
    print(f"Found {len(candidates)} channel(s) in range, {len(leads)} with a real audit finding, "
          f"{with_email} of those with a public contact email.")


def cmd_send_campaign(args):
    from campaign import run_campaign_batch
    run_campaign_batch(sender_email=args.sender_email)


def cmd_send_one(args):
    from campaign import send_one_pending
    result = send_one_pending(sender_email=args.sender_email)
    if result is None:
        print("Nothing due to send.")


def cmd_send_tonight(args):
    import time
    from datetime import datetime, timezone
    from campaign import run_campaign_batch

    start = datetime.fromisoformat(args.start)
    end = datetime.fromisoformat(args.end)
    now = datetime.now(timezone.utc)
    if now < start:
        wait = (start - now).total_seconds()
        print(f"Waiting {wait/60:.1f} min until window start ({args.start})...")
        time.sleep(wait)

    run_campaign_batch(sender_email=args.sender_email, count=args.count, window_end=end)


def cmd_list_leads(args):
    with connect(CONFIG.db_path) as conn:
        rows = conn.execute(
            "SELECT title, email, subscriber_count, upload_gap_days_avg, has_link_in_bio, niche "
            "FROM leads ORDER BY found_at DESC"
        ).fetchall()
    for row in rows:
        email = row["email"] or "(no public email)"
        print(f"{row['title']:<35} {email:<35} subs={row['subscriber_count']} "
              f"gap_avg={row['upload_gap_days_avg']} bio_link={bool(row['has_link_in_bio'])}")
    print(f"\n{len(rows)} total lead(s).")


def cmd_unsubscribe(args):
    from storage import add_unsubscribe
    with connect(CONFIG.db_path) as conn:
        add_unsubscribe(conn, args.email)
    print(f"Marked {args.email} as unsubscribed.")


def build_parser():
    parser = argparse.ArgumentParser(description="Course-seller/finance-creator outreach tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_find = sub.add_parser("find-leads", help="Search for creators via the YouTube API")
    p_find.add_argument("--query", required=True)
    p_find.add_argument("--max", type=int, default=25)
    p_find.set_defaults(func=cmd_find_leads)

    p_list = sub.add_parser("list-leads", help="Show stored leads")
    p_list.set_defaults(func=cmd_list_leads)

    p_send = sub.add_parser("send-campaign", help="Send one batch of pitches/follow-ups")
    p_send.add_argument("--sender-email", required=True)
    p_send.set_defaults(func=cmd_send_campaign)

    p_one = sub.add_parser("send-one", help="Send exactly one due lead's email and exit")
    p_one.add_argument("--sender-email", required=True)
    p_one.set_defaults(func=cmd_send_one)

    p_tonight = sub.add_parser("send-tonight", help="One-off overnight batch with irregular pacing across a window")
    p_tonight.add_argument("--sender-email", required=True)
    p_tonight.add_argument("--count", type=int, required=True, help="Max number of sends this run")
    p_tonight.add_argument("--start", required=True, help="ISO UTC datetime to start at, e.g. 2026-09-21T19:00:00+00:00")
    p_tonight.add_argument("--end", required=True, help="ISO UTC datetime to finish by")
    p_tonight.set_defaults(func=cmd_send_tonight)

    p_unsub = sub.add_parser("unsubscribe", help="Manually mark an email as opted out")
    p_unsub.add_argument("--email", required=True)
    p_unsub.set_defaults(func=cmd_unsubscribe)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
