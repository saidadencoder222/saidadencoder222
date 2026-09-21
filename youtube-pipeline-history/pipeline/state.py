"""Tracks which topics have been used and what's been uploaded, so repeated
runs don't repeat themselves. Backed by a plain JSON file.
"""
import json
import os
from datetime import datetime, timezone


def load(state_file: str) -> dict:
    if not os.path.exists(state_file):
        return {"used_topics": [], "uploads": []}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save(state_file: str, state: dict) -> None:
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def record_upload(state_file: str, *, topic: str, video_id: str | None, title: str) -> None:
    state = load(state_file)
    if topic not in state["used_topics"]:
        state["used_topics"].append(topic)
    state["uploads"].append(
        {
            "topic": topic,
            "title": title,
            "video_id": video_id,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save(state_file, state)
