# VSL Script Generator

Turns a creator's raw brain-dump about a client win into a structured,
production-ready 15-minute VSL script.

## Inputs
- `raw_ideas.txt` — a loose transcript/brain-dump describing a specific
  client win (place it at the workspace root or inside the relevant
  `clients/<creator-name>/` folder).
- Context files inside `core-brain/` (`creator-dna.md`, `offer-framework.md`)
  for voice, offer, and qualification details.

## Terminal Prompt

```
claude "Read the context files inside core-brain/. Take a raw transcript file
from raw_ideas.txt (which contains a creator's loose brain dump about a
specific client win) and output a complete, production-ready 15-minute VSL
Script structured using this exact high-ticket framework:
1. The Pattern Interrupt Hook (0-60 seconds: Call out the exact target
   audience and current frustration).
2. The Core Mechanism Reveal (Introduce the systemized asset, not the
   delivery mechanism).
3. The Case Study Proof (Deconstruct the numbers, timeline, and exact steps
   of the client win).
4. The Frictionless Call To Action (Tell them exactly why an application is
   required and who should NOT apply).
Output the file directly to scripts/optimized_vsl_output.md with clear
visual/delivery cues for the creator."
```

## Output

`scripts/optimized_vsl_output.md` — the generated script, with delivery/visual
cues (b-roll, on-screen text, pacing notes) inline so it's ready to hand to an
editor.
