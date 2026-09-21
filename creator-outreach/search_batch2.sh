#!/bin/bash
set -e
cd /home/user/saidadencoder222/creator-outreach
source venv/bin/activate

NICHES=(
  "screen time parenting"
  "picky eater toddler tips"
  "gentle discipline no yelling"
  "kids listening skills"
  "power struggles with toddlers"
  "positive parenting techniques"
  "raising resilient kids"
  "child behavior tips"
  "parenting without yelling"
  "calm parenting method"
  "toddler sleep training mom"
  "new mom tips vlog"
  "working mom parenting tips"
  "foster parenting vlog"
  "twin toddler mom"
  "autism parenting vlog"
  "teen parenting advice"
  "co-parenting communication tips"
  "stay at home dad vlog"
  "parenting influencer tips"
)

for n in "${NICHES[@]}"; do
  echo "=== $n ==="
  python3 main.py find-leads --query "$n" --max 25 || echo "(failed, continuing)"
done
