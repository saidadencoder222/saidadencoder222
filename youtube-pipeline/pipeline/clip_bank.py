"""Local movie clip bank the pipeline builds videos from.

This module deliberately does NOT scrape, download, or fetch copyrighted
movie footage from clip.cafe or anywhere else. Automating extraction of
copyrighted film clips for redistribution in monetized videos is copyright
infringement regardless of the source site, so that step is intentionally
left manual: you populate clip_bank/<clip_tag>/ yourself with clips you
have the legal right to use, and this module just indexes what's there.

Filenames double as the only information Claude gets about what happens in
each clip, so name them descriptively:
    clip_bank/hulk/03_hulk_vs_loki_avengers.mp4
    clip_bank/hulk/07_hulk_smash_abomination.mp4
"""
import os
import random

from moviepy import VideoFileClip

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".webm")


def has_clips(clip_bank_dir: str, clip_tag: str) -> bool:
    folder = os.path.join(clip_bank_dir, clip_tag)
    if not os.path.isdir(folder):
        return False
    return any(f.lower().endswith(VIDEO_EXTENSIONS) for f in os.listdir(folder))


def list_clips(clip_bank_dir: str, clip_tag: str, max_clips: int) -> list[str]:
    folder = os.path.join(clip_bank_dir, clip_tag)
    if not os.path.isdir(folder):
        raise RuntimeError(
            f"No clip bank folder for '{clip_tag}'. Create {folder}/ and add clips "
            f"you have the legal right to use before running this topic."
        )
    files = sorted(
        os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXTENSIONS)
    )
    if not files:
        raise RuntimeError(f"{folder}/ exists but has no video clips in it yet.")
    random.shuffle(files)
    return files[:max_clips]


def clip_label(path: str) -> str:
    """Turns '03_hulk_vs_loki_avengers.mp4' into 'hulk vs loki avengers'."""
    name = os.path.splitext(os.path.basename(path))[0]
    parts = name.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    return " ".join(parts) if parts else name


def extract_thumbnail_frame(clip_path: str, out_path: str, at_fraction: float = 0.5) -> str:
    clip = VideoFileClip(clip_path)
    try:
        clip.save_frame(out_path, t=clip.duration * at_fraction)
    finally:
        clip.close()
    return out_path
