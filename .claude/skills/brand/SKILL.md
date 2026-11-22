---
name: brand
description: The user's permanent visual identity for talking-head shorts (9:16), copied from the inspo reel "Grow to 50,000 using copywriting secrets": neon-yellow condensed-serif hero title, white tight bold-grotesk captions that switch to a white pill when an image is on screen, acid-yellow key words, serif-italic accents, unframed vintage/real images collaged around the speaker, real room kept, warm clean grade. Also the rules for cutting raw takes into complete, smooth stories. Use when the user says /brand, "my brand style", "the inspo style", or asks to edit raw takes into a short with that look.
---

# /brand: the user's visual representative

Confirmed taste. The user said: "from now on this is my visual style: that font, that colour scheme, everything. Copy the inspo to a T." Do not re-ask, do not drift. Reference: the "Grow to 50,000" copywriting reel (720x1280, 57 s). Everything below was measured from it.

## Palette and type (exact)
- **Acid yellow RGB (242,244,16) = #F2F410** for the hero title, hero words and highlighted caption words. White for everything else. Soft red/pink glow only behind the small caps sub-title. No other colours in the type system.
- **Hero / title face: condensed high-contrast serif** (Instrument Serif Regular, squashed horizontally to 0.78-0.8 so it reads like the inspo's tall condensed serif). Title = one line, about 80% of the frame width, yellow with a neon glow (blur 14 + blur 5 additive, white-hot core).
- **Sub-title**: Inter 600 caps, letter-spacing +9%, white with a faint red glow, directly under the title (about 82 px below the title baseline). It SPEAKS the hook: the title and sub must match the words he says, and change when he moves to the next clause.
- **Captions**: Inter 700, tracking -3%, about 64 px at 1080 wide (shrinks to fit 940 px), white with a soft shadow. 1-4 word chunks, original sentence case and punctuation, instant cut (no animation).
  - No image on screen: plain white, key words acid yellow (the topic words only).
  - Image on screen: WHITE PILL (white rectangle, tiny radius, about 0.26 x font-size padding) with BLACK text. No yellow inside a pill.
- **Typographic stack (hero caption)** at the start of each point, replaces the caption: line 1 hero word in yellow condensed serif (about 140 px, centred, fades in over .25 s); line 2 the spoken phrase in white Inter 700 (about 56 px, centred); line 3 serif ITALIC accent in white (about 70 px, right-aligned around x=800, never past x=1040). Stack sits in the headroom above the head (y about 170/260/340).
- Everything appears with an instant cut. The only fade in the whole system is the stack (.25 s). No bounce, no slide, no swoosh, no scale pop.

## Frame and images
- **Real room, untouched.** The speaker is scaled to 0.9 anchored bottom-centre so there is headroom (the inspo has the speaker low in frame): side slivers continue the wall (edge replicate, softened), the top continues the wall tone. No blur plates, no cut-outs unless asked.
- **Images are unframed**: no border, tiny soft shadow, rotated -4..+4 degrees, cut in instantly. Source types in the inspo: vintage print ads, paper quote cards, book covers, marketplace/screenshot cards, diagrams, stock photos, full-screen B-roll with pill captions.
- Placement: one large image in the headroom (about 520-640 px wide, centre y about 250) OR a collage around the head (hook: three pieces beside/under the face, about 230 px wide, x about 120 / 960 / 940, y about 800 / 770 / 1070). Face never covered.
- The HOOK always has the title + a 3-image collage + pill captions. Pick images that are the topic's own culture (philosophy -> classical oil paintings, Pavlov -> the real lab photos, etc.), high resolution, public domain or CC; credit them in the reply, never on screen.
- Images must be relevant to the exact words on screen. The user rejected random stock ("they don't add to the video").

## Grade
`brand.grade_brand`: warm natural grade (grade51.warm_grade), soft highlight bloom, +3% warmth, gamma .94 (skin and room a touch brighter), 10% vignette. Background stays the real room; the user wants it to look "nice, warm, high quality".

## Cutting raw takes (the user's rules, strict)
1. Raw files have many retakes, restarts, pauses, shouting. Pick the LAST COMPLETE take of each point. Never keep a bad take, never keep a stutter.
2. Every point must be a COMPLETE thought that flows into the next. If a take trails off ("...allow you to"), cut that bit out. Do not edit pieces that stop making sense.
3. Cut by word timings, not by loudness: remove every gap over about 0.2 s; keep air of 0.13 s between pieces. Check the final clip by RE-TRANSCRIBING it (clipped last syllables like "plannin-" and stray "and" fragments show up there), and compare to your intended text.
4. Splicing mid-sentence is fine if the join sounds natural ("said that the | worst sin is...").
5. Target 25-40 s. Fix ASR slips in the captions (generally -> journaling, paragraph's -> Pavlov's, Osteovoski -> Dostoevsky) and TELL the user.
6. A list video ("10 out of 10 habits, they get more niche") keeps its countdown order; the hook states the premise exactly as spoken.

## Audio
Voice only (the inspo has no sound effects): `highpass 70, acompressor -30dB 3.5:1, gain to -14 LUFS, alimiter`. Final encode `alimiter=limit=0.8` so the AAC peak stays below 0 dBFS. File size under 25 MB (two-pass x264 for 23 MB).

## Workflow
1. Download Drive files (`drive.usercontent.google.com/download?id=...&confirm=t` for big files), transcribe with faster-whisper word timestamps, contact-sheet.
2. Choose takes, build `selcut.py` ranges (or `mkcut.py`), re-transcribe the clip, fix word list, `tighten.py` for residual gaps.
3. Copy `video-toolkit/brand/code/m80.py`, edit the PLAN block (windows are found from the spoken words with `idx()` so text always lines up), fetch images (Wikimedia Commons `titles=` API for exact public-domain artworks is fastest; searches are rate limited, space calls 6-8 s).
4. Preview frames, render with `render3.py` (4 processes), encode, check loudness, upload, report credits, ASR fixes and anything unverified.

## Where the code lives
`video-toolkit/brand/code/` (brand.py = the style, m80.py / m82.py = two finished edits, mkcut/selcut/tighten = cutting, gi9.py = image fetch), fonts in `video-toolkit/brand/assets/`.
