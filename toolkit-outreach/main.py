import argparse

from config import CONFIG
from storage import connect, upsert_lead
from youtube_leads import find_gurus

MIN_SUBS = 3000
MAX_SUBS = 400000

# Maps a niche/search query to which interactive tool variant fits its
# audience best. Checked in order - first keyword match wins.
TOOL_TYPE_RULES = [
    (("fitness", "weight loss", "nutrition", "meal prep", "personal trainer",
      "bodybuilding", "diet coach", "macro"), "meal_plan"),
    (("trading", "day trading", "forex", "options trading", "crypto",
      "stock market", "swing trading", "investing"), "risk_profile"),
    (("dropshipping", "amazon fba", "ecommerce", "e-commerce", "print on demand",
      "shopify", "product research"), "product_finder"),
    (("social media marketing", "content creation", "copywriting",
      "email marketing", "digital marketing", "youtube automation",
      "content strategy", "personal branding"), "content_plan"),
    (("real estate",), "deal_analyzer"),
    (("massage", "spa", "med spa", "medspa", "chiropractor", "chiropractic",
      "aesthetics", "aesthetic clinic", "wellness studio", "salon", "esthetician",
      "physical therapy", "physiotherapy"), "service_match"),
]
DEFAULT_TOOL_TYPE = "offer_clarity"


def _tool_type_for(query: str) -> str:
    q = query.lower()
    for keywords, tool_type in TOOL_TYPE_RULES:
        if any(k in q for k in keywords):
            return tool_type
    return DEFAULT_TOOL_TYPE


def cmd_find_leads(args):
    if not CONFIG.youtube_api_key:
        raise SystemExit("Set YOUTUBE_API_KEY in .env first.")

    candidates = find_gurus(
        CONFIG.youtube_api_key, args.query, max_results=args.max,
        min_subscribers=args.min_subs, max_subscribers=args.max_subs,
    )
    tool_type = args.tool_type or _tool_type_for(args.query)

    with connect(CONFIG.db_path) as conn:
        for lead in candidates:
            upsert_lead(
                conn,
                channel_id=lead["channel_id"],
                title=lead["title"],
                email=lead["email"],
                niche=args.query,
                tool_type=tool_type,
                subscriber_count=lead["subscriber_count"],
                channel_url=lead["channel_url"],
                thumbnail_url=lead["thumbnail_url"],
            )

    with_email = sum(1 for lead in candidates if lead["email"])
    print(f"Found {len(candidates)} channel(s) [{tool_type}], {with_email} with a public contact email.")


def cmd_send_campaign(args):
    from campaign import run_campaign_batch
    run_campaign_batch(sender_email=args.sender_email)


def cmd_send_one(args):
    from campaign import send_one_pending
    result = send_one_pending(sender_email=args.sender_email)
    if result is None:
        print("Nothing due to send.")


def cmd_list_leads(args):
    with connect(CONFIG.db_path) as conn:
        rows = conn.execute(
            "SELECT title, email, tool_type, subscriber_count, niche FROM leads ORDER BY found_at DESC"
        ).fetchall()
    for row in rows:
        email = row["email"] or "(no public email)"
        print(f"{row['title']:<35} {email:<32} tool={row['tool_type']:<14} subs={row['subscriber_count']} niche={row['niche']}")
    print(f"\n{len(rows)} total lead(s).")


def cmd_unsubscribe(args):
    from storage import add_unsubscribe
    with connect(CONFIG.db_path) as conn:
        add_unsubscribe(conn, args.email)
    print(f"Marked {args.email} as unsubscribed.")


def build_parser():
    parser = argparse.ArgumentParser(description="Interactive conversion-tool outreach")
    sub = parser.add_subparsers(dest="command", required=True)

    p_find = sub.add_parser("find-leads")
    p_find.add_argument("--query", required=True)
    p_find.add_argument("--max", type=int, default=25)
    p_find.add_argument("--min-subs", type=int, default=MIN_SUBS)
    p_find.add_argument("--max-subs", type=int, default=MAX_SUBS)
    p_find.add_argument("--tool-type", default=None, help="Override auto-detected tool type")
    p_find.set_defaults(func=cmd_find_leads)

    p_list = sub.add_parser("list-leads")
    p_list.set_defaults(func=cmd_list_leads)

    p_send = sub.add_parser("send-campaign")
    p_send.add_argument("--sender-email", required=True)
    p_send.set_defaults(func=cmd_send_campaign)

    p_one = sub.add_parser("send-one")
    p_one.add_argument("--sender-email", required=True)
    p_one.set_defaults(func=cmd_send_one)

    p_unsub = sub.add_parser("unsubscribe")
    p_unsub.add_argument("--email", required=True)
    p_unsub.set_defaults(func=cmd_unsubscribe)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
