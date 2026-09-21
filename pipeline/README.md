# Creator content pipeline

A repeatable, credit-budgeted workflow that:

1. Searches TikTok + Instagram Reels for outlier videos in your niche
   ("helping creators monetize their audiences").
2. Watches the top ones and extracts *why the hook works*, clustering them into
   reusable hook styles (pattern-interrupt question, bold claim + number, POV text
   overlay, etc.).
3. Turns each hook style into a fresh, ready-to-film script for your content —
   adapted structure, never copied content.
4. Leaves publishing as a separate, explicit step (Instagram Reels can be
   automated once connected; TikTok/YouTube Shorts are manual — see
   `CROSS_POST_GUIDE.md`).

## How to run it

In any future Claude Code session on this repo, type:

```
/creator-pipeline
```

Each run reads `pipeline/state/*.json`, does one budgeted chunk of work, writes
results back, and stops. Nothing is repeated — a video already discovered, a hook
already analyzed, or a style already turned into an idea is skipped automatically.

## Why it's budgeted

Your vidIQ balance right now: **30 credits**, renewing 2026-09-30. This pipeline
uses real credits:

| Stage | Cost |
|---|---|
| Outlier search (one query, both platforms) | 5 credits |
| Watch + analyze one short-form video | 10 credits |
| Generate one script idea (~1 min length) | ~1 credit |
| Score/generate titles | 5 credits |

`pipeline/config.json` caps every run at `creditBudget.maxPerRun` (default 15) and
keeps a `reserveFloor` (default 5) untouched. That's roughly 2 runs before your
current balance resets — edit those numbers in `config.json` any time.

## Files

- `config.json` — niche, audience targeting, seed search queries, credit caps.
- `state/outliers.json` — every outlier video found, with hook analysis once done.
- `state/hooks.json` — the hook styles that have emerged, with example videos.
- `state/ideas.json` — generated scripts, one per hook style tried.
- `ideas/*.md` — human-readable script + caption drafts, ready to film from.
- `log.md` — a line per run: what happened, what it cost.
- `CROSS_POST_GUIDE.md` — what's automated vs. manual across TikTok/IG/YouTube.

## Next step

Nothing has spent any credits yet. When you're ready, just run `/creator-pipeline`
and the first cycle will do one outlier search + as much hook analysis as 15
credits covers.
