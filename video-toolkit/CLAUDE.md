# Working rules for video requests (read first)

Workflow when the user sends a concept: read `concept_template.md` fields -> download footage (Drive links work via `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`) -> **check the audio has real speech before anything else** (`ffmpeg -af volumedetect`; silent files can't be transcribed or edited to the dialogue) -> transcribe -> cut -> matte -> build -> mix -> render -> QC frames -> upload -> reply with link + honest limits.

## Hard rules
- Never invent results, quotes, client data, follower counts, endorsements or screenshots. Label illustrative graphics ("EXAMPLE", "ILLUSTRATIVE"). Only show numbers that come from supplied screenshots or the user's own words (and mark those as their claims).
- Keep the user's actual words; fix only clear ASR errors and flag them in the reply.
- Never claim an edit/export happened if it didn't. State what could not be done (e.g. real film stills are low-res fair-use files; Impact isn't installed so Anton is the stand-in).
- Third-party footage/reference reels are excluded unless the user supplies them for that edit.
- Use free-licence images (check licence via `batch2/eng/fetch.py`); credit them in a CREDITS file.

## Quality targets
- 1080x1920, 30fps, H.264 CRF ~15, AAC 192k; final ~-14 LUFS, peak <= -1.5 dBFS ideally.
- Music about -30 dBFS under speech (voice ~-16), ducked by the voice envelope; SFX peaks <= -16 dBFS; one deliberate silence before a major reveal; no SFX on every caption.
- Text behind the speaker only via the RVM matte; keep faces uncovered; captions in the 1400-1650px band, mobile-safe margins.
- Always review contact sheets of the rendered file (hook frame, each scene, end card) before delivering.

## User style preferences learned
- Talking-head reels: plain TikTok-style captions, Poppins, small, no shadow, subtle zooms, hand-drawn doodle overlays, speaker on screen >= 20s, no on-screen text hook unless asked.
- Cinematic briefs: Impact/Anton for emphasis, Bebas for titles, Poppins support; restrained black/charcoal/white + one accent; burn-in text effect used sparingly; word-synced reveals.
- No CapCut/DaVinci project linking is possible from the cloud sandbox; deliver rendered MP4s + source scripts.
