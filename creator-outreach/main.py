import argparse

from config import CONFIG
from storage import connect, upsert_lead
from youtube_leads import find_creators


def cmd_find_leads(args):
    if not CONFIG.youtube_api_key:
        raise SystemExit("Set YOUTUBE_API_KEY in .env first.")

    leads = find_creators(
        CONFIG.youtube_api_key,
        args.query,
        max_results=args.max,
        min_subscribers=args.min_subs,
        max_subscribers=args.max_subs,
    )

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
            )

    with_email = sum(1 for lead in leads if lead["email"])
    print(f"Found {len(leads)} channel(s), {with_email} with a public contact email.")


def cmd_send_campaign(args):
    from campaign import run_campaign_batch
    run_campaign_batch(sender_email=args.sender_email)


def cmd_list_leads(args):
    with connect(CONFIG.db_path) as conn:
        rows = conn.execute(
            "SELECT title, email, subscriber_count, niche FROM leads ORDER BY found_at DESC"
        ).fetchall()
    for row in rows:
        email = row["email"] or "(no public email)"
        print(f"{row['title']:<40} {email:<35} subs={row['subscriber_count']} niche={row['niche']}")
    print(f"\n{len(rows)} total lead(s).")


def cmd_unsubscribe(args):
    from storage import add_unsubscribe
    with connect(CONFIG.db_path) as conn:
        add_unsubscribe(conn, args.email)
    print(f"Marked {args.email} as unsubscribed.")


def build_parser():
    parser = argparse.ArgumentParser(description="YouTube creator outreach tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_find = sub.add_parser("find-leads", help="Search for creators via the YouTube API")
    p_find.add_argument("--query", required=True, help="Niche/keywords to search, e.g. 'cooking channel'")
    p_find.add_argument("--max", type=int, default=50)
    p_find.add_argument("--min-subs", type=int, default=0)
    p_find.add_argument("--max-subs", type=int, default=None)
    p_find.set_defaults(func=cmd_find_leads)

    p_list = sub.add_parser("list-leads", help="Show stored leads")
    p_list.set_defaults(func=cmd_list_leads)

    p_send = sub.add_parser("send-campaign", help="Send one batch of pitches/follow-ups")
    p_send.add_argument("--sender-email", required=True, help="Your Gmail address (used for Reply-To/unsubscribe)")
    p_send.set_defaults(func=cmd_send_campaign)

    p_unsub = sub.add_parser("unsubscribe", help="Manually mark an email as opted out")
    p_unsub.add_argument("--email", required=True)
    p_unsub.set_defaults(func=cmd_unsubscribe)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
