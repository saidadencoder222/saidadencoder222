# Universal caption engine (implemented in `../c5/cap8.py`)
Default: white, cinematic, no heavy shadow (owner: shadows look bad). Accent colour only on key words, taken from the subject (e.g. a Geometry Dash level's real palette).
Fonts installed & verified: Bebas Neue, Anton, Inter, Poppins, Instrument Serif Italic.

| # | Treatment | Implementation | Use when |
|---|---|---|---|
| 1 | Word reveal | Bebas, per word rise+scale+fade, key word accent | short punchy phrases |
| 2 | Key-word slam | Anton 1.8x->1.0 with blur, small Inter line above | the single important word |
| 3 | Tracked sentence | Inter, tracking collapses 26->2 while fading | calm explanatory lines |
| 4 | Mask wipe | Bebas phrase revealed L->R by soft mask + accent underline | 2-3 word statements |
| 5 | Stacked lines | two Bebas lines, 2nd larger/accent, own beat each | longer statements |
| 6 | Editorial serif | Instrument Serif Italic, slow fade-up + blur resolve | dramatic/open questions |
| 7 | Blur-in words | Inter bold per-word blur->sharp with drift | casual speech |
| 8 | Ghost number | giant Anton at ~16% behind clean line | numbers/rankings |
NOT yet implemented: text behind the subject (needs a fresh RVM matte per cut: `c4/rvm4.py`), perspective/tracked text, per-word motion tracking. Do not claim these without rendering them.
Assignment rules are in `cap8.assign()`: questions/"wrong/right" -> serif; numbers -> ghost; 1-word -> reveal; key word + <=3 words -> wipe; never the same treatment twice in a row.
