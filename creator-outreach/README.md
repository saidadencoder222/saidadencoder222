# Creator Outreach

A small tool to find YouTube creators by niche, collect the ones who've
publicly listed a business contact email, and run a rate-limited, opt-out
respecting email campaign pitching a paid digital product.

## What this deliberately does NOT do

- **No email scraping.** The YouTube Data API doesn't return creator email
  addresses. This tool only picks up an email when a creator has typed it
  directly into their public channel description (the common "Business
  inquiries: ..." line). It does not click through the gated "reveal
  email" button on channel About pages - that's kept behind
  login/captcha specifically to prevent harvesting.
- **No disguised pitch.** The email templates are an upfront "I built a
  paid tool, here's what it does and costs" pitch, not a fake brand-deal
  or collab offer.
- **Repeat sends are capped.** Each lead gets at most `MAX_TOUCHES` emails
  total (default 2: one pitch, one follow-up), spaced at least
  `FOLLOWUP_AFTER_DAYS` apart, and stops immediately once flagged
  unsubscribed.

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in:
   - `YOUTUBE_API_KEY` - from console.cloud.google.com (enable "YouTube
     Data API v3")
   - `SENDER_NAME`, `PRODUCT_NAME`, `PRODUCT_LINK`
3. Create an OAuth "Desktop app" client in Google Cloud Console (APIs &
   Services -> Credentials), download it as `credentials.json` in this
   folder. The Gmail scopes needed are `gmail.send` and `gmail.readonly`
   (the latter only to detect UNSUBSCRIBE replies).

## Usage

```bash
# 1. Find creators in a niche and store any public contact emails found
python main.py find-leads --query "home cooking channel" --max 50 --min-subs 1000

# 2. See what got stored
python main.py list-leads

# 3. Send today's batch (new pitches + due follow-ups, up to DAILY_SEND_LIMIT)
#    First run opens a browser for Gmail OAuth consent.
python main.py send-campaign --sender-email you@gmail.com

# Manually opt someone out
python main.py unsubscribe --email creator@example.com
```

Run `send-campaign` periodically (a daily cron job or systemd timer) -
each run sends at most one batch and is safe to re-run since sends are
tracked in `leads.db` and never duplicated.

## Compliance notes

This sends unsolicited commercial email, so before running it at any
volume:

- Keep the honest framing in the templates - don't repurpose them into a
  disguised "brand partnership" pitch.
- Every email includes a working, immediate opt-out (reply UNSUBSCRIBE);
  `send-campaign` checks for these replies and spam-folder placement
  before sending anything new, and never re-emails an opted-out address.
- CAN-SPAM (US) requires accurate sender info and honoring opt-outs
  promptly - both are handled here, but you're responsible for keeping
  `SENDER_NAME`/your Gmail address accurate. If you'll be emailing
  recipients in the EU/UK, review GDPR consent requirements separately -
  legitimate-interest cold outreach rules are stricter there.
- Keep `DAILY_SEND_LIMIT` conservative; Gmail will rate-limit or flag
  accounts that send a lot of near-identical mail quickly.
