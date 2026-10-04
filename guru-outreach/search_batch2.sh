#!/bin/bash
set -e
cd /home/user/saidadencoder222/guru-outreach
source venv/bin/activate

NICHES=(
  "notion course creator"
  "canva course seller"
  "youtube automation course"
  "ai side hustle course"
  "print on demand course"
  "self publishing course"
  "kindle publishing course"
  "digital marketing course"
  "sales funnel course"
  "high ticket sales coach"
  "real estate wholesaling course"
  "airbnb hosting course"
  "personal branding coach"
  "content creation coach"
  "online coaching course"
  "money mindset coach"
  "financial freedom coach"
  "trading psychology coach"
  "swing trading course"
  "faceless youtube channel course"
)

for n in "${NICHES[@]}"; do
  echo "=== $n ==="
  python3 main.py find-leads --query "$n" --max 25 || echo "(failed, continuing)"
done
