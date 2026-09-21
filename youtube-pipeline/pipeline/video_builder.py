"""Assembles the final MP4 from real movie clips: an intro segment, then one
segment per countdown moment (clip trimmed/centered to the narration
length, "#N" rank badge, burned-in captions synced to word timing),
concatenated in order with narration audio and optional background music.

Captions/badges are rendered as transparent PNGs with Pillow rather than
moviepy's TextClip, so the pipeline doesn't need ImageMagick on the runner.

Written against moviepy 2.x (no `moviepy.editor`; clip methods are
`with_*` / `resized` / `cropped` / `subclipped`, and transforms like
looping or volume scaling are `Effect` objects passed to `with_effects`).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    afx,
    concatenate_videoclips,
    vfx,
)

from .voiceover import Voiceover

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def _fit_clip(clip, resolution: tuple[int, int]):
    clip = clip.resized(height=resolution[1])
    if clip.w < resolution[0]:
        clip = clip.resized(width=resolution[0])
    return clip.cropped(
        x_center=clip.w / 2, y_center=clip.h / 2, width=resolution[0], height=resolution[1]
    )


def _caption_groups(vo: Voiceover, words_per_group: int) -> list[tuple[str, float, float]]:
    if not vo.word_timings:
        return []
    groups = []
    words = vo.word_timings
    for i in range(0, len(words), words_per_group):
        chunk = words[i : i + words_per_group]
        text = " ".join(w.text for w in chunk)
        start = chunk[0].start_s
        end = chunk[-1].start_s + chunk[-1].duration_s
        groups.append((text, start, max(end - start, 0.4)))
    return groups


def _caption_image(text: str, width: int) -> Image.Image:
    font = _font(50)
    img = Image.new("RGBA", (width, 180), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (width - tw) / 2, (180 - th) / 2
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return img


def _rank_badge(text: str) -> Image.Image:
    font = _font(70)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0] + 50, bbox[3] - bbox[1] + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w, h], radius=18, fill=(0, 0, 0, 190))
    draw.text((25, 12), text, font=font, fill=(255, 210, 0, 255))
    return img


def _audio_duration(vo: Voiceover) -> float:
    return vo.duration_s or AudioFileClip(vo.audio_path).duration


def _segment_clip(clip_path: str, audio: Voiceover, resolution: tuple[int, int], rank_label: str | None, words_per_group: int):
    duration = _audio_duration(audio)

    base = VideoFileClip(clip_path).without_audio()
    if base.duration < duration:
        base = base.with_effects([vfx.Loop(duration=duration)])
    else:
        start = max((base.duration - duration) / 2, 0)
        base = base.subclipped(start, start + duration)
    base = _fit_clip(base, resolution)

    overlays = []
    if rank_label:
        badge_img = _rank_badge(rank_label)
        overlays.append(
            ImageClip(np.array(badge_img)).with_position((40, 40)).with_duration(duration)
        )
    for text, start, dur in _caption_groups(audio, words_per_group):
        cap_img = _caption_image(text, resolution[0])
        overlays.append(
            ImageClip(np.array(cap_img))
            .with_start(start)
            .with_duration(dur)
            .with_position(("center", resolution[1] - 240))
        )

    segment = CompositeVideoClip([base, *overlays], size=resolution).with_duration(duration)
    segment = segment.with_audio(AudioFileClip(audio.audio_path))
    return segment


def build_video(
    cfg: dict,
    intro_audio: Voiceover,
    moment_segments: list[tuple[str, Voiceover, str]],
    music_path: str | None,
    out_path: str,
) -> str:
    """moment_segments: list of (clip_path, Voiceover, rank_label) in
    countdown order (#N first, #1 last)."""
    resolution = tuple(cfg["video"]["resolution"])
    fps = cfg["video"]["fps"]
    words_per_group = cfg["video"]["caption_words_per_group"]

    clips = [
        # Intro plays over the #N (first/weakest) clip as a backdrop, no badge.
        _segment_clip(moment_segments[0][0], intro_audio, resolution, None, words_per_group)
    ]
    for clip_path, audio, rank_label in moment_segments:
        clips.append(_segment_clip(clip_path, audio, resolution, rank_label, words_per_group))

    final = concatenate_videoclips(clips, method="compose")

    if music_path:
        music = AudioFileClip(music_path).with_effects(
            [afx.AudioLoop(duration=final.duration), afx.MultiplyVolume(0.07)]
        )
        final = final.with_audio(CompositeAudioClip([music, final.audio]))

    final.write_videofile(
        out_path, fps=fps, codec="libx264", audio_codec="aac", threads=4, preset="medium", logger=None
    )
    return out_path
