"""Assembles the final MP4 from a fixed-cadence scene timeline (see
scene_timeline.py): a new scene roughly every `video.scene_seconds`
seconds, mixing real archival video clips (Internet Archive) and Ken Burns
zooms over Wikimedia Commons stills, with burned-in captions synced to
word timing and the narration audio (+ optional background music).

Captions are rendered as transparent PNGs with Pillow rather than
moviepy's TextClip, so the pipeline doesn't need ImageMagick installed.
Written against moviepy 2.x (`with_*` methods, `Effect` objects for
looping/volume, no `moviepy.editor`).
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

from .scene_timeline import TimelineEntry
from .voiceover import Voiceover

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


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


def _fit_clip(clip, resolution: tuple[int, int]):
    clip = clip.resized(height=resolution[1])
    if clip.w < resolution[0]:
        clip = clip.resized(width=resolution[0])
    return clip.cropped(
        x_center=clip.w / 2, y_center=clip.h / 2, width=resolution[0], height=resolution[1]
    )


def _image_scene_clip(path: str, duration: float, resolution: tuple[int, int], zoom_in: bool, zoom_range: float, oversize: float):
    img = Image.open(path).convert("RGB")
    target_w, target_h = int(resolution[0] * oversize), int(resolution[1] * oversize)
    scale = max(target_w / img.width, target_h / img.height)
    img = img.resize((max(int(img.width * scale), 1), max(int(img.height * scale), 1)))

    start_scale, end_scale = (1.0, 1.0 + zoom_range) if zoom_in else (1.0 + zoom_range, 1.0)
    clip = ImageClip(np.array(img)).with_duration(duration)
    clip = clip.resized(lambda t: start_scale + (end_scale - start_scale) * (t / max(duration, 0.01)))
    return clip.with_position("center")


def _video_scene_clip(path: str, duration: float, resolution: tuple[int, int]):
    base = VideoFileClip(path).without_audio()
    if base.duration < duration:
        base = base.with_effects([vfx.Loop(duration=duration)])
    else:
        start = max((base.duration - duration) / 2, 0)
        base = base.subclipped(start, start + duration)
    return _fit_clip(base, resolution)


def build_video(
    cfg: dict,
    voiceover: Voiceover,
    timeline: list[TimelineEntry],
    music_path: str | None,
    out_path: str,
) -> str:
    resolution = tuple(cfg["video"]["resolution"])
    fps = cfg["video"]["fps"]
    zoom_range = cfg["video"]["ken_burns_zoom_range"]
    oversize = cfg["video"]["image_oversize_factor"]

    scene_clips = []
    for entry in timeline:
        if entry.scene.kind == "video":
            clip = _video_scene_clip(entry.scene.path, entry.duration_s, resolution)
        else:
            clip = _image_scene_clip(
                entry.scene.path, entry.duration_s, resolution, entry.zoom_in, zoom_range, oversize
            )
        scene_clips.append(clip)

    base = concatenate_videoclips(scene_clips, method="compose")
    total_duration = base.duration

    caption_clips = []
    for text, start, duration in _caption_groups(voiceover, cfg["video"]["caption_words_per_group"]):
        img = _caption_image(text, resolution[0])
        clip = (
            ImageClip(np.array(img))
            .with_start(start)
            .with_duration(duration)
            .with_position(("center", resolution[1] - 260))
        )
        caption_clips.append(clip)

    audio = AudioFileClip(voiceover.audio_path)
    final_audio = audio
    if music_path:
        music = AudioFileClip(music_path).with_effects(
            [afx.AudioLoop(duration=total_duration), afx.MultiplyVolume(0.08)]
        )
        final_audio = CompositeAudioClip([music, audio])

    video = CompositeVideoClip([base, *caption_clips], size=resolution).with_duration(total_duration)
    video = video.with_audio(final_audio)
    video.write_videofile(
        out_path, fps=fps, codec="libx264", audio_codec="aac", threads=4, preset="medium", logger=None
    )
    return out_path
