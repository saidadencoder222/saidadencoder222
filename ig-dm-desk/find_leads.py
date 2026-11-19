#!/usr/bin/env python3
"""
Find local businesses in the Gloucester / Cheltenham area WITHOUT the Google
Places API, and pull their Instagram handle from their own public website.

Sources (all free, no API key):
  1. OpenStreetMap via the Overpass API  -> business names, category, address, website
  2. Each business's own homepage        -> the instagram.com/<handle> link they publish

It does NOT scrape Instagram itself (against Meta's terms, and gets IPs blocked).
Checking whether an account posts regularly is done by you in the desk app, one
click per profile.

Usage:
  python3 find_leads.py                       # all niches, whole area
  python3 find_leads.py --niches beauty food  # only some niches
  python3 find_leads.py --town cheltenham     # only one town
  python3 find_leads.py --town southwest      # every South West town in the list
  python3 find_leads.py --seed my_handles.txt # also add handles you found by hand
Output: leads.csv  (load it in index.html)
"""
import argparse, csv, json, re, sys, time, urllib.request, urllib.parse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

# south, west, north, east
# Town-sized boxes (south, west, north, east). Small boxes keep Overpass fast and polite.
BBOX = {
    "gloucester":  (51.80, -2.30, 51.90, -2.18),
    "cheltenham":  (51.86, -2.14, 51.95, -2.03),
    "region":      (51.78, -2.35, 52.00, -2.00),
    "stroud":      (51.70, -2.25, 51.76, -2.17),
    "cirencester": (51.69, -1.99, 51.75, -1.93),
    "bristol":     (51.40, -2.70, 51.52, -2.50),
    "bath":        (51.35, -2.42, 51.42, -2.31),
    "weston":      (51.32, -2.99, 51.38, -2.90),
    "taunton":     (50.99, -3.15, 51.04, -3.06),
    "yeovil":      (50.92, -2.66, 50.97, -2.60),
    "swindon":     (51.53, -1.84, 51.61, -1.71),
    "salisbury":   (51.05, -1.82, 51.09, -1.76),
    "exeter":      (50.69, -3.56, 50.75, -3.48),
    "plymouth":    (50.34, -4.19, 50.42, -4.07),
    "torquay":     (50.44, -3.57, 50.50, -3.49),
    "barnstaple":  (51.06, -4.09, 51.10, -4.03),
    "truro":       (50.25, -5.09, 50.28, -5.03),
    "falmouth":    (50.14, -5.10, 50.17, -5.04),
    "newquay":     (50.40, -5.10, 50.44, -5.04),
    "stives":      (50.20, -5.50, 50.23, -5.46),
    "penzance":    (50.11, -5.56, 50.14, -5.51),
    "bournemouth": (50.70, -1.92, 50.76, -1.80),
    "poole":       (50.70, -2.02, 50.74, -1.94),
    "dorchester":  (50.70, -2.46, 50.73, -2.42),
    "weymouth":    (50.60, -2.48, 50.64, -2.43),
    "chippenham":  (51.44, -2.14, 51.48, -2.09),
    "trowbridge":  (51.30, -2.23, 51.34, -2.18),
    "wells":       (51.19, -2.66, 51.22, -2.62),
    "glastonbury": (51.13, -2.73, 51.16, -2.69),
    "tiverton":    (50.89, -3.51, 50.92, -3.46),
}
SOUTHWEST = [t for t in BBOX if t != "region"]

NICHES = {
    "beauty":  [("shop", "hairdresser|beauty|massage|tattoo|nails|barber"),
                ("amenity", "beauty|spa")],
    "food":    [("amenity", "restaurant|cafe|bar|pub|fast_food|ice_cream"),
                ("shop", "bakery|deli|coffee|confectionery")],
    "fitness": [("leisure", "fitness_centre|sports_centre|yoga"),
                ("sport", "fitness|yoga|pilates|martial_arts|boxing|crossfit")],
    "health":  [("amenity", "dentist|clinic|physiotherapist"),
                ("healthcare", "dentist|physiotherapist|alternative|clinic")],
    "retail":  [("shop", "clothes|florist|jewelry|gift|boutique|shoes|interior_decoration|furniture")],
    "auto":    [("shop", "car|car_repair|car_parts"), ("amenity", "car_wash")],
}

IG_RESERVED = {"p", "reel", "reels", "explore", "accounts", "sharer", "share", "stories",
               "tv", "about", "developer", "directory", "legal", "web", "oauth", "direct",
               "embed", "static", "privacy", "terms", "instagram", "ig"}
IG_RE = re.compile(r'(?:https?:)?//(?:www\.)?instagram\.com/([A-Za-z0-9_.]{2,30})', re.I)
UA = "Mozilla/5.0 (compatible; LocalLeadFinder/1.0)"


def build_query(bbox, niches):
    s, w, n, e = bbox
    parts = []
    for niche in niches:
        for key, vals in NICHES[niche]:
            parts.append(f'  nwr["name"]["{key}"~"^({vals})$"]({s},{w},{n},{e});')
    return "[out:json][timeout:120];\n(\n" + "\n".join(parts) + "\n);\nout center tags;"


def overpass(query):
    data = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for url in OVERPASS:
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=150) as r:
                return json.load(r)["elements"]
        except Exception as ex:
            last = ex
            print(f"  ! {url} failed: {ex}", file=sys.stderr)
            time.sleep(3)
    raise SystemExit(f"Overpass unreachable: {last}")


def clean_handle(raw):
    if not raw:
        return ""
    raw = raw.strip()
    m = IG_RE.search(raw if "instagram.com" in raw else "//instagram.com/" + raw.lstrip("@/"))
    if not m:
        return ""
    h = m.group(1).rstrip(".").lower()
    return "" if h in IG_RESERVED else h


def instagram_from_html(html):
    """Most common non-reserved instagram handle linked on the page."""
    c = Counter()
    for m in IG_RE.finditer(html):
        h = m.group(1).rstrip(".").lower()
        if h not in IG_RESERVED:
            c[h] += 1
    return c.most_common(1)[0][0] if c else ""


def fetch(url, timeout=10):
    if not url.startswith("http"):
        url = "http://" + url
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(600_000).decode("utf-8", "ignore")


def find_instagram(website):
    for suffix in ("", "/contact"):
        try:
            h = instagram_from_html(fetch(website.rstrip("/") + suffix))
            if h:
                return h
        except Exception:
            pass
    return ""


def category(tags):
    for k in ("shop", "amenity", "leisure", "healthcare", "sport", "craft"):
        if k in tags:
            return tags[k].replace("_", " ")
    return ""


def to_lead(el):
    t = el.get("tags", {})
    addr = " ".join(filter(None, [t.get("addr:housenumber"), t.get("addr:street")]))
    town = t.get("addr:city") or t.get("addr:suburb") or ""
    return {
        "name": t.get("name", ""),
        "category": category(t),
        "address": ", ".join(filter(None, [addr, town, t.get("addr:postcode", "")])),
        "phone": t.get("phone") or t.get("contact:phone") or "",
        "website": t.get("website") or t.get("contact:website") or "",
        "instagram": clean_handle(t.get("contact:instagram") or t.get("instagram") or ""),
        "source": "openstreetmap",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--niches", nargs="+", choices=list(NICHES), default=list(NICHES))
    ap.add_argument("--town", nargs="+", choices=list(BBOX) + ["southwest"], default=["region"],
                    help="one or more towns, or 'southwest' for every town listed")
    ap.add_argument("--target", type=int, default=0, help="stop once this many leads with Instagram are found")
    ap.add_argument("--seed", help="text file, one instagram handle or URL per line")
    ap.add_argument("--out", default="leads.csv")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    towns = SOUTHWEST if "southwest" in a.town else a.town
    leads = []
    for t in towns:
        print(f"Querying OpenStreetMap: {', '.join(a.niches)} in {t}...")
        try:
            leads += [to_lead(e) for e in overpass(build_query(BBOX[t], a.niches))]
        except SystemExit as ex:
            print(f"  skipped {t}: {ex}", file=sys.stderr)
        time.sleep(5)   # be polite to the free Overpass servers
    # de-dupe by name+address
    seen, uniq = set(), []
    for l in leads:
        k = (l["name"].lower(), l["address"].lower())
        if l["name"] and k not in seen:
            seen.add(k); uniq.append(l)
    leads = uniq
    print(f"  {len(leads)} businesses found")

    todo = [l for l in leads if not l["instagram"] and l["website"]]
    print(f"  checking {len(todo)} websites for an Instagram link...")
    with ThreadPoolExecutor(a.workers) as ex:
        for l, h in zip(todo, ex.map(lambda l: find_instagram(l["website"]), todo)):
            l["instagram"] = h

    if a.seed:
        for line in open(a.seed):
            h = clean_handle(line)
            if h and not any(l["instagram"] == h for l in leads):
                leads.append({"name": h, "category": "", "address": "", "phone": "",
                              "website": "", "instagram": h, "source": "manual"})

    with_ig = [l for l in leads if l["instagram"]]
    if a.target:
        with_ig = with_ig[:a.target]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "category", "address", "phone",
                                          "website", "instagram", "source"])
        w.writeheader(); w.writerows(with_ig)
    print(f"Saved {len(with_ig)} leads with an Instagram handle -> {a.out}")
    print(f"({len(leads) - len(with_ig)} businesses had no Instagram link found; "
          f"those are good phone/walk-in targets too)")
    no_ig = [l for l in leads if not l["instagram"]]
    with open("no_instagram.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "category", "address", "phone",
                                          "website", "instagram", "source"])
        w.writeheader(); w.writerows(no_ig)


if __name__ == "__main__":
    main()
