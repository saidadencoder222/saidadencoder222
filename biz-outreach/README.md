# Biz Outreach (no-website demo pitch)

Finds local businesses with no website via the Google Places API, builds
a real one-page demo site for each, and runs a rate-limited, opt-out
respecting email campaign offering to build it out - only for the subset
that has a publicly discoverable contact email.

## What this deliberately does NOT do

- **No search-page scraping.** Businesses are found via the official
  Google Places API (Text Search + Place Details), not by scraping
  google.com search results, which violates Google's ToS.
- **No fabricated "I built you a demo" claims.** `demo_site.py` actually
  writes a real HTML page per lead before any email goes out - the link
  in the email always points to something real.
- **No email harvesting.** Places API never returns an email address. The
  only email source here is a business's own public Facebook/Instagram
  page text, when the business itself put a social link in its Google
  listing's "website" field. Expect a **low hit rate** - most listings
  with no site simply don't publish a discoverable email anywhere. Leads
  without an email are still recorded (with phone/address) for manual or
  phone follow-up, but the campaign only ever auto-emails leads that have
  one.
- **Repeat sends are capped**, same as the other outreach tool: at most
  `MAX_TOUCHES` per lead, spaced `FOLLOWUP_AFTER_DAYS` apart, stopping
  immediately on unsubscribe.

## Setup

1. `pip install -r requirements.txt`
2. Enable **billing** on your Google Cloud project (Places API requires
   it - Google gives $200/month free credit across Maps Platform, but a
   card on file is mandatory even to get a working key).
3. Enable **Places API** (console.cloud.google.com -> APIs & Services ->
   Library), then create an API key under Credentials. Restrict it to
   Places API only.
4. Copy `.env.example` to `.env`, set `GOOGLE_PLACES_API_KEY`,
   `SENDER_NAME`, and `DEMO_BASE_URL` (see hosting below).
5. Reuse or create a Gmail OAuth "Desktop app" `credentials.json` the
   same way as the creator-outreach tool (needs `gmail.send` +
   `gmail.readonly` scopes).

### Hosting the demo pages

`find-leads` writes each demo to `demos/<slug>/index.html`. That folder
needs to be reachable at the URL in `DEMO_BASE_URL` before you send any
email. Simplest free option: commit the `demos/` folder to a GitHub repo
and enable GitHub Pages on it (Settings -> Pages -> deploy from
branch/folder), then set `DEMO_BASE_URL` to the resulting
`https://<user>.github.io/<repo>/...` path. Any other static host
(Netlify, Vercel, S3, your own server) works too - just point
`DEMO_BASE_URL` at wherever you upload the `demos/` folder.

## Usage

```bash
# 1. Find no-website businesses in a niche/area, generate their demo pages
python main.py find-leads --query "plumbers in Austin, TX" --max 40

# 2. Upload/publish the demos/ folder to wherever DEMO_BASE_URL points, then:
python main.py list-leads

# 3. Send today's batch (only to leads with a discovered email)
python main.py send-campaign --sender-email you@gmail.com

python main.py unsubscribe --email business@example.com
```

## Compliance and honesty notes

- Keep the "I built you a demo" framing true - never send the email
  before the linked page is actually live.
- Every email includes a working opt-out; `send-campaign` checks for
  UNSUBSCRIBE replies and spam placement before sending anything new.
- The generated demo page includes a "not affiliated with or endorsed
  by {business_name}" line - don't remove it; it keeps the demo from
  looking like an official site you don't have rights to represent.
- CAN-SPAM requires accurate sender info and prompt opt-out handling -
  both are wired in, but keep `SENDER_NAME` accurate.
- There's no way to guarantee outcomes like revenue targets from this
  tooling - conversion depends entirely on lead quality, demo quality,
  and your follow-through on calls.
