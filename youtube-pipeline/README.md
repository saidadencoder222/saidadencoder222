# YouTube movie-countdown pipeline

Builds "Top 10 [Character] Moments" style long-form videos — a proven,
high-retention compilation/countdown format — from movie clips you supply,
with an AI-written script narrated over them to drive engagement (hooks,
pattern changes, escalating stakes toward #1), auto-generated thumbnail and
metadata, and upload to YouTube. Designed to run on a schedule (3x/day, see
`.github/workflows/daily_pipeline.yml`).

## Copyright — read this before using real movie clips

"Top 10 Hulk Moments" style videos are built from actual copyrighted film
footage. This project will **not** automate acquiring that footage — no
scraping, no ripping, no downloading from clip databases (clip.cafe
included). That step is intentionally manual and is on you:

- Only use clips you have the legal right to use.
- Monetized use of studio-owned footage routinely triggers YouTube Content
  ID claims (ad revenue redirected to the rights holder, not you) and can
  escalate to copyright strikes; three strikes terminates the channel. Some
  compilation channels operate under a fair-use/commentary argument, but
  that requires substantive original commentary, not just clips + music,
  and it is not a guarantee against claims or strikes.
- **Never commit clip files to this git repo.** `.gitignore` already
  excludes `clip_bank/**/*.mp4` etc. Pushing copyrighted video to GitHub is
  redistribution.

If you want to avoid this risk entirely, the alternative is building the
same countdown format from footage you can freely license (official
trailers, stills, fan art with permission, or original recreation art)
instead of real scene clips — ask if you want that version instead.

## How it works

1. `pipeline/topics.py` picks the next "Top N" topic from
   `data/topics_pool.yaml` that (a) hasn't been used yet and (b) has clips
   sitting in `clip_bank/<clip_tag>/`.
2. `pipeline/clip_bank.py` indexes that folder; filenames are the only
   information Claude gets about each clip's content, so name them
   descriptively (`03_hulk_vs_loki_avengers.mp4`) — see `clip_bank/README.md`.
3. `pipeline/script_writer.py` asks Claude for a full countdown script:
   a hook intro + punchy narration per moment, counting down to #1.
4. `pipeline/voiceover.py` synthesizes each narration segment with edge-tts
   (free) or ElevenLabs, capturing word-level timing for captions.
5. `pipeline/video_builder.py` cuts each clip to the length of its
   narration, overlays a "#N" rank badge and burned-in captions, and
   concatenates everything with the narration audio.
6. `pipeline/thumbnail.py` grabs a frame from the #1 clip and overlays the
   title.
7. `pipeline/metadata.py` generates an optimized title/description/tags.
8. `pipeline/youtube_uploader.py` uploads the video + thumbnail via the
   YouTube Data API v3.
9. `pipeline/state.py` records what's been used so nothing repeats.

## One-time setup

1. **Python deps + ffmpeg**
   ```
   pip install -r requirements.txt
   sudo apt-get install ffmpeg fonts-dejavu-core   # or your OS equivalent
   ```

2. **Anthropic API key** — for script/title/description generation.
   Set `ANTHROPIC_API_KEY`.

3. **YouTube upload credentials** (one-time, local, not in CI):
   - In Google Cloud Console, create a project, enable the **YouTube Data
     API v3**, and create an OAuth 2.0 Client ID of type "Desktop app".
   - Add yourself as a test user on the OAuth consent screen (the upload
     scope is sensitive).
   - Run:
     ```
     python scripts/get_youtube_refresh_token.py \
       --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
     ```
     This opens a browser login and prints a refresh token.
   - Set `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.

4. **Populate the clip bank** — see `clip_bank/README.md`. Nothing will run
   for a topic until its folder has clips in it.

5. Copy `.env.example` to `.env` and fill in the values above for local
   runs, or add them as GitHub Actions repo secrets for the scheduled
   workflow (Settings -> Secrets and variables -> Actions).

## Running it

```
python main.py --dry-run     # build script+voiceover+video+thumbnail, skip upload
python main.py                # build and upload one video
python main.py --count 3      # three videos in one process
```

Always run `--dry-run` first and watch the output in `dry_run_output/`
before turning on real uploads — check pacing, caption accuracy, and that
the narration actually matches what's in each clip.

## Scheduling ("3 videos a day")

`.github/workflows/daily_pipeline.yml` fires 3x/day via cron. It targets a
**self-hosted runner** on purpose: `clip_bank/` lives only on your machine
(it's gitignored and must stay that way — see the copyright section), so a
GitHub-hosted runner has no way to reach your footage. Set your own machine
up as a self-hosted runner for this repo (Settings -> Actions -> Runners),
or just run `python main.py` on a cron job / Task Scheduler entry locally
instead of using GitHub Actions at all — it's the same script either way.

## Known limits, honestly

- **Quality depends entirely on your clip curation and filenames** — the
  script writer never watches the footage, so vague filenames produce
  generic narration that won't match what's on screen.
- **No de-duplication of which specific clips get used within a re-run
  topic** beyond "don't repeat a whole topic" — if you want a topic to be
  runnable multiple times with different clip subsets, add more clips than
  `clip_bank.max_moments` needs per run.
- **Auto-publish (`privacy_status: public`) means no human review step.**
  Consider `unlisted` in `config.yaml` while you're validating output
  quality, then switch to `public` once you trust it.
