"""OPTIONAL, experimental: animates a still image into a short original
AI-generated video clip via Stability AI's image-to-video API, instead of
a static Ken Burns zoom — pure visual variety, not a substitute for
sourcing real footage of anything. Off by default (visuals.ai_animate_fraction
= 0 in config.yaml); requires your own STABILITY_API_KEY.

NOT live-tested from this development sandbox (no key available, and
outbound calls to api.stability.ai are blocked by this sandbox's network
policy) — written against Stability's documented v2beta async job shape
(submit -> poll result). Validate with a single --dry-run before relying
on it, and expect to need small fixes if their API has moved since.
"""
import time

import requests

SUBMIT_URL = "https://api.stability.ai/v2beta/image-to-video"
RESULT_URL = "https://api.stability.ai/v2beta/image-to-video/result/{id}"


def animate_image(image_path: str, out_path: str, api_key: str, seed: int = 0, poll_timeout_s: int = 120) -> bool:
    """Returns True and writes out_path on success; False (writes nothing)
    on any failure, so callers fall back to a static Ken Burns clip."""
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(
                SUBMIT_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                files={"image": f},
                data={"seed": seed, "cfg_scale": 1.8, "motion_bucket_id": 127},
                timeout=60,
            )
        resp.raise_for_status()
        generation_id = resp.json()["id"]

        deadline = time.time() + poll_timeout_s
        while time.time() < deadline:
            result = requests.get(
                RESULT_URL.format(id=generation_id),
                headers={"Authorization": f"Bearer {api_key}", "Accept": "video/*"},
                timeout=30,
            )
            if result.status_code == 202:
                time.sleep(5)
                continue
            result.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(result.content)
            return True
        return False
    except (requests.RequestException, KeyError, OSError):
        return False
