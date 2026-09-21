# Guru Outreach (course sellers / finance creators)

Finds course-seller/finance-creator YouTube channels, computes a real
audit from public data only (upload consistency, recent view averages,
whether their bio even has a link), and pitches a partnership/call to
only the channels where that audit found an actual gap.

## What this deliberately does NOT do

- **No cross-platform scraping.** Scoped to YouTube's official API only -
  Instagram/TikTok/Twitter don't have an equivalent compliant API, and
  scraping them raises the same ToS/legal issues avoided in the other
  two tools.
- **No fabricated findings.** `generate_audit.py`'s `build_observations()`
  only reports something if the numbers actually show it (inconsistent
  posting, no bio link, low view-to-sub ratio). A channel with none of
  those gets skipped entirely by `find-leads` rather than sent a forced
  "looks solid" pitch.
- **No mega-channels.** Capped to 5,000-300,000 subscribers - a channel
  with millions of subscribers obviously doesn't need an unsolicited
  growth audit, and pitching one anyway just looks tone-deaf.
- **No claimed avatar images.** This sandbox's network policy blocks
  external image hosts entirely (tested against three separate Google
  CDNs). Personalization is a deterministic per-channel accent color
  instead, same as creator-outreach.
- **Repeat sends capped** at `MAX_TOUCHES`, spaced `FOLLOWUP_AFTER_DAYS`
  apart, stopping immediately on unsubscribe - same pattern as the other
  two tools.

## Setup

Same as creator-outreach: `pip install -r requirements.txt` in a venv,
a Gmail OAuth `credentials.json`, and `YOUTUBE_API_KEY` in `.env`
(reuses the same key/project creator-outreach already has enabled).

## Usage

```bash
python main.py find-leads --query "how to make money online course" --max 25
python main.py list-leads
python main.py send-campaign --sender-email you@yourdomain.com
python main.py unsubscribe --email someone@example.com
```

`find-leads` only stores channels where the audit found a real,
computed issue - most searches will return far fewer leads than
candidates found, by design.
