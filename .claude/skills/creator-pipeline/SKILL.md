---
name: creator-pipeline
description: Run one budgeted cycle of the outlier-research -> hook-style -> script/idea pipeline for saidaden's "creator monetization" content, using vidIQ MCP tools. Invoke with /creator-pipeline. Never spends more than pipeline/config.json's creditBudget.maxPerRun credits in one run.
---

# Creator content pipeline

Goal: keep discovering outlier TikTok/Reels in this niche, cluster their hooks into
reusable styles, and turn each style into a ready-to-film script — without blowing
through the vidIQ credit balance in one sitting.

State lives in `pipeline/state/*.json` and is git-committed, so progress persists
across sessions and across resets of this environment. Config lives in
`pipeline/config.json`. Always read both before doing anything.

## 0. Budget guard (always first)

1. Call `vidiq_balance`.
2. `runBudget = min(config.creditBudget.maxPerRun, balance.totalCredits - config.creditBudget.reserveFloor)`.
3. If `runBudget <= 0`, stop immediately and tell the user their balance is too low
   to run a cycle right now (report `renewableResetsAt`). Do not call any paid tool.
4. Track `spent = 0` through the run. Before every paid call, check
   `spent + callCost <= runBudget`; if it would exceed, skip that stage, leave it
   for the next run, and move on. Never guess a tool's cost — use the cost each
   tool's own description states.

## 1. Outlier discovery (5 credits/call)

- Read `pipeline/state/queries_run.json` (list of `{query, embeddingType}` already run).
- Pick the first entry in `config.seedQueries` NOT yet in that list.
- If all seed queries are exhausted, skip this stage (nothing new to search — the
  hook-analysis and idea stages can still run on existing data).
- Otherwise call `vidiq_instagram_tiktok_outlier_search` with:
  - `query` = the chosen seed query's `query`
  - `embeddingType` = its `embeddingType`
  - `audienceQuery` = `config.audienceQuery`
  - `resultsPerPlatform` = `config.resultsPerPlatform`
- Append the query to `queries_run.json`.
- For each returned video (both platforms), append to `pipeline/state/outliers.json`
  if its id/shortcode isn't already present: `{id, platform, url, caption, views,
  outlierScore, creatorHandle, discoveredAt}`. Dedupe on id.

## 2. Hook analysis (10 credits/call)

- From `outliers.json`, take outliers with no `hookAnalysis` field yet, sorted by
  `outlierScore` descending.
- For each one, while budget allows, call `vidiq_watch_shortform_content` with the
  video's full URL to get the scene-by-scene walkthrough.
- Write the result back onto that outlier record as `hookAnalysis` (the walkthrough
  text) plus a short `hookSummary` you write yourself (1 sentence: what happens in
  the first 3 seconds and why it stops the scroll).

## 3. Hook clustering (0 credits — your own judgment)

- Look at all outliers with a `hookSummary` but no `styleTag` yet.
- Group them into named styles (reuse existing names in `hooks.json.styles` where
  they fit; only add a new style name when nothing existing fits). Typical buckets:
  `pattern_interrupt_question`, `bold_claim_number`, `pov_text_overlay`,
  `before_after`, `myth_bust`, `story_hook`, `challenge_call`.
- Set each outlier's `styleTag`.
- Update `hooks.json.styles.<name>` = `{description, exampleOutlierIds: [...]}`.

## 4. Idea generation (~1 credit per minute of script)

- For each style in `hooks.json.styles` with >= 2 example outliers and no idea
  generated yet this cycle, and while budget allows:
  - Call `vidiq_generate_script` with:
    - `topic` = the niche (`config.niche`)
    - `title` = a working title you draft for this specific angle
    - `concept` = describe the hook style + how it applies to creator monetization
    - `research` = 2-3 concrete talking points pulled from the clustered examples'
      `hookAnalysis`/`hookSummary` (never copy a script verbatim — adapt the
      structure/pattern, not the content)
    - `lengthMinutes` = `config.scriptLengthMinutes`
  - This is async: poll `vidiq_job_poll` with the returned `mcpJobId` until
    `completed`.
  - Append the result to `pipeline/state/ideas.json`:
    `{id, styleTag, title, script, sourceOutlierIds, createdAt, status: "drafted"}`.
  - Also write a human-readable copy to `pipeline/ideas/<id>.md` (title, hook style,
    script, and a caption draft) — this is the file the user actually reads to film.

## 5. Wrap up every run

- Append one entry to `pipeline/log.md`: date, credits spent (broken down by stage),
  what was produced (new outliers found / hooks analyzed / ideas drafted), and what
  is queued for next run.
- Tell the user in chat: what ran, what it cost, what's ready to film, and roughly
  how many runs are left on the current balance.
- Commit the updated `pipeline/state/*.json`, `pipeline/ideas/*.md`, and
  `pipeline/log.md` (ask before pushing, per standing git rules).

## Publishing (separate, manual trigger — never run automatically)

Only run when the user explicitly asks to publish a specific finished video:

- **Instagram Reels**: requires a connected account with `publishingAvailable: true`
  (check `vidiq_instagram_connected_accounts`; if none, tell the user to connect at
  https://app.vidiq.com first). Then `vidiq_video_upload` (if the file isn't hosted
  yet) followed by `vidiq_instagram_publish_reel`, always showing the user the exact
  video + caption + account before calling it, per that tool's own approval rule.
- **TikTok / YouTube Shorts**: no publish tool exists in this MCP server. Tell the
  user to upload manually via each platform's app — see
  `pipeline/CROSS_POST_GUIDE.md` for how to vary the hook/caption per platform
  instead of posting identical copies.
