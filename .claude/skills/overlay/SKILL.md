---
name: overlay
description: Build the user's "overlay" short (9:16): their real talking-head footage full-frame (NO cut-out), white-edged image/clip cards popping in above their head on each idea, pale-yellow serif key-word pops, one small white caption, subtle zooms, clean quiet pops. Copies a viral reference's format (the BTS "masterclass in branding" video) for a topic the user chooses (e.g. Game of Thrones). Use when the user says /overlay, "overlay format", "the overlay bit", or asks to copy a viral video's format onto their own footage.
---

# /overlay: the user's viral-format overlay edit

Confirmed taste. Do not re-ask it, do not drift. Built for: the user watches a winning viral video in their niche, copies its FORMAT, and applies it to a topic they like ("masterclass in branding" about Game of Thrones / BTS).

## What the reference format is (measured from the BTS video, 720x1280)
- Speaker is FULL FRAME, natural grade, **no matte / no cut-out**. Headroom above the head holds the overlays.
- **Overlay card**: image or video clip, centred, **thin white edge** (~6 px at 1080), soft drop shadow, bottom of the card just above the head (bottom y about 512, card 700x394 landscape; portrait/shield cards about 380x410). It pops in (scale .93 to 1 and fade in about .16 s) and is replaced by the next one with a hard cut. A new card about every 2-3 s, always about the sentence being said. Only one overlay at a time.
- **Key-word pop** (no card): small white sans line / BIG pale-yellow bold serif word (RGB 248,248,185, Crimson Pro Bold) / small white line, centred in the top area, soft shadow. Used for the statement lines ("masterclass in branding", "visual identity", "the motto", "color scheme").
- **List card**: plain white card, light-blue (RGB 174,202,235) bold sans numbered lines ("1. Symbols / 2. Mottos / 3. Color scheme") when the user says "three things".
- **Caption**: ONE stream, small white Inter 600 about 46 px, ORIGINAL sentence case and punctuation, 1-4 word chunks, soft shadow, at about y 1470 (below the chin, over the torso, away from the mouth and the mic hand). No colours, no pop, no highlights.

## Look and motion (user's additions)
- **Subtle close zooms**: the footage drifts in and out around the face (ping-pong 1.0 to 1.07 across each overlay) plus a quick close-up punch (+0.05, about .5 s) on the emphasised words. The overlay cards do NOT zoom. Never constant zooming.
- Crop the thin bright band at the top edge of phone footage (crop 10 px, rescale).
- WB the footage toward neutral (keep about 28% warmth) with `bscenes.look`; set the wall colour per video with `bscenes.set_wall([b,g,r])` (sample a wall patch).

## Audio (the user asked: clean, not too loud)
- Voice only, cleaned: highpass 90, afftdn, light gate, compressor, loudnorm about -14 LUFS (peak <= -2 dBFS).
- SFX: one **soft clean pop** as each overlay lands, peaking about 1/6 of the voice, ducked under speech. No swooshes, risers, impacts, bass hits, no music unless asked. Quieter is the safe direction.

## Images and clips
- The user supplies a clip file (landscape footage stored rotated inside a 9:16 mp4): rotate with `ffmpeg -vf transpose=2` (counter-clockwise) and ALWAYS look at a frame to check. Scene-detect (`select='gt(scene,0.35)'`) and chain segments to fill each card's duration.
- Images "from Google": Bing/Google scraping returns junk for niche queries. What works: the topic's **fandom wiki MediaWiki API** (`<wiki>.fandom.com/api.php?action=query&generator=images&titles=<page>&prop=imageinfo&iiprop=url|size`), which gives 1900-4000 px stills, concept art and SVG house sigils (rasterise with cairosvg at 1600 px). Look at a contact sheet before using anything. `code/fetch_got.py` and `dl_got.py` are the Game of Thrones example (sigils for Stark/Targaryen/Lannister/Martell, Winterfell, Dorne, King's Landing, dragons).
- Match images to the words: symbols -> sigils, mottos -> sigil + the words on a house-colour card, colour scheme -> locations (cold/dark, bright/warm, red), "a dragon" -> a dragon still.
- Third-party art/screens are copyrighted: tell the user plainly, credit sources in the reply, never put credits on screen.

## Content rules
- Preserve the user's words. Cut pauses over 0.3 s only. Fix ASR errors in the captions and TELL the user each one (GoT video: "this house dark" -> "this is House Stark", "replaces death" -> "pays his debts"; the comment keyword the ASR heard as "kind" was left as heard and flagged).
- Do not invent claims. Cards that state facts (mottos, locations) must be true to the show.
- If the ending is cut off or a CTA word is unclear, say so instead of guessing.

## Workflow
1. Download all links (Drive: `curl -L "https://drive.google.com/uc?export=download&id=<ID>"`), probe, transcribe, contact-sheet each. Work out which file is the reference, the clips, and the user's raw. The user's raw is the talking-head with their voice; the reference is someone else's viral video (study it, do not reuse it).
2. `video-toolkit/greenscreen/code/prep_cut.py raw.mp4 <vid> work` for words and pause-tightened cut; rebuild the clip with `ffmpeg ... -c:v libx264 -crf 12 -preset veryfast` from `fa<vid>.txt`, extract frames `fd<vid>/%04d.jpg`, and **run `ffmpeg -v error -i clip -f null -` to prove it decodes cleanly** (a full disk or a parallel job corrupts it).
3. Fill the `EV` table in `code/m50.py`: `(first_word_index, next_event_first_word_index, kind, params)`; kinds `pop`, `clip`, `img`, `img2`, `sigil`, `trio`, `quad`, `motto`, `palette`, `list`. Overlay times come from word start times. Pick `EMPH` word indices for the close-up punches.
4. Preview several frames (`m50.preview([...], out.jpg)`), view them: cards above the head, nothing over the face, captions not on the mouth.
5. Audio: `code/audioG50.py` (voice + soft pops). Render `python3 render3.py m50 work/mix.wav out.mp4` (4 processes), check loudness, view a frame sheet, upload, report: the ASR fixes, image sources and credits, anything unverified.

## Where the code lives
`video-toolkit/overlay/code/` (m50.py = the format, audioG50.py = mix, fetch_got.py / dl_got.py = wiki asset fetchers). The shared engine is `video-toolkit/greenscreen/code/` (`simple.py` and `bscenes.py` were recreated in session 4 because the originals were lost; `render3.py`, `prep_cut.py`, mst/mscenes). Script paths point at an old scratchpad (`SC=...`): update them for the new session. Needs ffmpeg, numpy, opencv, scipy, pillow, faster-whisper, cairosvg.
