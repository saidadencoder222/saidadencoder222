"""Edits your own raw short-form footage into a punchier cut using the
editing conventions common across high-retention creators: automatic
jump-cuts on dead air, burned-in phrase captions synced to speech, and a
light continuous zoom-in for energy. Works on whatever footage you give
it — this is a style/format tool, not a way to reuse anyone else's video.

Usage:
    python edit_for_virality.py input.mp4 output.mp4
    python edit_for_virality.py input.mp4 output.mp4 --words-per-caption 4 --no-jumpcuts
"""
import argparse
from dataclasses import dataclass

import numpy as np
from moviepy import CompositeVideoClip, ImageClip, VideoFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SILENCE_GAP_THRESHOLD = 0.45   # gaps longer than this get compressed into a jump cut
SILENCE_GAP_KEEP = 0.12        # how much of a long gap survives, so cuts don't feel jarring
ZOOM_PER_SEGMENT = 0.035       # subtle continuous zoom-in over each kept segment


@dataclass
class Word:
    text: str
    start: float
    end: float


def transcribe(path: str, model_size: str = "base.en") -> list[Word]:
    from faster_whisper import WhisperModel  # heavy optional dep, only needed here

    print(f"[transcribe] loading whisper model '{model_size}' (downloads once, then cached)...")
    model = WhisperModel(model_size, compute_type="int8")
    segments, _ = model.transcribe(path, word_timestamps=True)
    words: list[Word] = []
    for seg in segments:
        for w in seg.words:
            text = w.word.strip()
            if text:
                words.append(Word(text=text, start=w.start, end=w.end))
    print(f"[transcribe] {len(words)} words")
    return words


def build_keep_segments(words: list[Word], total_duration: float, jumpcuts: bool) -> list[tuple[float, float]]:
    """Returns contiguous (orig_start, orig_end) ranges to keep from the
    ORIGINAL timeline. When jumpcuts is True, gaps between words longer
    than SILENCE_GAP_THRESHOLD are compressed down to SILENCE_GAP_KEEP."""
    if not words:
        return [(0.0, total_duration)]

    raw: list[tuple[float, float]] = []
    cursor = 0.0
    for w in words:
        gap = w.start - cursor
        if jumpcuts and gap > SILENCE_GAP_THRESHOLD:
            raw.append((max(w.start - SILENCE_GAP_KEEP, cursor), w.start))
        else:
            raw.append((cursor, w.start))
        raw.append((w.start, w.end))
        cursor = w.end

    trailing_gap = total_duration - cursor
    if jumpcuts and trailing_gap > SILENCE_GAP_THRESHOLD:
        raw.append((cursor, cursor + SILENCE_GAP_KEEP))
    else:
        raw.append((cursor, total_duration))

    merged: list[tuple[float, float]] = []
    for s, e in raw:
        if e <= s:
            continue
        if merged and s <= merged[-1][1] + 0.01:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def remap_time(orig_t: float, keep_segments: list[tuple[float, float]]) -> float | None:
    """Maps a timestamp on the ORIGINAL timeline to where it lands on the
    NEW (cut) timeline. Returns None if it fell inside a removed gap."""
    new_t = 0.0
    for s, e in keep_segments:
        if orig_t < s:
            return None
        if orig_t <= e:
            return new_t + (orig_t - s)
        new_t += e - s
    return None


def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def _caption_image(text: str, width: int) -> Image.Image:
    font = _font(70)
    img = Image.new("RGBA", (width, 220), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text.upper(), font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (width - tw) / 2, (220 - th) / 2
    for dx in (-4, 0, 4):
        for dy in (-4, 0, 4):
            draw.text((x + dx, y + dy), text.upper(), font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), text.upper(), font=font, fill=(255, 255, 255, 255))
    return img


def build_video(
    input_path: str,
    words: list[Word],
    keep_segments: list[tuple[float, float]],
    output_path: str,
    words_per_caption: int,
    zoom: bool,
) -> None:
    src = VideoFileClip(input_path)
    resolution = (src.w, src.h)

    clips = []
    for s, e in keep_segments:
        clip = src.subclipped(s, e)
        if zoom:
            dur = e - s
            clip = clip.resized(lambda t, d=dur: 1.0 + ZOOM_PER_SEGMENT * (t / max(d, 0.01)))
        clips.append(clip)
    base = concatenate_videoclips(clips, method="compose")

    caption_clips = []
    for i in range(0, len(words), words_per_caption):
        chunk = words[i : i + words_per_caption]
        text = " ".join(w.text for w in chunk)
        new_start = remap_time(chunk[0].start, keep_segments)
        new_end = remap_time(chunk[-1].end, keep_segments)
        if new_start is None or new_end is None:
            continue
        img = _caption_image(text, resolution[0])
        caption_clips.append(
            ImageClip(np.array(img))
            .with_start(new_start)
            .with_duration(max(new_end - new_start, 0.3))
            .with_position(("center", int(resolution[1] * 0.72)))
        )

    final = CompositeVideoClip([base, *caption_clips], size=resolution)
    final.write_videofile(output_path, fps=src.fps, codec="libx264", audio_codec="aac", preset="medium")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--words-per-caption", type=int, default=3)
    parser.add_argument("--no-jumpcuts", action="store_true", help="Keep original pacing, only add captions/zoom")
    parser.add_argument("--no-zoom", action="store_true", help="Skip the continuous zoom-in effect")
    parser.add_argument("--whisper-model", default="base.en", help="tiny.en/base.en/small.en — bigger = more accurate, slower")
    args = parser.parse_args()

    words = transcribe(args.input, args.whisper_model)
    total_duration = VideoFileClip(args.input).duration
    keep_segments = build_keep_segments(words, total_duration, jumpcuts=not args.no_jumpcuts)

    kept_duration = sum(e - s for s, e in keep_segments)
    print(f"[cuts] {len(keep_segments)} segments, {kept_duration:.1f}s of {total_duration:.1f}s kept "
          f"({total_duration - kept_duration:.1f}s of dead air trimmed)")

    build_video(args.input, words, keep_segments, args.output, args.words_per_caption, zoom=not args.no_zoom)
    print(f"[done] {args.output}")


if __name__ == "__main__":
    main()
