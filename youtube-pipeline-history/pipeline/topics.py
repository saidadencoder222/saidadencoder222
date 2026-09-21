"""Picks the next history topic to produce a video for, cycling through
data/topics_pool.yaml and skipping anything already used per state.json.
When the pool is exhausted, asks Claude to brainstorm and append fresh
topics in the same style rather than repeating.
"""
import yaml

from . import state as state_mod


def _load_pool(pool_file: str) -> list[str]:
    with open(pool_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("topics", []))


def _append_pool(pool_file: str, new_topics: list[str]) -> None:
    with open(pool_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {"topics": []}
    data["topics"].extend(new_topics)
    with open(pool_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def next_topic(cfg: dict, anthropic_client) -> str:
    pool_file = cfg["niche"]["topic_pool_file"]
    state_file = cfg["niche"]["state_file"]

    pool = _load_pool(pool_file)
    used = set(state_mod.load(state_file)["used_topics"])

    for topic in pool:
        if topic not in used:
            return topic

    category = cfg["niche"]["category"]
    resp = anthropic_client.messages.create(
        model=cfg["llm"]["model"],
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate 20 new evergreen, high-search-demand YouTube video title "
                    f"ideas for a long-form {category} channel. Pick topics with strong "
                    f"photographic/archival coverage (so period photos/paintings/documents "
                    f"exist for them), specific and curiosity-driven, no misleading clickbait. "
                    f"Avoid duplicating these already-used titles: {sorted(used)[:50]}. "
                    f"Return ONLY a plain list, one title per line, no numbering."
                ),
            }
        ],
    )
    text = resp.content[0].text
    fresh = [line.strip("-* \t") for line in text.splitlines() if line.strip()]
    fresh = [t for t in fresh if t and t not in used]
    if not fresh:
        raise RuntimeError("Topic pool exhausted and Claude returned no new topics.")

    _append_pool(pool_file, fresh)
    return fresh[0]
