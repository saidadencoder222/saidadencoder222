#!/bin/bash
set -e
cd /home/user/saidadencoder222/toolkit-outreach
source venv/bin/activate

NICHES=(
  "meal plan for muscle gain coach"
  "vegan fitness coach"
  "postpartum fitness coach"
  "senior fitness coach"
  "sports performance coach"
  "online personal trainer program"
  "commercial real estate coach"
  "real estate mentor program"
  "land investing coach"
  "multifamily real estate coach"
  "real estate agent training"
  "day trader mentor"
  "options income coach"
  "passive income coach"
  "network marketing coach"
  "public speaking coach business"
  "course creator coach"
  "weight loss meal plan coach"
  "macro tracking coach"
  "no code course creator"
)

for n in "${NICHES[@]}"; do
  echo "=== $n ==="
  python3 main.py find-leads --query "$n" --max 25 || echo "(failed, continuing)"
done
