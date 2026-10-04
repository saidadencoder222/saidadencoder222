"""
Builds tool_page.html: one shared interactive-tool page, personalized
per lead via a ?id=<channel_id> URL param read client-side. The lead's
real thumbnail loads client-side from YouTube's own CDN.
"""

import json

from personalize import get_palette_accent
from config import CONFIG
from storage import connect, leads_with_email

TEMPLATE_PATH = "proposal_template.html"
OUTPUT_PATH = "tool_page.html"


def build():
    with connect(CONFIG.db_path) as conn:
        leads = [dict(l) for l in leads_with_email(conn)]

    data = {}
    for lead in leads:
        data[lead["channel_id"]] = {
            "title": lead["title"],
            "thumbnailUrl": lead["thumbnail_url"],
            "niche": lead["niche"],
            "toolType": lead["tool_type"],
            "channelUrl": lead["channel_url"],
            "accent": get_palette_accent(lead["channel_id"]),
        }

    with open(TEMPLATE_PATH) as f:
        template = f.read()

    html = template.replace("__PROPOSAL_DATA__", json.dumps(data))

    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"Wrote {OUTPUT_PATH} with {len(data)} lead(s)")
    for cid in list(data.keys())[:3]:
        print(f"  ?id={cid}  ({data[cid]['toolType']})")


if __name__ == "__main__":
    build()
