"""Generates the narration script for a history topic using Claude:
documentary-style long-form narration with [VISUAL: keyword] cues marking
where the imagery should change, used later to search Wikimedia Commons.
"""
import re
from dataclasses import dataclass

VISUAL_CUE_RE = re.compile(r"^\[VISUAL:\s*(.+?)\]\s*$", re.MULTILINE)


@dataclass
class Script:
    title_seed: str
    narration: str          # clean text for TTS, no cue lines
    visual_cues: list[str]  # ordered list of image search keywords


def generate_script(cfg: dict, anthropic_client, topic: str) -> Script:
    target_minutes = cfg["video"]["target_minutes"]
    words_per_minute = cfg["video"]["words_per_minute"]
    target_words = target_minutes * words_per_minute

    system_prompt = (
        "Act as a senior documentary scriptwriter for a long-form YouTube history channel. "
        "Turn the given topic into a compelling, well-researched narration: a strong hook "
        "opening, clear chronological or thematic structure, specific facts and figures "
        "(dates, names, numbers) rather than vague generalities, and a satisfying closing "
        "reflection. Write for voiceover narration only — no host, no dialogue, no stage "
        "directions. Every 1-2 sentences, insert a line of the exact form "
        "`[VISUAL: <short search phrase for a real historical photo, painting, map, or "
        "document related to this moment>]` on its own line to mark where the imagery should "
        "change. Keep visual search phrases specific and literal (e.g. 'Titanic launching "
        "1911' not 'sad ship'), since they'll be used as real search queries against a "
        "photo archive. Do not use markdown headers or speaker labels — output only "
        "narration sentences and [VISUAL: ...] cue lines."
    )
    user_prompt = (
        f"Topic: {topic}\n"
        f"Target length: approximately {target_words} words "
        f"(~{target_minutes} minutes of narration).\n"
        "Write the full script now."
    )

    resp = anthropic_client.messages.create(
        model=cfg["llm"]["model"],
        max_tokens=cfg["llm"]["max_tokens"],
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = resp.content[0].text

    visual_cues = VISUAL_CUE_RE.findall(raw)
    narration = VISUAL_CUE_RE.sub("", raw)
    narration = re.sub(r"\n{2,}", "\n\n", narration).strip()

    if not visual_cues:
        visual_cues = [topic]

    return Script(title_seed=topic, narration=narration, visual_cues=visual_cues)


def load_script_from_file(path: str, topic: str) -> Script:
    """Loads a script someone else wrote (e.g. pasted from a Claude chat)
    instead of calling the API. Same [VISUAL: ...] cue format as above."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    visual_cues = VISUAL_CUE_RE.findall(raw)
    narration = VISUAL_CUE_RE.sub("", raw)
    narration = re.sub(r"\n{2,}", "\n\n", narration).strip()

    if not visual_cues:
        visual_cues = [topic]

    return Script(title_seed=topic, narration=narration, visual_cues=visual_cues)
