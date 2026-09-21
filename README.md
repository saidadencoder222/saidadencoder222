- 👋 Hi, I’m @saidadencoder222
- 👀 I’m interested in sports generally but i am trying to learn different types of code and build a strong foundation.
- 🌱 I’m currently learning python.
- 💞️ I’m looking to collaborate on nothing at the moment because i am not goood enough YET.
- 📫 How to reach me saidaden229@gmail.com

<!---
saidadencoder222/saidadencoder222 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

---

## Creator Growth Proposal Tool

Pulls a course seller / finance creator's public YouTube data, flags concrete
weak points (upload cadence, engagement rate, missing CTAs, thin monetization
footprint), and renders a personalized one-page proposal (with your own case
studies as social proof) that you host on GitHub Pages and link to from a
short outreach email. No scraping/reuse of the prospect's own images or video —
findings are text/stats only.

### Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in YOUTUBE_API_KEY, and GMAIL_* / PAGES_BASE_URL when ready to send
cp data/prospects.example.csv data/prospects.csv        # your real target list (gitignored)
cp data/social_proof.example.yaml data/social_proof.yaml # your real case studies (gitignored)
```

`data/prospects.csv` columns: `channel` (a `@handle`, channel ID, or search
term), `email`, `greeting_name`.

### Run

```bash
# Dry run — renders proposal pages into docs/proposals/<slug>/ and prints the
# email instead of sending it. Always do this first.
python src/main.py data/prospects.csv --sender-name "Your Name" --booking-link "https://cal.com/you"

# Commit + push docs/proposals/ so GitHub Pages serves the pages, set
# PAGES_BASE_URL in .env to https://<you>.github.io/<repo> once Pages is
# enabled (Settings -> Pages -> Deploy from branch -> main /docs), then:
python src/main.py data/prospects.csv --send
```

Sending requires `GMAIL_ADDRESS` + a Gmail **app password** (not your normal
password — generate one under Google Account -> Security -> App passwords)
in `.env`. Without those set, `--send` still falls back to dry-run.

Review every rendered page in `docs/proposals/` before pushing — the audit
heuristics are a starting point, not a substitute for a human check on tone
and accuracy per prospect.
