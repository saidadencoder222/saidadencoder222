"""Generates the click-worthy title, SEO description, and tags for a
finished video, then appends required Creative Commons attribution for any
image that needs it.
"""
import json
import re
from dataclasses import dataclass

from .visuals import SourcedImage


@dataclass
class Metadata:
    title: str
    description: str
    tags: list[str]


def generate_metadata(cfg: dict, anthropic_client, topic: str, narration: str, images: list[SourcedImage]) -> Metadata:
    system_prompt = (
        "Act as an elite YouTube title strategist and SEO copywriter for a history "
        "documentary channel. Given a video topic and its narration script, produce ONE "
        "high-click title using curiosity, specificity, and a clear viewer outcome (no "
        "misleading clickbait — the title must accurately represent the video), a "
        "keyword-rich YouTube description (150-250 words, a one-line hook then a short "
        "summary, no links), and 10-15 relevant tags. "
        "Respond ONLY with valid JSON: "
        '{"title": "...", "description": "...", "tags": ["...", ...]}'
    )
    user_prompt = f"Topic: {topic}\n\nNarration script (for context):\n{narration[:6000]}"

    resp = anthropic_client.messages.create(
        model=cfg["llm"]["model"],
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = resp.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise RuntimeError(f"Metadata generation did not return JSON: {raw[:300]}")
    data = json.loads(match.group(0))
    return _to_metadata(data, images)


def load_metadata_from_file(path: str, images: list[SourcedImage]) -> Metadata:
    """Loads title/description/tags someone else wrote (e.g. pasted from a
    Claude chat) instead of calling the API. Expects a JSON file:
    {"title": "...", "description": "...", "tags": ["...", ...]}"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _to_metadata(data, images)


def _to_metadata(data: dict, images: list[SourcedImage]) -> Metadata:
    description = data["description"].strip()
    attributions = [img.attribution_line for img in images if img.needs_attribution]
    if attributions:
        description += "\n\nImage credits (Creative Commons, via Wikimedia Commons):\n"
        description += "\n".join(f"- {line}" for line in attributions)

    return Metadata(
        title=data["title"].strip()[:100],
        description=description,
        tags=[t.strip() for t in data.get("tags", [])][:15],
    )
