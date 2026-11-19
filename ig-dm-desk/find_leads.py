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
  python3 find_leads.py --seed my_handles.txt # also add handles you found by hand
Output: leads.csv  (load it in index.html)
"""
import argparse, csv, json, re, sys, time, urllib.request, urllib.parse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

# south, west, north, east
BBOX = {
    "gloucester":  (51.80, -2.30, 51.90, -2.18),
    "cheltenham":  (51.86, -2.14, 51.95, -2.03),
    "region":      (51.78, -2.35, 52.00, -2.00),   # both + Churchdown, Brockworth, Charlton Kings...
}

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
    ap.add_argument("--town", choices=list(BBOX), default="region")
    ap.add_argument("--seed", help="text file, one instagram handle or URL per line")
    ap.add_argument("--out", default="leads.csv")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    print(f"Querying OpenStreetMap for {', '.join(a.niches)} in {a.town}...")
    leads = [to_lead(e) for e in overpass(build_query(BBOX[a.town], a.niches))]
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
