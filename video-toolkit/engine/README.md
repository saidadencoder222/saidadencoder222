# Video Production Engine (v0.1)

**What this is:** a modular documentation + code system, NOT an installed Claude plugin. It lives in this repo (`video-toolkit/engine/`) and works because a future session is told to read it. The rendering code is real and runs (`../c1`-`../c6`); the specs below are written from the 11 reference reels in the Drive folder "Video Examples for Claude Engine".

| Component | File |
|---|---|
| A Global engine | `GLOBAL.md` |
| B Format library | `formats/*.md` (ranking, storytelling, business, podcast, case study, explainer, top-of-funnel) |
| C Creator references | `creators/REFERENCES.md` (+ `ref_stats.json`) |
| D Asset library | `assets/INDEX.md`, `assets/assets.csv` |
| E Storyboard engine | `storyboards/TEMPLATE.md` |
| F Verification | `verification/CHECKLIST.md`, `verification/verify.py` |
| G Improvement | `changelog/CHANGELOG.md`, `changelog/FEEDBACK.md`, `changelog/PERFORMANCE.csv` |
| ICP pain points | `ICP_PAIN_POINTS.md` (**no source document found yet**) |

**Start of every session:** read `../CLAUDE.md`, `GLOBAL.md`, the chosen format file, `creators/REFERENCES.md`, `changelog/FEEDBACK.md`.
**Workflow:** idea -> pick pain point -> pick format -> storyboard -> user approves -> edit -> `verify.py` + frame review -> report -> log feedback.
