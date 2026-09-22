#!/bin/bash
set -e
cd /home/user/saidadencoder222/toolkit-outreach
source venv/bin/activate

NICHES=(
  "fitness coach"
  "weight loss coach"
  "nutrition coach"
  "meal prep coach"
  "personal trainer online"
  "macro coach"
  "bodybuilding coach"
  "diet coach"
  "womens fitness coach"
  "keto coach"
  "day trading coach"
  "forex trading coach"
  "options trading coach"
  "crypto trading coach"
  "stock trading coach"
  "swing trading coach"
  "trading mentor"
  "futures trading coach"
  "dropshipping coach"
  "amazon fba coach"
  "ecommerce coach"
  "print on demand coach"
  "shopify coach"
  "social media marketing coach"
  "content creation coach"
  "copywriting coach"
  "email marketing coach"
  "digital marketing coach"
  "youtube automation coach"
  "personal branding coach"
  "content strategy coach"
  "real estate investing coach"
  "real estate wholesaling coach"
  "airbnb hosting coach"
  "business coach"
  "side hustle coach"
  "online coaching business"
  "freelancing coach"
  "consulting business coach"
  "coaching business mentor"
)

for n in "${NICHES[@]}"; do
  echo "=== $n ==="
  python3 main.py find-leads --query "$n" --max 25 || echo "(failed, continuing)"
done
