"""Sources real historical imagery from Wikimedia Commons — a genuinely
public-domain / Creative-Commons-licensed archive, searchable via a free,
keyless API. No scraping of copyrighted material, no manual asset prep:
this is the piece that makes the pipeline actually zero-manual-work.

Every image's license is checked against config.yaml's allowed_licenses
before use; anything unlicensed or unclear is skipped rather than assumed
safe. CC-BY/CC-BY-SA images require attribution, so we track it here and
metadata.py appends it to the video description.
"""
import os
import time
from dataclasses import dataclass

import requests

API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "history-doc-pipeline/1.0 (educational documentary project)"}
# Wikimedia rate-limits anonymous API clients; firing ~30 searches back-to-back
# (one per visual cue) reliably triggers 429s without pacing/backoff, and once
# triggered the cooldown can outlast a few quick retries.
REQUEST_DELAY_S = 3.0
MAX_RETRIES = 6


@dataclass
class SourcedImage:
    path: str
    title: str
    author: str
    license_short_name: str
    source_url: str

    @property
    def needs_attribution(self) -> bool:
        return not self.license_short_name.lower().startswith(("public domain", "pd-", "cc0"))

    @property
    def attribution_line(self) -> str:
        return f'"{self.title}" by {self.author}, {self.license_short_name} (via Wikimedia Commons) — {self.source_url}'


def _search_commons_image(query: str, allowed_licenses: set[str]) -> dict | None:
    """Returns None (rather than raising) if Commons can't be reached after
    retries, so one rate-limited/flaky keyword doesn't kill the whole run —
    the caller just moves on to the next cue."""
    backoff = 3.0
    resp = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                API_URL,
                headers=HEADERS,
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": f"{query} filetype:bitmap",
                    "gsrnamespace": 6,  # File: namespace
                    "gsrlimit": 8,
                    "prop": "imageinfo",
                    "iiprop": "url|extmetadata",
                    "iiurlwidth": 1600,
                },
                timeout=30,
            )
        except requests.RequestException as e:
            print(f"    [visuals] request error for '{query}': {e}")
            return None

        if resp.status_code == 429:
            wait = float(resp.headers.get("Retry-After", backoff))
            if attempt < MAX_RETRIES - 1:
                print(f"    [visuals] rate-limited on '{query}', waiting {wait:.0f}s "
                      f"(attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait)
                backoff *= 2
                continue
            print(f"    [visuals] still rate-limited on '{query}' after {MAX_RETRIES} attempts, skipping")
            return None
        break

    if not resp.ok:
        print(f"    [visuals] HTTP {resp.status_code} for '{query}', skipping")
        return None

    pages = resp.json().get("query", {}).get("pages", {})

    for page in pages.values():
        infos = page.get("imageinfo")
        if not infos:
            continue
        info = infos[0]
        meta = info.get("extmetadata", {})
        license_short = meta.get("LicenseShortName", {}).get("value", "")
        if license_short not in allowed_licenses:
            continue
        return {
            "title": page.get("title", "").removeprefix("File:"),
            "author": _strip_html(meta.get("Artist", {}).get("value", "Unknown")),
            "license_short_name": license_short,
            "url": info.get("thumburl") or info.get("url"),
            "source_url": info.get("descriptionurl", ""),
        }
    return None


def _strip_html(text: str) -> str:
    import re

    return re.sub(r"<[^>]+>", "", text).strip() or "Unknown"


def fetch_images(cfg: dict, keywords: list[str], out_dir: str, count_override: int | None = None) -> list[SourcedImage]:
    os.makedirs(out_dir, exist_ok=True)
    allowed = set(cfg["visuals"]["allowed_licenses"])
    max_images = count_override if count_override is not None else cfg["visuals"]["pool_size"]

    results: list[SourcedImage] = []
    for i, keyword in enumerate(keywords[:max_images]):
        if i > 0:
            time.sleep(REQUEST_DELAY_S)  # pace requests, Commons rate-limits bursts
        found = _search_commons_image(keyword, allowed)
        if not found:
            continue
        path = os.path.join(out_dir, f"img_{i:03d}.jpg")
        try:
            with requests.get(found["url"], headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
        except requests.RequestException as e:
            print(f"    [visuals] download failed for '{keyword}': {e}, skipping")
            continue
        results.append(
            SourcedImage(
                path=path,
                title=found["title"],
                author=found["author"],
                license_short_name=found["license_short_name"],
                source_url=found["source_url"],
            )
        )

    if not results:
        raise RuntimeError(
            "No properly-licensed images found on Wikimedia Commons for any of the "
            f"visual cues: {keywords}. Try a topic with more archival coverage."
        )
    return results
