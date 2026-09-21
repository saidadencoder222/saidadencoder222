"""Builds the pool of visuals for a video: for each [VISUAL: ...] cue from
the script, tries a real public-domain archival clip (Internet Archive)
first for variety, falling back to a license-checked Wikimedia Commons
still. Separately, `scene_timeline.build_timeline` cuts through this pool
on a fixed clock rather than one-per-cue, so the video keeps changing
scenes for engagement regardless of how many unique cues the script had.
"""
import os
from dataclasses import dataclass

from . import archive_video
from .visuals import SourcedImage, fetch_images


@dataclass
class Scene:
    kind: str  # "image" or "video"
    path: str
    attribution: SourcedImage | None = None  # set for image scenes needing CC credit


def build_pool(cfg: dict, keywords: list[str], out_dir: str) -> list[Scene]:
    os.makedirs(out_dir, exist_ok=True)
    pool_size = cfg["visuals"]["pool_size"]
    scene_seconds = cfg["video"]["scene_seconds"]
    try_video_fraction = cfg["visuals"].get("try_archive_video_first", True)

    scenes: list[Scene] = []
    keywords = keywords[:pool_size] if len(keywords) >= pool_size else _cycle(keywords, pool_size)

    still_keywords_needed = []
    for i, keyword in enumerate(keywords):
        if try_video_fraction:
            clip_path = os.path.join(out_dir, f"clip_{i:03d}.mp4")
            got_clip = archive_video.fetch_clip(keyword, clip_path, clip_seconds=scene_seconds)
            if got_clip:
                scenes.append(Scene(kind="video", path=clip_path))
                continue
        still_keywords_needed.append((i, keyword))

    if still_keywords_needed:
        images = fetch_images(
            cfg,
            [kw for _, kw in still_keywords_needed],
            out_dir,
            count_override=len(still_keywords_needed),
        )
        for img in images:
            scenes.append(Scene(kind="image", path=img.path, attribution=img))

    if not scenes:
        raise RuntimeError(
            f"No usable visuals (video or image) found for any of: {keywords}. "
            "Try a topic with more archival/photographic coverage."
        )
    return scenes


def _cycle(items: list[str], target_len: int) -> list[str]:
    if not items:
        return items
    out = []
    while len(out) < target_len:
        out.extend(items)
    return out[:target_len]
