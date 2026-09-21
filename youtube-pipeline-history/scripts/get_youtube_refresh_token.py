"""One-time local setup: obtains a long-lived YouTube OAuth refresh token.

Run this once on your own machine (not in CI):

    python scripts/get_youtube_refresh_token.py \
        --client-id YOUR_CLIENT_ID \
        --client-secret YOUR_CLIENT_SECRET

It opens a browser for you to log in and grant upload access to your
YouTube channel, then prints a refresh token. Save that as the
YOUTUBE_REFRESH_TOKEN GitHub Actions secret (along with the client id/secret
you passed in) — the pipeline uses it on every run without you logging in
again.

Prerequisite: create an OAuth 2.0 Client ID (type "Desktop app") in Google
Cloud Console for a project that has the YouTube Data API v3 enabled, and
add yourself as a test user (or publish the OAuth consent screen) since
this scope is sensitive.
"""
import argparse

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    args = parser.parse_args()

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\nSave this as the YOUTUBE_REFRESH_TOKEN secret:\n")
    print(creds.refresh_token)


if __name__ == "__main__":
    main()
