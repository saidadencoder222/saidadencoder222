"""
Finds course-seller/finance-guru channels via the YouTube Data API and
computes a real, defensible audit from public data only - upload
consistency, recent view averages, and whether their bio even links
anywhere (a funnel/email capture gap). No claims about "all their
socials" - scoped to what YouTube's own API can verify, so nothing in
the pitch is fabricated.

Email is only pulled when a creator has put one directly in their
public channel description - same conservative pattern as
creator-outreach, no gated-page scraping.
"""

import re
import statistics
import time
from datetime import datetime, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
URL_RE = re.compile(r"https?://\S+")
IGNORED_DOMAINS = {"youtube.com", "google.com"}

RECENT_VIDEO_SAMPLE = 6


def _extract_email(description: str):
    for match in EMAIL_RE.findall(description or ""):
        domain = match.split("@")[-1].lower()
        if domain not in IGNORED_DOMAINS:
            return match
    return None


def _has_link_in_bio(description: str) -> bool:
    return bool(URL_RE.search(description or ""))


def _recent_upload_stats(youtube, uploads_playlist_id: str):
    """Returns (avg_views, gap_days_avg, gap_days_stdev) from the last
    RECENT_VIDEO_SAMPLE uploads, or (None, None, None) if unavailable."""
    try:
        resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=RECENT_VIDEO_SAMPLE,
        ).execute()
    except HttpError:
        return None, None, None

    items = resp.get("items", [])
    if len(items) < 2:
        return None, None, None

    video_ids = [i["contentDetails"]["videoId"] for i in items]
    published = [
        datetime.fromisoformat(i["contentDetails"]["videoPublishedAt"].replace("Z", "+00:00"))
        for i in items
    ]

    stats_resp = youtube.videos().list(part="statistics", id=",".join(video_ids)).execute()
    views = [int(v.get("statistics", {}).get("viewCount", 0)) for v in stats_resp.get("items", [])]
    avg_views = sum(views) // len(views) if views else None

    published.sort(reverse=True)
    gaps = [(published[i] - published[i + 1]).days for i in range(len(published) - 1)]
    gap_avg = round(statistics.mean(gaps), 1) if gaps else None
    gap_stdev = round(statistics.pstdev(gaps), 1) if len(gaps) > 1 else 0.0

    return avg_views, gap_avg, gap_stdev


def find_gurus(api_key: str, query: str, *, max_results: int = 25,
               min_subscribers: int = 5000, max_subscribers: int = None):
    youtube = build("youtube", "v3", developerKey=api_key)

    channel_ids = []
    page_token = None
    while len(channel_ids) < max_results:
        resp = youtube.search().list(
            part="snippet", q=query, type="channel",
            maxResults=min(50, max_results - len(channel_ids)),
            pageToken=page_token,
        ).execute()
        channel_ids.extend(item["snippet"]["channelId"] for item in resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)

    leads = []
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
            avg_views, gap_avg, gap_stdev = (None, None, None)
            if uploads_playlist:
                avg_views, gap_avg, gap_stdev = _recent_upload_stats(youtube, uploads_playlist)

            leads.append({
                "channel_id": item["id"],
                "title": snippet["title"],
                "email": _extract_email(snippet.get("description", "")),
                "subscriber_count": subs,
                "channel_url": f"https://www.youtube.com/channel/{item['id']}",
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url")
                    or snippet.get("thumbnails", {}).get("default", {}).get("url"),
                "avg_recent_views": avg_views,
                "upload_gap_days_avg": gap_avg,
                "upload_gap_days_stdev": gap_stdev,
                "has_link_in_bio": _has_link_in_bio(snippet.get("description", "")),
            })

    return leads
