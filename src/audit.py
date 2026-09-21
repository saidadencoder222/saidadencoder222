"""Turns raw channel data into a list of weak-point findings + suggestions.

Deliberately text/stats-only: it never touches thumbnails, video frames, or
profile images, so the proposal page never redistributes the prospect's own
media without consent.
"""
from datetime import datetime, timezone
import re

LINK_RE = re.compile(r"https?://\S+")


def _days_since(iso_ts: str) -> int:
    published = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - published).days


def _upload_gaps_days(videos: list[dict]) -> list[int]:
    dates = sorted(
        (datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) for v in videos),
        reverse=True,
    )
    return [(dates[i] - dates[i + 1]).days for i in range(len(dates) - 1)]


def run_audit(channel: dict) -> list[dict]:
    findings = []
    videos = channel["recent_videos"]

    if not videos:
        findings.append({
            "title": "No recent uploads found",
            "severity": "high",
            "detail": "Could not find recent public videos to analyze.",
            "suggestion": "Confirm the channel is active and public.",
        })
        return findings

    # 1. Upload consistency / recency
    last_upload_days = _days_since(videos[0]["published_at"])
    if last_upload_days > 21:
        findings.append({
            "title": "Inconsistent upload cadence",
            "severity": "high" if last_upload_days > 45 else "medium",
            "detail": f"Last upload was {last_upload_days} days ago.",
            "suggestion": "A predictable weekly cadence compounds algorithmic reach and keeps warm leads engaged between launches.",
        })

    gaps = _upload_gaps_days(videos)
    if gaps and (max(gaps) - min(gaps) > 20):
        findings.append({
            "title": "Erratic posting schedule",
            "severity": "medium",
            "detail": f"Recent gaps between uploads range from {min(gaps)} to {max(gaps)} days.",
            "suggestion": "Batch-producing content and scheduling releases smooths out the algorithm's confidence in the channel.",
        })

    # 2. Engagement rate vs views
    engagement_rates = []
    for v in videos:
        if v["view_count"] > 0:
            rate = (v["like_count"] + v["comment_count"]) / v["view_count"]
            engagement_rates.append(rate)
    if engagement_rates:
        avg_engagement = sum(engagement_rates) / len(engagement_rates)
        if avg_engagement < 0.02:
            findings.append({
                "title": "Low engagement relative to views",
                "severity": "medium",
                "detail": f"Average like+comment rate across recent videos is {avg_engagement:.1%}.",
                "suggestion": "Stronger on-screen CTAs and pinned comments asking a direct question can lift engagement, which YouTube rewards with more reach.",
            })

    # 3. Lead capture / monetization links in channel description
    channel_links = LINK_RE.findall(channel["description"])
    if len(channel_links) == 0:
        findings.append({
            "title": "No monetization or lead-capture links in channel bio",
            "severity": "high",
            "detail": "The channel description has no outbound links.",
            "suggestion": "Add a link to a lead magnet, waitlist, or flagship offer directly in the About section — it's free real estate that's currently unused.",
        })

    # 4. Video descriptions missing CTAs/links
    videos_without_links = sum(1 for v in videos if not LINK_RE.search(v["description"]))
    if videos_without_links / len(videos) > 0.5:
        findings.append({
            "title": "Most video descriptions have no call-to-action link",
            "severity": "medium",
            "detail": f"{videos_without_links}/{len(videos)} recent videos have no link in the description.",
            "suggestion": "A consistent first-line CTA link (offer, calendar, freebie) in every description turns passive viewers into a funnel.",
        })

    # 5. Underused monetization surface area — single offer signal
    offer_keywords = ["course", "coaching", "membership", "mentorship", "program", "community"]
    mentions = sum(1 for kw in offer_keywords if kw in channel["description"].lower())
    if mentions <= 1:
        findings.append({
            "title": "Narrow monetization footprint",
            "severity": "medium",
            "detail": "Channel bio references at most one monetized offer.",
            "suggestion": "Layering a low-ticket digital product, an affiliate stack, and a high-ticket cohort/coaching tier captures buyers at every intent level, not just one.",
        })

    return findings
