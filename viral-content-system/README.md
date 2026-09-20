# Viral Content System

A repeatable workflow for turning "what's going viral in my niche on TikTok/Instagram
right now" into original video ideas for **your own account**, backed by data instead
of guesswork.

## Why this doesn't use a scraper

TikTok's and Instagram's Terms of Service prohibit unauthorized scraping, and pulling
another creator's videos to repost them is copyright infringement. Instead, this
system uses **vidIQ's outlier/trend APIs** (an official, ToS-compliant analytics
provider both platforms' creators use) to surface *metadata and performance patterns*
— view counts, hook structure, length, posting cadence, hashtags — not to copy anyone's
content. You use the patterns to make your own original videos.

## How it works

```
/viral-scan <niche or competitor handles>
        │
        ▼
1. Pull top outlier videos in your niche (vidIQ: outlier search, trending videos)
2. Normalize into data/raw/<date>_<niche>.json
3. scripts/analyze_patterns.py -> data/reports/<date>_<niche>_report.md
      (best duration, hook style, posting windows, hashtag clusters, format mix)
4. Draft original video concepts that follow the winning pattern
      (vidIQ: title/script/thumbnail generation) -> data/ideas/<date>_<niche>_ideas.md
5. Earnings estimate for your account size -> included in the report
```

Re-run `/viral-scan` weekly (or before each content-planning session) to keep the
pattern data fresh — trends on TikTok/Instagram move fast.

## Setup

1. Edit `config/niche.example.yaml`, save it as `config/niche.yaml`, and fill in:
   - your niche/keywords
   - a handful of competitor or inspiration accounts (public handles)
   - your own account handle + current follower count (for earnings estimates)
2. Run the skill: `/viral-scan` (it reads `config/niche.yaml` automatically), or
   `/viral-scan <niche>` to override for a one-off topic.

## Folder layout

- `config/` — your niche/competitor config (gitignored once you add real handles,
  since it's your personal targeting list)
- `data/raw/` — normalized video metadata pulled each run
- `data/reports/` — human-readable pattern-analysis reports
- `data/ideas/` — generated original video concepts per run
- `scripts/analyze_patterns.py` — the stats engine; run standalone on any raw JSON
  file if you want to re-analyze without a fresh pull

## Standalone analysis

If you already have a `data/raw/*.json` file, you can re-run just the analysis:

```
python3 scripts/analyze_patterns.py data/raw/2026-09-20_fitness.json
```
