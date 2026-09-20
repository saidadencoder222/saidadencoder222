"""
Finds candidate creators via the YouTube Data API and pulls a contact email
*only* when the creator has put one directly in their public channel
description (the common "Business inquiries: ..." line). This deliberately
does not scrape the "About" page's gated email-reveal button - that's kept
behind a login/captcha specifically so it can't be harvested, and doing so
would be outside what the API's data is meant to be used for.

If a channel doesn't list an email in its description, we still record it
as a lead (useful for manual follow-up, e.g. a contact form) but leave the
email field empty so it's never emailed automatically.
"""

import re
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Description text on a lot of channels is a boilerplate footer, not a
# contact line. Skip obvious false positives like "noreply@youtube.com".
IGNORED_DOMAINS = {"youtube.com", "google.com"}


def _extract_email(description: str):
    for match in EMAIL_RE.findall(description or ""):
        domain = match.split("@")[-1].lower()
        if domain not in IGNORED_DOMAINS:
            return match
    return None


def find_creators(api_key: str, query: str, *, max_results: int = 50,
                   min_subscribers: int = 0, max_subscribers: int = None):
    """Search channels matching `query`, yield dicts with lead info.

    Only uses public search.list / channels.list endpoints - no scraping.
    """
    youtube = build("youtube", "v3", developerKey=api_key)

    channel_ids = []
    page_token = None
    while len(channel_ids) < max_results:
        resp = youtube.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=min(50, max_results - len(channel_ids)),
            pageToken=page_token,
        ).execute()

        channel_ids.extend(item["snippet"]["channelId"] for item in resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)  # be gentle with quota/rate

    leads = []
    # channels().list accepts up to 50 IDs per call.
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        try:
            resp = youtube.channels().list(
                part="snippet,statistics",
                id=",".join(batch),
            ).execute()
        except HttpError as e:
            raise RuntimeError(f"YouTube API error: {e}") from e

        for item in resp.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            subs = int(stats.get("subscriberCount", 0)) if not stats.get("hiddenSubscriberCount") else None

            if subs is not None:
                if subs < min_subscribers:
                    continue
                if max_subscribers is not None and subs > max_subscribers:
                    continue

            leads.append({
                "channel_id": item["id"],
                "title": snippet["title"],
                "email": _extract_email(snippet.get("description", "")),
                "subscriber_count": subs,
                "channel_url": f"https://www.youtube.com/channel/{item['id']}",
            })

    return leads
