# Cross-posting guide

## Automated

**Instagram Reels** — once you connect your IG account at https://app.vidiq.com,
Claude can publish directly with the `vidiq_instagram_publish_reel` tool. It always
shows you the exact video, caption, and account before it actually posts.

## Manual (no API for these)

**TikTok** and **YouTube Shorts** have no publish tool available here. Upload
through each app directly. Two reasons this is actually fine, not a gap to route
around:

1. Both platforms' own algorithms tend to suppress content that's detectably
   identical to what's already live elsewhere (watermarks, matching hashes).
2. Native-feeling posts perform better anyway — a caption/hook tuned to the
   platform beats a copy-pasted one.

**Workflow per finished idea:**

1. Film/edit once, export a clean vertical MP4 with no platform watermark.
2. Post to each platform with a *platform-tuned* opening line and caption:
   - **TikTok**: punchier, more casual hook text overlay in the first frame; TikTok
     search-friendly caption (people search TikTok like a search engine).
   - **IG Reels**: hook can lean slightly more polished; caption can be longer,
     first line still has to earn the tap on "more".
   - **YouTube Shorts**: title/caption can be more literal/keyword-forward — Shorts
     surfaces through YouTube search and suggested-Shorts more than hashtags.
3. Each `pipeline/ideas/<id>.md` file includes one script but you (or Claude, when
   asked) should draft the platform-specific caption variants before you post —
   that's a free (0-credit) step, just ask.

## Tracking what worked

Once accounts are connected, `vidiq_video_stats`, `vidiq_instagram_owner_insights`,
and `vidiq_channel_performance_trends` can pull real performance back in, so the
next `/creator-pipeline` run can weight which hook styles actually converted for
you, not just which ones are outliers elsewhere. Not wired into the automated skill
yet — ask for it once you have real posts up.
