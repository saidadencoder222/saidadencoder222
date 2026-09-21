"""Sources short public-domain archival VIDEO clips from the Internet
Archive — a real public-domain library with a free, keyless API — as an
alternative to a still image for a given visual cue, restricted to
collections documented as public domain. Anything outside those
collections, or with no usable video file, is skipped so callers can fall
back to a Wikimedia Commons still instead.

NOTE: outbound calls to archive.org could not be live-tested from this
development sandbox (network policy blocks it here) — this is written
against archive.org's documented advancedsearch/metadata API shapes, but
verify with `python main.py --dry-run` before trusting it unattended.
"""
import os
import random
import re
import subprocess

import requests

SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata/{identifier}"

# Collections documented as public domain (US government / ephemeral /
# educational films, NASA footage). Don't add a collection here without
# confirming its actual licensing — this list is what keeps this module
# copyright-safe.
PUBLIC_DOMAIN_COLLECTIONS = ["prelinger", "NASAarchive", "usgovfilms"]


def _search_items(query: str, limit: int) -> list[str]:
    collections = " OR ".join(f"collection:({c})" for c in PUBLIC_DOMAIN_COLLECTIONS)
    q = f"({collections}) AND mediatype:(movies) AND ({query})"
    resp = requests.get(
        SEARCH_URL,
        params={"q": q, "fl[]": "identifier", "rows": limit, "output": "json"},
        timeout=30,
    )
    resp.raise_for_status()
    return [d["identifier"] for d in resp.json().get("response", {}).get("docs", [])]


def _parse_length_seconds(length_field) -> float | None:
    if length_field is None:
        return None
    text = str(length_field).strip()
    try:
        return float(text)
    except ValueError:
        pass
    parts = text.split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        return None
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts[-3:]
    return h * 3600 + m * 60 + s


def _pick_mp4_file(identifier: str, min_seconds: float) -> tuple[str, float] | None:
    resp = requests.get(METADATA_URL.format(identifier=identifier), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    files = data.get("files", [])

    candidates = []
    for f in files:
        name = f.get("name", "")
        if not name.lower().endswith(".mp4"):
            continue
        duration = _parse_length_seconds(f.get("length"))
        if duration is None or duration < min_seconds:
            continue
        candidates.append((name, duration))
    if not candidates:
        return None

    # Prefer a shorter derivative over a full-length feature when several exist.
    candidates.sort(key=lambda c: c[1])
    name, duration = candidates[0]
    return f"https://archive.org/download/{identifier}/{name}", duration


def fetch_clip(query: str, out_path: str, clip_seconds: float, ffmpeg_bin: str = "ffmpeg", search_limit: int = 5) -> bool:
    """Downloads a random `clip_seconds`-long segment matching `query` to
    out_path. Returns False (writes nothing) if no suitable public-domain
    clip was found, so the caller can fall back to a still image."""
    try:
        identifiers = _search_items(query, search_limit)
    except requests.RequestException:
        return False

    for identifier in identifiers:
        try:
            picked = _pick_mp4_file(identifier, clip_seconds)
        except requests.RequestException:
            continue
        if not picked:
            continue
        url, duration = picked

        start = random.uniform(0, max(duration - clip_seconds - 1, 0))
        result = subprocess.run(
            [
                ffmpeg_bin, "-y", "-ss", str(start), "-i", url, "-t", str(clip_seconds),
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", out_path, "-loglevel", "error",
            ],
            capture_output=True, timeout=120,
        )
        if result.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return True

    return False
