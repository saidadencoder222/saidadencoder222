"""Generates a "Top N [Topic] Moments" countdown script — a proven,
high-retention long-form format — for the movie clips available in the
local clip bank, using Claude. Clip content is inferred only from the
filename you gave each clip (name them descriptively, e.g.
03_hulk_vs_loki_avengers.mp4) — Claude does not watch the footage.
"""
import json
import re
from dataclasses import dataclass


@dataclass
class Moment:
    rank: int
    clip_path: str
    narration: str


@dataclass
class Script:
    title_seed: str
    intro_narration: str
    moments: list[Moment]

    @property
    def full_text(self) -> str:
        return self.intro_narration + "\n" + "\n".join(m.narration for m in self.moments)


def generate_script(cfg: dict, anthropic_client, topic_title: str, clip_paths: list[str], clip_labels: list[str]) -> Script:
    n = len(clip_paths)
    system_prompt = (
        "Act as a senior YouTube scriptwriter specializing in movie countdown/compilation "
        "channels — a proven, high-retention long-form format. Write a 'Top " + str(n) + "' "
        "countdown script for the given topic, counting down from #" + str(n) + " to #1. You are "
        "given the labeled moments available, in the order they'll be shown (#" + str(n) + " first, "
        "#1 last = the best). For EACH moment write 3-5 sentences of punchy narration that sets up "
        "context, builds anticipation, and reacts to that specific moment, using its label as your "
        "only information about what happens in it. Use curiosity hooks, pattern changes, and "
        "engagement techniques (rhetorical questions, callbacks, escalating stakes toward #1) to "
        "maximize retention. Also write a short, high-energy 4-6 sentence hook intro for the very "
        "start of the video that previews what's coming without giving away #1. "
        "Respond ONLY with valid JSON of the form: "
        '{"intro": "...", "moments": ["moment 1 narration", "moment 2 narration", ...]} '
        "where moments[] has exactly " + str(n) + " entries, in the same order as the labels given."
    )
    labeled = "\n".join(f"#{n - i} - {label}" for i, label in enumerate(clip_labels))
    user_prompt = f"Topic: {topic_title}\n\nMoments (in countdown order, #{n} first to #1 last):\n{labeled}"

    resp = anthropic_client.messages.create(
        model=cfg["llm"]["model"],
        max_tokens=cfg["llm"]["max_tokens"],
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = resp.content[0].text.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise RuntimeError(f"Script generation did not return JSON: {raw[:300]}")
    data = json.loads(match.group(0))

    moments_narration = data["moments"]
    if len(moments_narration) != n:
        raise RuntimeError(f"Expected {n} moment narrations, got {len(moments_narration)}")

    moments = [
        Moment(rank=n - i, clip_path=clip_path, narration=narration)
        for i, (clip_path, narration) in enumerate(zip(clip_paths, moments_narration))
    ]

    return Script(title_seed=topic_title, intro_narration=data["intro"], moments=moments)
