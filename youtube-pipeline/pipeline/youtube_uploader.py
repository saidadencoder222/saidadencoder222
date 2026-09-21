"""Uploads the finished video + thumbnail to YouTube via the Data API v3,
authenticating with a long-lived refresh token (see
scripts/get_youtube_refresh_token.py for the one-time setup flow).
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_client(client_id: str, client_secret: str, refresh_token: str):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def upload_video(
    *,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str,
    privacy_status: str,
    made_for_kids: bool,
) -> str:
    youtube = _get_client(client_id, client_secret, refresh_token)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]

    youtube.thumbnails().set(
        videoId=video_id, media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
    ).execute()

    return video_id
