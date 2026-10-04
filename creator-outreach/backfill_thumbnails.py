"""One-off: fills in thumbnail_url for leads stored before that column
existed, by re-querying channels().list (cheap - snippet part only)."""

from googleapiclient.discovery import build

from config import CONFIG
from storage import connect

def run():
    with connect(CONFIG.db_path) as conn:
        rows = conn.execute(
            "SELECT channel_id FROM leads WHERE thumbnail_url IS NULL"
        ).fetchall()
        ids = [r["channel_id"] for r in rows]
        if not ids:
            print("Nothing to backfill.")
            return

        youtube = build("youtube", "v3", developerKey=CONFIG.youtube_api_key)
        updated = 0
        for i in range(0, len(ids), 50):
            batch = ids[i:i + 50]
            resp = youtube.channels().list(part="snippet", id=",".join(batch)).execute()
            for item in resp.get("items", []):
                thumb = (item["snippet"].get("thumbnails", {}).get("high", {}).get("url")
                         or item["snippet"].get("thumbnails", {}).get("default", {}).get("url"))
                if thumb:
                    conn.execute(
                        "UPDATE leads SET thumbnail_url = ? WHERE channel_id = ?",
                        (thumb, item["id"]),
                    )
                    updated += 1
            conn.commit()
        print(f"Backfilled {updated}/{len(ids)} thumbnail(s).")


if __name__ == "__main__":
    run()
