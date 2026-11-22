---
name: storyboard
description: The user's editing SYSTEM. Run this first for every new video: read the inspiration index, transcribe, build an interactive forest-green storyboard artifact (line by line, with the real clip), let the user change anything, read their changes back from the artifact database, then edit. Use when the user sends a video and says what they want, says /storyboard, "storyboard", "plan the edit", or starts any new edit.
---

# /storyboard: plan with the user before any editing

The user found the old way inefficient (edit, show, get feedback, redo). New order, always:

1. **Receive** the video(s) and the brief. Download (Drive: `drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t` for big files), probe, transcribe with word timestamps (faster-whisper `small.en`, `beam_size=8`, `condition_on_previous_text=False`).
2. **Read the inspiration library**: `inspiration/INDEX.md` and `inspiration/inspiration.json`. Pick the matching style (`/brand` is the default look; `/overlay`, `/greenscreen`, `/carousel` for those formats), open its thumbnails, and note what to copy. New inspo from the user goes into the index first (add to the json, save contact sheets to `inspiration/thumbs/`, add a `copy` line, update the skill).
3. **Clean the story**: choose the last complete take of each point, drop retakes, stumbles and unfinished thoughts (see /brand cutting rules), build the cut and re-transcribe it to check for stutters. Make a 360x640 proxy clip of the cut.
4. **Build the storyboard artifact** from `video-toolkit/storyboard/page.html` (forest green, publishes with `db` capability and `clip.mp4`): one beat per spoken line with start/end, caption text, visual type (hook title / accent words / image card / caption only / graphic), big word + small lines, glow, images (thumbnails with labels), sound, graphic, note. Seed the beats with your own plan through `ArtifactData` batch (`project/main` + `beats/bNN`; see `example_beats.json`). Fill every field with a real proposal copied from the inspo, with a short reason in the note.
5. **Give the user the link and wait.** They scrub the real video, edit any field, cut lines, trim start/end, write notes and press Approve.
6. **Read it back** (also `list` the `suggestions` collection: the user's own free-text edits, each with `kind`, optional timecode `t`, `done`; treat every undone one as an instruction, do it, then set `done:true` with `update`) with `ArtifactData` (`list` on `beats`, `get` on `project/main`): `status` must be `approved` (else ask); treat every field as the instruction; honour `keep:false` (cut), `t0/t1` (new trims), caption text, `img` ids, `sfx`, notes. Anything ambiguous: ask once, then proceed.
7. **Edit** with the style engine (`video-toolkit/brand/code/`). Translate beats to the plan blocks in `m80.py/m82.py` (ACCENTS, IMGS, TITLE/SUBS), render, QC frames + loudness, upload, report.
8. Update the storyboard after the render if the user asks for changes, then re-render only what changed.

## House rules learned (do not relearn)
- Title hooks sit ABOVE the head, appear instantly: no fade, no animation. Images are hard cuts, no fades, no sound effects on images, big (800 px wide in the headroom, 340 px x3 in the hook row at the bottom), relevant to the words, and never reused between two videos the user will post together.
- Captions small and under the chin, varied position, no white box; key words yellow.
- Read `audio-library/README.md` for music/SFX; the user's Interstellar piano is the default bed.
- Keep the user's words; fix and report ASR slips; remove stumbles you find by re-transcribing the cut.
