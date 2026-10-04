import argparse

from config import CONFIG
from demo_site import generate_demo
from places_leads import find_businesses_without_website
from storage import connect, upsert_lead

DEMO_TEMPLATE_PATH = "templates/demo_template.html"


def cmd_find_leads(args):
    if not CONFIG.places_api_key:
        raise SystemExit("Set GOOGLE_PLACES_API_KEY in .env first.")

    leads = find_businesses_without_website(
        CONFIG.places_api_key, args.query, max_results=args.max,
    )

    with connect(CONFIG.db_path) as conn:
        for lead in leads:
            slug, demo_url = generate_demo(
                lead,
                template_path=DEMO_TEMPLATE_PATH,
                output_dir=CONFIG.demo_output_dir,
                base_url=CONFIG.demo_base_url,
            )
            upsert_lead(
                conn,
                place_id=lead["place_id"],
                name=lead["name"],
                category=lead["category"],
                address=lead["address"],
                phone=lead["phone"],
                email=lead["email"],
                email_source=lead["email_source"],
                demo_url=demo_url,
            )

    with_email = sum(1 for lead in leads if lead["email"])
    print(f"Found {len(leads)} business(es) with no website, {with_email} with a public contact email.")
    print(f"Demo pages written under {CONFIG.demo_output_dir}/ - host that folder (e.g. GitHub Pages) "
          f"at the base URL configured in DEMO_BASE_URL before sending.")


def cmd_send_campaign(args):
    from campaign import run_campaign_batch
    run_campaign_batch(sender_email=args.sender_email)


def cmd_list_leads(args):
    with connect(CONFIG.db_path) as conn:
        rows = conn.execute(
            "SELECT name, email, phone, category, demo_url FROM leads ORDER BY found_at DESC"
        ).fetchall()
    for row in rows:
        email = row["email"] or "(no public email - manual/phone follow-up)"
        print(f"{row['name']:<35} {email:<35} phone={row['phone']} demo={row['demo_url']}")
    print(f"\n{len(rows)} total lead(s).")


def cmd_unsubscribe(args):
    from storage import add_unsubscribe
    with connect(CONFIG.db_path) as conn:
        add_unsubscribe(conn, args.email)
    print(f"Marked {args.email} as unsubscribed.")


def build_parser():
    parser = argparse.ArgumentParser(description="No-website business outreach tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_find = sub.add_parser("find-leads", help="Search for businesses with no website via Places API")
    p_find.add_argument("--query", required=True, help="e.g. 'plumbers in Austin, TX'")
    p_find.add_argument("--max", type=int, default=40)
    p_find.set_defaults(func=cmd_find_leads)

    p_list = sub.add_parser("list-leads", help="Show stored leads")
    p_list.set_defaults(func=cmd_list_leads)

    p_send = sub.add_parser("send-campaign", help="Send one batch of pitches/follow-ups")
    p_send.add_argument("--sender-email", required=True)
    p_send.set_defaults(func=cmd_send_campaign)

    p_unsub = sub.add_parser("unsubscribe", help="Manually mark an email as opted out")
    p_unsub.add_argument("--email", required=True)
    p_unsub.set_defaults(func=cmd_unsubscribe)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
