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

Also supports filtering by the channel's most recent upload - view count
and how long ago it was posted - as a cheap proxy for "active and getting
real reach right now" rather than just raw subscriber count.
"""

import re
import time
from datetime import datetime, timedelta, timezone

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


def _latest_video_info(youtube, uploads_playlist_id: str):
    """Returns (video_id, published_at) for a channel's most recent upload."""
    try:
        resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=1,
        ).execute()
    except HttpError:
        return None, None

    items = resp.get("items", [])
    if not items:
        return None, None

    details = items[0]["contentDetails"]
    return details.get("videoId"), details.get("videoPublishedAt")


def find_creators(api_key: str, query: str, *, max_results: int = 50,
                   min_subscribers: int = 0, max_subscribers: int = None,
                   min_recent_views: int = 0, max_video_age_days: int = None):
    """Search channels matching `query`, yield dicts with lead info.

    Only uses public search.list / channels.list / playlistItems.list
    endpoints - no scraping. `min_recent_views`/`max_video_age_days` filter
    on the channel's single most recent upload, as a proxy for "actively
    posting and currently getting real reach" rather than raw sub count.
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

    candidates = []
    # channels().list accepts up to 50 IDs per call.
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        try:
            resp = youtube.channels().list(
                part="snippet,statistics,contentDetails",
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

            uploads_playlist = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

            candidates.append({
                "channel_id": item["id"],
                "title": snippet["title"],
                "email": _extract_email(snippet.get("description", "")),
                "subscriber_count": subs,
                "channel_url": f"https://www.youtube.com/channel/{item['id']}",
                "uploads_playlist": uploads_playlist,
            })

    if not min_recent_views and max_video_age_days is None:
        for c in candidates:
            c.pop("uploads_playlist", None)
        return candidates

    # Look up each candidate's most recent video, then batch-fetch view counts.
    video_ids_by_channel = {}
    for c in candidates:
        if not c["uploads_playlist"]:
            continue
        video_id, published_at = _latest_video_info(youtube, c["uploads_playlist"])
        if video_id:
            video_ids_by_channel[c["channel_id"]] = (video_id, published_at)

    view_counts = {}
    video_ids = [v[0] for v in video_ids_by_channel.values()]
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        resp = youtube.videos().list(part="statistics", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            view_counts[item["id"]] = int(item.get("statistics", {}).get("viewCount", 0))

    now = datetime.now(timezone.utc)
    leads = []
    for c in candidates:
        video_info = video_ids_by_channel.get(c["channel_id"])
        c.pop("uploads_playlist", None)
        if not video_info:
            continue

        video_id, published_at = video_info
        views = view_counts.get(video_id, 0)
        if views < min_recent_views:
            continue

        if max_video_age_days is not None and published_at:
            age_days = (now - datetime.fromisoformat(published_at.replace("Z", "+00:00"))).days
            if age_days > max_video_age_days:
                continue

        c["latest_video_views"] = views
        c["latest_video_published_at"] = published_at
        leads.append(c)

    return leads
