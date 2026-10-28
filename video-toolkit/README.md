# Video toolkit

Python/ffmpeg pipeline for vertical (1080x1920) short-form video: cut pauses from talking-head footage, matte the speaker (Robust Video Matting) so text can sit behind them, build word-synced graphics, synthesize a quiet music/SFX bed, render and QC.

## Setup
```
./setup.sh        # installs deps, fetches the RVM model, links this folder to /tmp/vt
```
Needs `ffmpeg`. No media is stored in the repo; footage goes in each engine's `raw/` or `work/` folder (git-ignored).

## Layout
| Folder | What it is |
|---|---|
| `c1/` | talking-head reels: pause cutting (`cut.py`), doodle overlays (`doodle.py`, `cc3.py`), per-video scripts (`vids3.py`) |
| `c2/` | documentary compositor (`doc.py` - typography, glitch, burn, matte helpers), audio mix (`audio2.py`), RVM matting (`rvm.py`), asset fetch (`getassets.py`) |
| `c3/` | text-only Trial Reels engine (`rl.py` + 30 specs in `reels.py`, `runall.py` renders them in parallel) |
| `c4/` | film-ranking (`film2.py`, `audio5.py`) and creator-audit (`alex.py`, `audioA.py`) engines + `render*.py` |
| `batch2/` | `eng/fetch.py` (licence-checked Wikimedia Commons image fetch), `upload.sh` (gofile link) |

## Typical run (talking-head video)
1. Transcribe with faster-whisper (word timestamps), build keep-intervals, concat the cut clip (see top of any `c4` session notes / `cut` snippets in `c4/alex.py` docs).
2. `python3 c4/rvmA.py` style matte (`rvm4.py` is the generic version: edit input/output paths).
3. Edit the scene functions (`behind()` for text behind the speaker, `front()` for UI) in a copy of `c4/alex.py` or `c4/film2.py`.
4. Audio: copy `c4/audioA.py`, adjust the SFX times.
5. Render: copy `c4/renderA.py` (4 parallel chunks -> ffmpeg concat -> mux).
6. QC with contact sheets, then `batch2/upload.sh out/video.mp4`.

See `CLAUDE.md` for the rules this pipeline follows.
