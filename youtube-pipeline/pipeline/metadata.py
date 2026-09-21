"""Generates the click-worthy title, SEO description, and tags for a
finished video, in the style of the "elite YouTube title strategist" prompt.
"""
import json
import re
from dataclasses import dataclass


@dataclass
class Metadata:
    title: str
    description: str
    tags: list[str]


def generate_metadata(cfg: dict, anthropic_client, topic: str, narration: str) -> Metadata:
    system_prompt = (
        "Act as an elite YouTube title strategist and SEO copywriter. Given a video topic "
        "and its narration script, produce ONE high-click title using curiosity, specificity, "
        "tension, and a clear viewer outcome (no misleading clickbait — the title must "
        "accurately represent the video), a keyword-rich YouTube description (150-250 words, "
        "include a one-line hook, then a short summary, no links), and 10-15 relevant tags. "
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
    return Metadata(
        title=data["title"].strip()[:100],
        description=data["description"].strip(),
        tags=[t.strip() for t in data.get("tags", [])][:15],
    )
