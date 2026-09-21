"""Picks the next countdown topic to produce a video for: cycles through
data/topics_pool.yaml, skipping topics already used (per state.json) and
topics whose clip_bank/<clip_tag>/ folder isn't populated yet. When every
unused topic lacks clips, asks Claude to brainstorm fresh ones so the pool
never just repeats — but a fresh topic still needs its clip_bank folder
populated before it can actually run.
"""
import yaml

from . import clip_bank
from . import state as state_mod


def _load_pool(pool_file: str) -> list[dict]:
    with open(pool_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("topics", []))


def _append_pool(pool_file: str, new_topics: list[dict]) -> None:
    with open(pool_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {"topics": []}
    data["topics"].extend(new_topics)
    with open(pool_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def _slugify(title: str) -> str:
    return "-".join(w.lower() for w in title.split() if w.isalnum())[:40]


def next_topic(cfg: dict, anthropic_client) -> dict:
    pool_file = cfg["niche"]["topic_pool_file"]
    state_file = cfg["niche"]["state_file"]
    clip_bank_dir = cfg["clip_bank"]["dir"]

    pool = _load_pool(pool_file)
    used = set(state_mod.load(state_file)["used_topics"])

    ready = [t for t in pool if t["title"] not in used and clip_bank.has_clips(clip_bank_dir, t["clip_tag"])]
    if ready:
        return ready[0]

    unused_but_empty = [t for t in pool if t["title"] not in used]
    if unused_but_empty:
        tags = ", ".join(sorted({t["clip_tag"] for t in unused_but_empty}))
        raise RuntimeError(
            "No topic is ready to run: every unused topic in the pool needs clips added to "
            f"clip_bank/<clip_tag>/ first. Populate one of: {tags}. See clip_bank/README.md."
        )

    # Every topic used: ask Claude for fresh ideas. Still requires you to
    # populate the corresponding clip_bank folder before it can run.
    category = cfg["niche"]["category"]
    resp = anthropic_client.messages.create(
        model=cfg["llm"]["model"],
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate 15 new 'Top 10 ... Moments' style YouTube countdown video title "
                    f"ideas for a {category} channel. For each, give a short kebab-case tag "
                    f"identifying the character/franchise (e.g. 'hulk', 'iron-man', 'batman'). "
                    f"Avoid duplicating these already-used titles: {sorted(used)[:50]}. "
                    'Respond ONLY as JSON: [{"title": "...", "clip_tag": "..."}, ...]'
                ),
            }
        ],
    )
    import json
    import re

    text = resp.content[0].text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    fresh = json.loads(match.group(0)) if match else []
    fresh = [t for t in fresh if t.get("title") not in used]
    if not fresh:
        raise RuntimeError("Topic pool exhausted and Claude returned no new topics.")

    _append_pool(pool_file, fresh)

    ready = [t for t in fresh if clip_bank.has_clips(clip_bank_dir, t["clip_tag"])]
    if not ready:
        tags = ", ".join(sorted({t["clip_tag"] for t in fresh}))
        raise RuntimeError(
            f"Added new topics but none have clips yet. Populate clip_bank/<tag>/ for one of: {tags}."
        )
    return ready[0]
