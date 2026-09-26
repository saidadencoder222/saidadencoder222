# Short-form viral-style editor

Takes your own raw footage and re-cuts it using editing conventions common
across high-retention short-form creators: automatic jump-cuts on dead
air, burned-in phrase captions synced to your actual speech, and a light
continuous zoom-in for energy.

This is a **style/format** tool — it doesn't reuse, download, or reference
any other creator's actual video. Point it at your own footage.

## Setup

```
pip install -r requirements.txt
sudo apt install ffmpeg fonts-dejavu-core   # if you don't already have these
```

First run downloads a small Whisper speech-recognition model (~150MB for
`base.en`), cached afterward.

## Usage

```
python edit_for_virality.py input.mp4 output.mp4
```

Options:
```
--words-per-caption 4     # bigger chunks = fewer, longer captions (default 3)
--no-jumpcuts              # keep your original pacing, just add captions/zoom
--no-zoom                  # skip the continuous zoom-in effect
--whisper-model small.en   # tiny.en (fastest) / base.en (default) / small.en (more accurate)
```

## What it actually does

1. Transcribes your audio with word-level timestamps (faster-whisper,
   runs locally, no API key).
2. Finds gaps between words longer than 0.45s (dead air, "umm" pauses,
   thinking gaps) and compresses them down to 0.12s — the jump-cut effect
   that keeps pacing tight.
3. Renders bold, high-contrast captions in chunks of a few words, timed
   to when you actually said them, positioned lower-third.
4. Applies a slow continuous zoom-in across each kept segment for a bit
   of visual energy instead of a static shot.

## Tuning it

- Talking fast with few natural pauses? `--no-jumpcuts` to avoid choppy cuts.
- Want the classic word-by-word pop-in caption style instead of phrase
  chunks? Set `--words-per-caption 1`.
- Silence threshold/keep duration, caption size/position, and zoom rate
  are constants at the top of `edit_for_virality.py` — tweak directly if
  the defaults don't match your style.
