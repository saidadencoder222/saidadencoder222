"""
Builds proposal_page.html: one shared page, personalized per creator via
a ?id=<channel_id> URL param read client-side. Each creator's real
audit findings, stats, and thumbnail URL are precomputed here in Python
(single source of truth - the same build_observations() logic used for
the PDF/email) and embedded as a JSON blob. The creator's actual avatar
loads client-side from YouTube's own CDN - the visitor's browser fetches
it directly, not this sandbox, so the network block doesn't apply.
"""

import json

from config import CONFIG
from generate_audit import build_observations
from personalize import get_palette_accent
from storage import connect, leads_with_email

TEMPLATE_PATH = "proposal_template.html"
OUTPUT_PATH = "proposal_page.html"


def build():
    with connect(CONFIG.db_path) as conn:
        leads = [dict(l) for l in leads_with_email(conn)]

    data = {}
    for lead in leads:
        observations = build_observations(lead)
        data[lead["channel_id"]] = {
            "title": lead["title"],
            "thumbnailUrl": lead["thumbnail_url"],
            "subscriberCount": lead["subscriber_count"],
            "avgRecentViews": lead["avg_recent_views"],
            "uploadGapDaysAvg": lead["upload_gap_days_avg"],
            "hasLinkInBio": bool(lead["has_link_in_bio"]),
            "accent": get_palette_accent(lead["channel_id"]),
            "findings": [{"heading": h, "text": t} for h, t in observations],
        }

    with open(TEMPLATE_PATH) as f:
        template = f.read()

    html = template.replace("__PROPOSAL_DATA__", json.dumps(data))

    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"Wrote {OUTPUT_PATH} with {len(data)} creator(s)")
    print("Sample URL param values:")
    for cid in list(data.keys())[:3]:
        print(f"  ?id={cid}")


if __name__ == "__main__":
    build()
