"""Pulls public channel + recent video data from the YouTube Data API v3."""
import os
from googleapiclient.discovery import build


def get_client():
    api_key = os.environ["YOUTUBE_API_KEY"]
    return build("youtube", "v3", developerKey=api_key)


def resolve_channel_id(youtube, handle_or_id: str) -> str:
    """Accepts a channel ID (UC...), a @handle, or a custom URL slug."""
    if handle_or_id.startswith("UC"):
        return handle_or_id

    handle = handle_or_id.lstrip("@")
    resp = youtube.channels().list(part="id", forHandle=handle).execute()
    items = resp.get("items", [])
    if items:
        return items[0]["id"]

    resp = youtube.search().list(part="snippet", q=handle_or_id, type="channel", maxResults=1).execute()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Could not resolve channel for '{handle_or_id}'")
    return items[0]["snippet"]["channelId"]


def get_channel_data(youtube, channel_id: str) -> dict:
    resp = youtube.channels().list(
        part="snippet,statistics,contentDetails,brandingSettings",
        id=channel_id,
    ).execute()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"No channel found for id '{channel_id}'")
    channel = items[0]

    uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    recent_videos = get_recent_videos(youtube, uploads_playlist_id, max_results=15)

    return {
        "channel_id": channel_id,
        "title": channel["snippet"]["title"],
        "description": channel["snippet"].get("description", ""),
        "custom_url": channel["snippet"].get("customUrl", ""),
        "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
        "view_count": int(channel["statistics"].get("viewCount", 0)),
        "video_count": int(channel["statistics"].get("videoCount", 0)),
        "recent_videos": recent_videos,
    }


def get_recent_videos(youtube, uploads_playlist_id: str, max_results: int = 15) -> list[dict]:
    resp = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=max_results,
    ).execute()
    video_ids = [item["contentDetails"]["videoId"] for item in resp.get("items", [])]
    if not video_ids:
        return []

    stats_resp = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids),
    ).execute()

    videos = []
    for item in stats_resp.get("items", []):
        stats = item.get("statistics", {})
        videos.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"].get("description", ""),
            "published_at": item["snippet"]["publishedAt"],
            "duration": item["contentDetails"]["duration"],
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        })
    return videos
