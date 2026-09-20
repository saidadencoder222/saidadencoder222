"""
Per-creator personalization: pulls each channel's own public avatar
(official API thumbnail field, not scraped) and derives an accent color
from it, so their copy of the preview PDF is themed to match their own
channel instead of every creator getting an identical generic document.
"""

import io

import requests
from PIL import Image

DEFAULT_ACCENT = "#1f2937"


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


def download_avatar(thumbnail_url: str, dest_path: str) -> bool:
    if not thumbnail_url:
        return False
    try:
        resp = requests.get(thumbnail_url, timeout=10)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False
