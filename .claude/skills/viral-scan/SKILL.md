---
name: viral-scan
description: Pull current viral outlier videos in a niche on TikTok/Instagram (via the vidIQ MCP tools), analyze what patterns drive their views, and draft original video concepts for the user's own account in that style. Use when the user wants to research trends, find viral patterns, or plan content for their TikTok/Instagram account.
---

# Viral Scan

Repeatable workflow: fresh trend data in, a pattern report and original content
ideas out. Lives in `viral-content-system/` at the repo root.

## Never do this

- Never download, re-encode, or repost another creator's actual video file.
- Never generate captions/scripts that copy a specific creator's wording —
  only structural patterns (length, hook style, pacing, format) are fair game.
- If the user asks to scrape/rip someone else's account content to repost it,
  decline and explain why (ToS violation + copyright infringement), same as
  you would outside this skill.

## Steps

1. **Load config.** Read `viral-content-system/config/niche.yaml` if it
   exists. If not, ask the user for: niche/keywords, optional inspiration
   handles, their own handle + follower count, and which platform(s)
   (tiktok/instagram/both). Offer to save their answers into that file for
   next time.

2. **Pull outliers.** Use the vidIQ MCP tools to gather viral videos for the
   niche:
   - `vidiq_instagram_tiktok_outlier_search` and/or `vidiq_outliers` with the
     niche keywords
   - `vidiq_trending_videos` / `vidiq_trend_categories` for broader trend context
   - `vidiq_ig_profile_reels` for each `inspiration_accounts` handle, if given
   - `vidiq_video_stats` and `vidiq_video_transcript` on the top results to
     get view/engagement numbers and the opening hook text
   - `vidiq_comment_insights` optionally, to see what resonates in comments

3. **Normalize and save.** Map each result into the schema documented at the
   top of `viral-content-system/scripts/analyze_patterns.py` (platform, id,
   url, creator, caption, views, likes, comments, shares, duration_sec,
   posted_at, hashtags, hook_text, format). Save as
   `viral-content-system/data/raw/<YYYY-MM-DD>_<niche-slug>.json`.

4. **Analyze.** Run:
   ```
   python3 viral-content-system/scripts/analyze_patterns.py \
     viral-content-system/data/raw/<file>.json \
     viral-content-system/data/reports/<YYYY-MM-DD>_<niche-slug>_report.md
   ```

5. **Generate original ideas.** Using the report's patterns (winning duration
   bucket, hook structure, format mix, posting-hour histogram, top hashtags),
   draft 3-5 **original** video concepts for the user's own account:
   - `vidiq_generate_titles` and `vidiq_generate_script` per concept, written
     around the user's own niche/angle — not paraphrases of a specific viral
     video
   - `vidiq_generate_thumbnail` for cover art ideas
   - `vidiq_keyword_research` to sanity-check hashtag/keyword choices
   Save the concepts to
   `viral-content-system/data/ideas/<YYYY-MM-DD>_<niche-slug>_ideas.md`.

6. **Earnings estimate.** Use `vidiq_earnings_calculate` and/or
   `vidiq_video_earnings_estimate` with the user's follower count / expected
   views to give a realistic revenue range. Append this to the report.

7. **Summarize for the user** in chat: the single strongest pattern found,
   the best posting window, and the top 1-2 video concepts — point them to
   the full report/ideas files for the rest. Don't dump the whole markdown
   into chat.

## Re-running

This is meant to be re-run regularly (weekly is reasonable for fast-moving
TikTok/Instagram trends). Each run's raw data and report/ideas files are
timestamped, so nothing gets overwritten — the user can compare reports over
time to see how patterns shift.
