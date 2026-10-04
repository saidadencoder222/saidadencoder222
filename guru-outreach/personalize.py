"""
Per-creator personalization for the preview PDF.

Ideally this would pull each channel's own avatar and derive a true
brand color from it - the code for that is below and works fine
outside this specific sandbox. But this environment's outbound network
policy blocks arbitrary external image hosts (confirmed: YouTube's own
thumbnail CDN gets a 403 at the proxy, while official *.googleapis.com
API calls go through fine), so avatar fetches here are unreliable.

Instead, the default path is a deterministic per-channel color picked
from a curated, tasteful palette - real per-creator variation with zero
network dependency, so a batch send never stalls or silently falls back
to grey because one image host was unreachable.
"""

import hashlib
import io

import requests
from PIL import Image

DEFAULT_ACCENT = "#1f2937"

# Muted, professional tones - avoids anything that reads as spammy/neon.
PALETTE = [
    "#b45309",  # warm terracotta
    "#166534",  # sage green
    "#1e40af",  # dusty blue
    "#6b21a8",  # plum
    "#a16207",  # mustard
    "#0f766e",  # teal
    "#9d174d",  # rose
    "#1e293b",  # navy
]


def get_palette_accent(key: str) -> str:
    """Deterministic accent color for a given channel_id/title - same
    creator always gets the same color, different creators spread across
    the palette. No network call, so this always works."""
    digest = hashlib.sha256((key or "").encode()).hexdigest()
    index = int(digest, 16) % len(PALETTE)
    return PALETTE[index]


def get_accent_color(thumbnail_url: str) -> str:
    """Downloads a channel's own avatar and returns its dominant color as hex."""
    if not thumbnail_url:
        return DEFAULT_ACCENT

    try:
        resp = requests.get(thumbnail_url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception:
        return DEFAULT_ACCENT

    img = img.resize((32, 32))
    pixels = list(img.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)

    # Darken if the average is too light/washed out to read as a heading color.
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    if luminance > 200:
        r, g, b = (int(c * 0.6) for c in (r, g, b))

    return f"#{r:02x}{g:02x}{b:02x}"


def save_circular_avatar(thumbnail_url: str, dest_path: str, size: int = 240) -> bool:
    """Downloads a channel's own avatar and saves a circular-cropped PNG."""
    if not thumbnail_url:
        return False

    try:
        resp = requests.get(thumbnail_url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    except Exception:
        return False

    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    circular = Image.new("RGBA", (size, size))
    circular.paste(img, (0, 0), mask=mask)
    circular.save(dest_path, "PNG")
    return True
