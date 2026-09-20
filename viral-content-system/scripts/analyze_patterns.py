#!/usr/bin/env python3
"""Turn a batch of viral-video metadata into a pattern report.

Input: a JSON file containing a list of video records, e.g.

[
  {
    "platform": "tiktok",
    "id": "7312...",
    "url": "https://...",
    "creator": "@handle",
    "caption": "...",
    "views": 4200000,
    "likes": 610000,
    "comments": 8300,
    "shares": 41000,
    "duration_sec": 27,
    "posted_at": "2026-09-14T18:30:00Z",
    "hashtags": ["fitness", "beginner"],
    "hook_text": "first line viewers hear/see",
    "format": "talking_head"
  },
  ...
]

Only "views" and "duration_sec" are required for basic stats; everything else
degrades gracefully if missing. Usage:

    python3 analyze_patterns.py data/raw/2026-09-20_fitness.json [output.md]
"""
import json
import sys
import statistics
from collections import Counter, defaultdict
from datetime import datetime


def load_videos(path):
    with open(path) as f:
        videos = json.load(f)
    if not isinstance(videos, list) or not videos:
        raise ValueError("Input JSON must be a non-empty list of video records")
    return videos


def duration_bucket(seconds):
    if seconds is None:
        return "unknown"
    if seconds <= 15:
        return "0-15s"
    if seconds <= 30:
        return "16-30s"
    if seconds <= 60:
        return "31-60s"
    return "60s+"


def engagement_rate(v):
    views = v.get("views") or 0
    if not views:
        return None
    if v.get("likes") is None and v.get("comments") is None and v.get("shares") is None:
        return None
    interactions = (v.get("likes") or 0) + (v.get("comments") or 0) + (v.get("shares") or 0)
    return interactions / views


def top_quartile(videos):
    views_sorted = sorted(videos, key=lambda v: v.get("views") or 0, reverse=True)
    cutoff = max(1, len(views_sorted) // 4)
    return views_sorted[:cutoff]


def analyze(videos):
    report = {}

    views = [v["views"] for v in videos if v.get("views") is not None]
    report["n_videos"] = len(videos)
    report["median_views"] = statistics.median(views) if views else None
    report["max_views"] = max(views) if views else None

    by_bucket = defaultdict(list)
    for v in videos:
        by_bucket[duration_bucket(v.get("duration_sec"))].append(v.get("views") or 0)
    report["avg_views_by_duration"] = {
        bucket: round(statistics.mean(vs), 0) for bucket, vs in by_bucket.items() if vs
    }

    rates = [engagement_rate(v) for v in videos]
    rates = [r for r in rates if r is not None]
    report["median_engagement_rate"] = round(statistics.median(rates), 4) if rates else None

    hour_counts = Counter()
    for v in videos:
        ts = v.get("posted_at")
        if not ts:
            continue
        try:
            hour_counts[datetime.fromisoformat(ts.replace("Z", "+00:00")).hour] += 1
        except ValueError:
            continue
    report["posting_hour_histogram_utc"] = dict(sorted(hour_counts.items()))

    hashtag_counts = Counter()
    for v in videos:
        for tag in v.get("hashtags") or []:
            hashtag_counts[tag.lower().lstrip("#")] += 1
    report["top_hashtags"] = hashtag_counts.most_common(15)

    format_counts = Counter(v.get("format") for v in videos if v.get("format"))
    report["format_mix"] = dict(format_counts.most_common())

    top = top_quartile(videos)
    report["top_quartile_hooks"] = [
        {"creator": v.get("creator"), "views": v.get("views"), "hook_text": v.get("hook_text")}
        for v in top
        if v.get("hook_text")
    ][:10]

    return report


def render_markdown(report, source_path):
    lines = [f"# Pattern report — {source_path}", ""]
    lines.append(f"- Videos analyzed: **{report['n_videos']}**")
    if report["median_views"] is not None:
        lines.append(f"- Median views: **{int(report['median_views']):,}**")
    if report["max_views"] is not None:
        lines.append(f"- Max views: **{int(report['max_views']):,}**")
    if report["median_engagement_rate"] is not None:
        lines.append(f"- Median engagement rate (likes+comments+shares / views): **{report['median_engagement_rate']:.2%}**")
    lines.append("")

    if report["avg_views_by_duration"]:
        lines.append("## Avg views by duration")
        for bucket, avg in sorted(report["avg_views_by_duration"].items()):
            lines.append(f"- {bucket}: {int(avg):,}")
        lines.append("")

    if report["posting_hour_histogram_utc"]:
        lines.append("## Posting hour histogram (UTC)")
        for hour, count in report["posting_hour_histogram_utc"].items():
            lines.append(f"- {hour:02d}:00 — {count} video(s)")
        lines.append("")

    if report["format_mix"]:
        lines.append("## Format mix")
        for fmt, count in report["format_mix"].items():
            lines.append(f"- {fmt}: {count}")
        lines.append("")

    if report["top_hashtags"]:
        lines.append("## Top hashtags")
        for tag, count in report["top_hashtags"]:
            lines.append(f"- #{tag}: {count}")
        lines.append("")

    if report["top_quartile_hooks"]:
        lines.append("## Hooks from the top quartile by views")
        lines.append("(Study the *structure* — don't copy the wording.)")
        for h in report["top_quartile_hooks"]:
            views = f"{h['views']:,}" if h.get("views") else "?"
            lines.append(f"- **{views} views** ({h.get('creator', 'unknown')}): \"{h['hook_text']}\"")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source_path = sys.argv[1]
    videos = load_videos(source_path)
    report = analyze(videos)
    markdown = render_markdown(report, source_path)

    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
        with open(out_path, "w") as f:
            f.write(markdown)
        print(f"Wrote report to {out_path}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
