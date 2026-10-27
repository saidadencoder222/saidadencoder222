# Command system

Give a command + input. Styles combine: `FIRST + SECOND` (first = structure, second = visual treatment).

| Command | Structure | Format file |
|---|---|---|
| RANKING | countdown, one reveal per item, name + number + visuals | formats/RANKING.md |
| STORYTELLING | hook > context > development > conflict > turn > resolution > takeaway | formats/STORYTELLING.md |
| DOCUMENTARY | researched claims, real photos/docs, dates, labels | formats/DOCUMENTARY.md |
| BUSINESS | hook, evidence on screen, toggle/checklist lists, CTA | formats/BUSINESS.md |
| CHARACTER | character-centred reveal, traits as labels | formats/CHARACTER.md |
| FILM | title, stills, scene selections | formats/FILM.md |
| EDUCATIONAL | staged diagrams in understanding order | formats/EDUCATIONAL.md |
| CINEMATIC | atmosphere, slow movement, big breathing statements | formats/CINEMATIC.md |
| COMMENTARY | argument with evidence introduced when relevant | formats/COMMENTARY.md |
| EXPERIMENTAL | purposeful unusual layouts | formats/EXPERIMENTAL.md |

Workflow per video (see `../CLAUDE.md`): 1) check audio is real speech 2) transcribe (faster-whisper, word times) 3) cut: remove retakes, stutters, dead air, non-speech tails (`c5/cutbuild.py`) 4) shot plan 5) build with `c5/` engine 6) audio: real licensed track ~-33 dB under voice + natural SFX 7) render 1080x1920 8) QC frames + loudness 9) log feedback in changelog.
Input rules: video + command -> derive the structure from its content; script + command -> build to the script; topic only -> research, propose concept; ask only essential questions.
