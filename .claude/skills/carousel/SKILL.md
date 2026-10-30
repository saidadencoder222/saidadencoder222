---
name: carousel
description: Build the user's Instagram carousel (4:5, 1080x1350) that SELLS Claude as their video editor: a dark, italic-accent slide deck where real video of their own clip plays inside the slides, walks through the five edit passes (transcribe, cut-out, captions, motion, sound) with behind-the-scenes explanations, ends on "Comment EDIT". Use when the user says /carousel, "carousel", "carousale" or asks for an IG carousel with video embedded.
---

# /carousel: the user's "Claude is now a full time editor" carousel

The user sells Claude's video editing service. The carousel proves it with THEIR real footage, so every tile is a real render of an actual edit pass, never a mock-up of results. Everything below is confirmed taste.

## Deliverables (always give all, plus the page)
1. `slide_01..10.mp4`: each slide as a 7 s looping video (1080x1350) for posting as video slides.
2. `carousel_reel.mp4`: all slides with 0.5 s slide-left transitions and very quiet clicks (about 65 s).
3. `slide_01..10.jpg`: stills.
4. The edited business video on its own (`after_final.mp4`, 1080x1920, sound).
5. **An Artifact page** (swipeable, each slide a looping `<video>` that plays when in view): `code/viewer.html` + `s01..10.mp4/.jpg` published with the `files` map. The user asked for "the slides with the vid embedded in it", so always publish this page, not just zips.

## Slide system (10 slides, in this order)
1 Cover "Claude is now a *full time editor*." (raw clip tile tilted left, after tile right with dashed arrow, pill "Swipe for the 5-pass method")
2 The method: struck-through "Don't ask Claude for an edit." / "Ask for *five passes*" + five rows with colored bars
3 Pass 01 Transcribe: raw clip + scrolling words.json with timestamps (REAL words) + prompt chip
4 Pass 02 Cut-out: real matte, big word behind the head over a checkerboard
5 Pass 03 Captions: real caption render + style card
6 Pass 04 Motion: three real scene clips with "SAYS 00:xx" labels
7 Pass 05 Sound: after tile + REAL waveform + click markers + measured LUFS
8 "You don't edit. You *direct.*" example note + progress bar + "Your taste is the one part it can't do for you."
9 Raw clip in, finished reel out: raw tile + after tile + animated timeline (video, cut-out, cards, captions, clicks) + real counts (words timed, frames cut out, cards, clicks, LUFS)
10 CTA: "Comment *EDIT*." "I'll send you the full outline: the five passes, the prompts and my reel style rules." Pill "Comment EDIT for the full outline". (Not "DM me": the user said the CTA is Comment EDIT.)

Slides 3-7 each carry a **BEHIND THE SCENES** box (3 short bullets with the real numbers: words timed, seconds trimmed, frames matted, click level, loudness). The user asked for the editing process to be explained behind everything.

## Look
- Dark world: bg #0b0a0e with a slowly drifting purple/peach glow, mono eyebrow with a glowing dot, big bold Inter headline with ONE italic gradient word (Crimson Pro italic, gradient #ffc9a8 > #f6b6d4 > #b9a6ff), IBM Plex Mono labels, prompt chip (peach "PROMPT" tag) at the bottom, progress bar + "NN / 10" footer. These are the user's font system; never copy the reference creator's fonts.
- Animation (`slides/enh.js`, injected before `</body>`): headline words rise + de-blur one by one, tiles/cards pop in with overshoot and float, prompt chip wipes open, behind-the-scenes bullets stagger, slow zoom, footer bar eases. Slides are driven by `window.setU(u)` and captured frame by frame, so everything is deterministic.
- Video tiles are 9:16 (never crop a portrait video into a landscape box: slide 9 had that bug).

## The edited video (the star)
`code/d3tiles.py` renders the "after": cut-out of the user over a soft dark gradient, Anton small/BIG/small hook (first ~4 s), ONE simple white lowercase Inter caption at the bottom, punch-in zooms on sentence starts, and **topic animations** (`code/illus.py`): while the user says something, they shrink to ~0.6 and a flat-vector scene about it plays above them:
- stress / struggling -> sad person, head in hands, sweat drops, "?" and video clips orbiting, desk with messy timeline
- results -> bar chart climbing, counter to the number the user SAID (2.2M), small happy person
- plan -> calendar, Saturday lit, five video cards drop in, rank badges 1-5
- quality -> stairs with a figure climbing
- changes/improvements -> v1 > v2 > v3 cards
- metrics -> spreadsheet, weak "hook" row flagged by a magnifier, then fixed
Write new scenes for new topics in `illus.py` (same palette, `SCENES` list of `(t0, t1, fn, person_scale, y0)`; person scale eases in/out). The user asked for "an animation of a person sad etc." for what they talk about, so match scenes to the SENTENCE.
- NO light particles, NO swooshes/risers. Audio: voice at about -14 LUFS + very soft clicks (`code/d3audio.py`), no music.

## Workflow
1. Get the user's video (Drive: `curl -L "https://drive.google.com/uc?export=download&id=<ID>"`). If they only describe it ("the business owner video"), search the earlier transcript (`/root/.claude/projects/.../*.jsonl`) for the Drive id and words; confirm by transcribing.
2. Run the greenscreen toolkit prep: `video-toolkit/greenscreen/code/prep_cut.py raw.mp4 <vid> work` (words + pause-tightened cut json), build `clip<vid>.mkv` from `fa<vid>.txt`, frames `fd<vid>/%04d.jpg`, matte with `rvm<vid>.py`, build the alpha cache once (`mscenes.alpha_arr`). `code/redo30.sh` is the whole sequence. VERIFY frames afterward (`find fd -size -20k`): a full disk silently corrupts frames.
3. Plan CARDS/SCENES from the words; render tiles `cut`, `caps`, `motion3`, and the full edit in **4 parallel chunks** (`d3tiles.py fullc 0..3`, then concat + mux `mix.wav`). Do NOT run duplicate renders of the same output; memory/CPU contention made renders 5x slower.
4. Audio `d3audio.py` -> mix.wav, wave.json (peaks + click times), words_raw.json (words in RAW time for the transcript tile).
5. Edit the slide HTML in `slides/` (swap text, numbers, tiles; keep BTS facts true), capture with `cap.py <slide numbers>` (Playwright, Chromium at `/opt/pw-browsers/chromium`, `--no-sandbox`; tile videos must be VP9 .webm, plain Chromium has no H.264). Check a still sheet (`still.py <u> <slides>`) before the full capture.
6. Concat reel with xfade, zip, upload (gofile), downscale slide mp4s to 864x1080 for the page, publish the viewer.

## Rules
- Only real renders and real numbers in tiles. Illustrative things (example note on slide 8, comment box) are labelled as examples.
- Preserve the user's words; tell them every caption word you changed or guessed (ASR misses like "number three").
- Tell them what you could not verify; do not claim the edit was watched end to end unless it was.
- Disk is tight (about 1.5 GB free at times): delete old work dirs, never the user's raw file; keep memory in mind.

## Where things are
`video-toolkit/carousel/` : `code/` (d3tiles.py = edit renderer, illus.py = topic animations, d3audio.py, cap.py, still.py, shot.py, redo30.sh, viewer.html), `slides/` (the 10 animated slide pages + enh.js), `static-slides/` (the first still version). Paths inside scripts point at an old scratchpad (`/tmp/claude-0/...`): update them. Needs `video-toolkit/greenscreen/` for prep_cut, rvm, mscenes, mst, cscenes, fonts.
