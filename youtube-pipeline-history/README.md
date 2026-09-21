# History documentary pipeline

Builds long-form (7-11 min) history documentary videos fully automatically:
AI-written narration, AI voiceover, real historical images sourced live
from Wikimedia Commons with a Ken Burns pan/zoom, auto-generated thumbnail
and metadata, uploaded to YouTube. Designed to run on a schedule (3x/day,
see `.github/workflows/daily_pipeline.yml`).

## Why this one needs nothing from you (unlike the movie-clip pipeline)

The sibling `youtube-pipeline/` project builds "Top 10 [character] Moments"
videos and requires you to manually supply real movie clips, because there
is no legal way to automate acquiring copyrighted film footage.

This pipeline is different: **Wikimedia Commons is an actual public-domain
/ Creative-Commons-licensed archive with a free, keyless search API.**
`pipeline/visuals.py` checks every image's license metadata against
`config.yaml`'s `allowed_licenses` and only uses images that clear it —
public domain, CC0, or CC-BY/CC-BY-SA (which get auto-attributed in the
video description, as their license requires). Nothing is scraped from a
site that doesn't license its content for this; nothing needs to be
manually curated. That's what makes this one runnable on a plain
GitHub-hosted Actions runner with zero setup beyond API keys.

## How it works

1. `pipeline/topics.py` picks the next unused topic from
   `data/topics_pool.yaml` (asks Claude for more once the pool is used up).
2. `pipeline/script_writer.py` asks Claude for a full documentary
   narration with specific facts/dates, interleaved with
   `[VISUAL: <search phrase>]` cues for real archival imagery.
3. `pipeline/voiceover.py` synthesizes the narration with edge-tts (free)
   or ElevenLabs, capturing word-level timing.
4. `pipeline/visuals.py` searches Wikimedia Commons for each cue,
   license-filters the results, and downloads what clears the filter.
5. `pipeline/video_builder.py` builds a Ken Burns slow-zoom sequence
   across the images (each held for a share of the runtime proportional to
   the narration), with burned-in captions.
6. `pipeline/thumbnail.py` overlays the title on the first sourced image.
7. `pipeline/metadata.py` generates title/description/tags via Claude and
   appends required CC attribution lines to the description.
8. `pipeline/youtube_uploader.py` uploads via the YouTube Data API v3.
9. `pipeline/state.py` records what's been used so nothing repeats.

## One-time setup

1. **Python deps + ffmpeg**
   ```
   pip install -r requirements.txt
   sudo apt-get install ffmpeg fonts-dejavu-core   # or your OS equivalent
   ```

2. **Anthropic API key** — for script/title/description generation.
   Set `ANTHROPIC_API_KEY`. No image API key needed.

3. **YouTube upload credentials** (one-time, local, not in CI):
   - In Google Cloud Console, create a project, enable the **YouTube Data
     API v3**, and create an OAuth 2.0 Client ID of type "Desktop app".
   - Add yourself as a test user on the OAuth consent screen.
   - Run:
     ```
     python scripts/get_youtube_refresh_token.py \
       --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
     ```
   - Set `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.

4. Copy `.env.example` to `.env` and fill in the values above for local
   runs, or add them as GitHub Actions repo secrets for the scheduled
   workflow (Settings -> Secrets and variables -> Actions).

## Running it

```
python main.py --dry-run     # build script+voiceover+video+thumbnail, skip upload
python main.py                # build and upload one video
python main.py --count 3      # three videos in one process
```

Always run `--dry-run` first and check `dry_run_output/` — read the
narration against the images it picked, and confirm facts/dates before
trusting it unattended. Claude can still get historical specifics wrong;
this pipeline doesn't fact-check itself.

## Scheduling ("3 videos a day")

`.github/workflows/daily_pipeline.yml` fires 3x/day via cron on a normal
`ubuntu-latest` runner — no self-hosting needed, since nothing it depends
on lives outside the repo/APIs. It commits `data/state.json` back after
each run so topic rotation persists across runs.

## Known limits, honestly

- **Claude can get historical facts, dates, or figures wrong.** This
  pipeline doesn't verify claims against a source — spot-check a few
  dry runs before trusting it unattended, especially early on.
- **Image relevance depends on Commons' coverage.** Well-documented
  Western/20th-century topics return strong results; obscure or
  poorly-photographed topics may return thin or loosely-related images.
- **Auto-publish (`privacy_status: public`) means no human review step.**
  Consider `unlisted` in `config.yaml` while validating output quality.
