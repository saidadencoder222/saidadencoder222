"""
Builds proposal_page.html: one shared page, personalized per creator via
a ?id=<channel_id> URL param read client-side. Same pattern as
guru-outreach/build_proposal_page.py - the creator's real thumbnail loads
client-side from YouTube's own CDN (the visitor's browser fetches it, not
this sandbox), so the network block here doesn't apply.
"""

import json

from config import CONFIG
from personalize import get_palette_accent
from storage import connect, leads_with_email

TEMPLATE_PATH = "proposal_template.html"
OUTPUT_PATH = "proposal_page.html"


def build():
    with connect(CONFIG.db_path) as conn:
        leads = [dict(l) for l in leads_with_email(conn)]

    data = {}
    for lead in leads:
        data[lead["channel_id"]] = {
            "title": lead["title"],
            "thumbnailUrl": lead["thumbnail_url"],
            "niche": lead["niche"],
            "accent": get_palette_accent(lead["channel_id"]),
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
