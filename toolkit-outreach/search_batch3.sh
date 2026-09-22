#!/bin/bash
set -e
cd /home/user/saidadencoder222/toolkit-outreach
source venv/bin/activate

NICHES=(
  "nutrition coaching business"
  "online meal plan coach"
  "fat loss coach"
  "strength coach business"
  "sports nutrition coach"
  "algo trading coach"
  "prop trading coach"
  "trading psychology coach"
  "technical analysis coach"
  "trading course creator"
  "dropshipping course creator"
  "private label coach"
  "etsy seller coach"
  "online arbitrage coach"
  "podcast coach"
  "brand strategist coach"
  "seo coach"
  "affiliate marketing coach"
  "lead generation coach"
  "real estate agent coach"
  "property investing coach"
  "buy to let coach"
  "rental property coach"
  "online business coach"
  "scale your business coach"
  "sales coach"
  "high ticket sales coach"
  "confidence coach business"
  "life coach business"
  "career coach business"
)

for n in "${NICHES[@]}"; do
  echo "=== $n ==="
  python3 main.py find-leads --query "$n" --max 25 || echo "(failed, continuing)"
done
