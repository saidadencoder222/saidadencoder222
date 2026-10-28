---
name: greenscreen
description: Build the user's green-screen movie-commentary short (9:16): their cut-out sits small in the middle of a 2x2 grid of four images that change with every idea, an Anton title in the first seconds, ONE simple white Inter caption at the bottom, voice at -14 LUFS, quiet ambient bed, clicks instead of swooshes. Use when the user says /greenscreen or asks for a "green screen" / "4 images behind me" edit.
---

# /greenscreen: the user's green-screen commentary edit

Everything below is the user's confirmed taste. Do not re-ask it, do not drift from it.

## The look (non-negotiable)
- **Layout:** 1080x1920. A 2x2 grid of full-bleed images (each cell 540x960, thin black gutters). The user is cut out with the RVM matte and shown SMALL in the centre (scale about 0.56-0.62, head near y=840). The cut-out bottom fades out over about 150 px. Every beat (each new idea) swaps ALL four images, quadrant by quadrant with a short flash. Light punch-in (scale +0.07) on emphasised words.
- **Title:** same style as the "recreating a viral edit" video: **Anton**, off-white (236,236,236), soft shadow, three centred lines at the top: small / BIG / small, each rising and scaling in (1.14 to 1.0) with a stagger, faded out after the hook (about 6.5 s). Hooking wording, built from the user's own claim. No white box, no amber word, no second title.
- **Captions:** exactly ONE caption stream, the user's usual simple white one: **Inter 600, lowercase, white, soft shadow, 1-4 word chunks**, bottom of the frame (y about 1600, size 58), never over the face. NO keyword highlighting, NO extra text overlays, NO lists, NO labels, NO chapter tags, NO credits on screen.
- **One font family system** across all the user's videos: Anton (titles), Inter (captions), IBM Plex Mono (tiny labels only if a video needs them), Crimson (serif annotations). Never copy a reference creator's fonts or layout styling; never use a boxed title.
- **Colour:** white-balance the warm tungsten cast toward neutral (keep about 28% warmth), light contrast, desaturate the shirt about 14%, every grid cell run through one shared grade (`unify`: 18% desaturation, slight lift, vignette) so the four images read as one set. NO film grain.

## Images (the user was strict)
- HD only (cells are 540x960, so source short side >= about 1000 px; NASA/Wikimedia originals are 1900-3200 px). No low-res thumbnails, no diagrams, no charts, no labelled science graphics, no screenshots with text.
- NOT just space. Mix, per idea, what is actually being said: the user's own supplied stills, real photos (people, family, light, film sets), real HD space/Earth photos, moving NASA footage in some cells, and original graphics drawn in code (e.g. glowing brain network for psychology, rising bars for content improvement).
- **Hook cells are fixed in meaning:** (1) the actor/subject, (2) the key iconic visual (e.g. black hole), (3) a psychology image, (4) content improvement. Later beats vary and must reflect the sentence.
- User-supplied film stills are small: show them at native width over a blurred, darkened copy of themselves (`still_cell`, names starting `u`); the tall one covers. Never stretch a small still to fill a cell.
- Moving footage: NASA Image Library videos are public domain (`images-api.nasa.gov`, media_type=video, take `~medium.mp4`). Inspect frames first: reject clips with people, captions or flashes.
- Never use footage lifted from the film itself unless the user supplies it. Do not invent scenes, quotes or facts; label artist's concepts honestly in the reply.
- Licensing: prefer public domain (NASA, US Army, Highsmith, Met Open Access, Internet Archive). CC BY / BY-SA allowed with credit given in the REPLY (not on screen). Wikimedia and LoC rate-limit this server: run fetches in the background, one query at a time, and fall back to NASA.

## Audio
- Voice: highpass 90, afftdn, light gate, compressor, loudnorm to -14 LUFS (user clips are often -33 LUFS).
- Music: ONE quiet licensed ambient bed (Kevin MacLeod, incompetech: "Floating Cities" worked; CC BY 3.0, credit in reply), about **38 dB under the voice**, ducked while speaking, a near-silent dip right before the single most important sentence, swelling slightly through the video.
- SFX: **no swooshes, no risers, no impacts, no bass hits.** Only soft dry **clicks** (two on each image swap, one tiny tick on an emphasised word), peaking at about **a fifth of the voice**. Quieter is always the safe direction: the user has complained about loud and tacky audio three times.
- If asked for "no background audio": voice only, no music, no clicks.

## Content rules
- Preserve the user's words. Cut only retakes, dead air and pauses over 0.3 s (never shorten inside words). Fix ASR errors in the captions (e.g. "brother's" -> "father's") and TELL the user which words you changed.
- Do not add claims, stats or testimonials. Illustrative graphics are labelled in the reply, never presented as real data.
- Do not add a generic "like and follow" end if the user's own words don't contain one (keep theirs).

## Workflow
1. Get the video: Drive links work with `curl -L "https://drive.google.com/uc?export=download&id=<ID>"`. Probe it, transcribe (faster-whisper small.en).
2. `python3 video-toolkit/greenscreen/code/prep_cut.py raw.mp4 <vid> <work>` -> cut json, filter, clip, frames. Review and fix the printed word list. Copy `rvm17.py` to `rvm<vid>.py` (change clip/alpha ids), run it for the alpha matte (RVM onnx, 540x960). Build the alpha cache ONCE in a single process (`mscenes.alpha_arr(<vid>)`) before rendering with 4 processes, or the processes corrupt the .npy.
3. Plan beats from the sentences (about 7-8 beats, 3-8 s each), pick four images per beat that reflect the sentence; pick `PUNCH` times on the emphasised words.
4. Copy `code/m18.py` to `m<vid>.py`; edit BEATS, HOOK title lines, PUNCH. `S3.setup(<vid>)` etc. Preview with `m<vid>.preview([...times], out.jpg)` and look at the frames (title not over the face, nothing cut off, no stray text, no flashes).
5. Audio: adapt `audioD.py` (beat list from the module, dip time, music offset). Render: `python3 render3.py m<vid> work/mix<vid>.wav out.mp4` (4 processes, about 8-10 min). Check loudness (about -14 LUFS), inspect a frame sheet, upload, and report credits plus anything you changed or could not verify.
6. The silent render is `work/sil_m<vid>.mp4`: audio-only changes are a re-mux (`ffmpeg -i sil -i mix -map 0:v -map 1:a -c:v copy`), no re-render.

## Gotchas learned the hard way
- `pkill -f <name>` kills your own shell if the name appears in the command line: use `ps aux | grep ... | awk '{print $2}' | xargs kill` in a separate command.
- Disk is limited: do not leave multi-GB frame folders around, and never delete a user's raw source before the job is done (keep `raw.mp4`).
- Python tools: OpenCV wants int pixel coords; broadcast gradients to (h,w,3) before drawing text on them.
- Scientific videos often have burned-in captions: always check frames.

## Where the code lives
`video-toolkit/greenscreen/code/` (m18.py = layout + beats, cscenes.py = matte compositing, mst.py/mscenes.py/mrun.py = engine, audioD.py = clicks-only mix, prep_cut.py, rvm17.py, hands15.py, nasa*.py / wm.py = image fetchers) and `video-toolkit/greenscreen/fonts/`. Paths inside the scripts point at the old scratchpad (`SC=...`): update them to the new session's scratchpad before running.
