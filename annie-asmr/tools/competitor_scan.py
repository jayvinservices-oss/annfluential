"""Scan YouTube for the strongest ASMR videos in each of our sound niches.

Read-only: search.list + videos.list + channels.list. Public stats only (views,
likes, comments, length, age); other channels' watch time is private, so
"estimated watch hours" is views x an assumed average view length.

python -m tools.competitor_scan            -> metadata/competitors/<date>.yaml + reports/competitors-<date>.md
"""
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.youtube import data_api  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NICHES = {
    "gum": ["asmr gum chewing", "asmr gum popping", "asmr gum chewing no talking"],
    "knuckles": ["asmr knuckle cracking", "asmr finger cracking", "asmr cracking sounds sleep"],
    "lip gloss": ["asmr lip gloss application", "asmr lip gloss mouth sounds", "asmr lip gloss tapping"],
    "nails / tapping": ["asmr long nails tapping", "asmr nail tapping no talking"],
    "christmas": ["christmas asmr", "asmr gift wrapping", "asmr christmas ornaments tapping",
                  "asmr unwrapping presents"],
    "crafts": ["asmr card making", "asmr rhinestones", "asmr sticker peeling"],
    "sleep": ["asmr for sleep 1 hour no talking", "asmr mouth sounds for sleep"],
    "ai asmr": ["ai asmr", "ai asmr mouth sounds"],
}
WATCH_SHARE = 0.25          # assumed: average viewer watches a quarter of a long ASMR video


def iso_dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    d, h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + se


def main():
    yt = data_api()
    found = {}
    for niche, queries in NICHES.items():
        for q in queries:
            for order in ("viewCount", "relevance"):
                r = yt.search().list(part="id", q=q, type="video", maxResults=25, order=order,
                                     relevanceLanguage="en", safeSearch="moderate").execute()
                for it in r.get("items", []):
                    found.setdefault(it["id"]["videoId"], set()).add(niche)
    ids = list(found)
    vids = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute()
        vids += r["items"]
    chans = {}
    cids = list({v["snippet"]["channelId"] for v in vids})
    for i in range(0, len(cids), 50):
        r = yt.channels().list(part="snippet,statistics", id=",".join(cids[i:i + 50])).execute()
        for c in r["items"]:
            chans[c["id"]] = {"name": c["snippet"]["title"],
                              "subs": int(c["statistics"].get("subscriberCount", 0) or 0)}
    today = dt.datetime.now(dt.timezone.utc)
    rows = []
    for v in vids:
        sn, st = v["snippet"], v["statistics"]
        secs = iso_dur(v["contentDetails"]["duration"])
        if secs < 180:                      # Shorts / teasers don't earn long-form watch hours
            continue
        views = int(st.get("viewCount", 0) or 0)
        pub = dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        age = max((today - pub).days, 1)
        ch = chans.get(sn["channelId"], {})
        desc = sn.get("description", "")
        rows.append({
            "id": v["id"], "url": f"https://youtu.be/{v['id']}", "title": sn["title"],
            "channel": ch.get("name", sn["channelTitle"]), "subs": ch.get("subs", 0),
            "niches": sorted(found[v["id"]]), "minutes": round(secs / 60, 1), "views": views,
            "likes": int(st.get("likes", st.get("likeCount", 0)) or 0),
            "comments": int(st.get("commentCount", 0) or 0),
            "published": pub.date().isoformat(), "age_days": age,
            "views_per_day": round(views / age, 1),
            "outlier": round(views / max(ch.get("subs", 0), 1), 2),
            "est_watch_hours": int(views * secs / 3600 * WATCH_SHARE),
            "chapters": len(re.findall(r"^\s*\(?\d{1,2}:\d{2}(?::\d{2})?\)?\s", desc, re.M)) >= 3,
            "no_talking": bool(re.search(r"no talking", sn["title"] + desc, re.I)),
            "ai": bool(re.search(r"\bAI\b", sn["title"])),
            "tags": sn.get("tags", [])[:25],
        })
    rows.sort(key=lambda r: r["est_watch_hours"], reverse=True)
    date = today.date().isoformat()
    out = ROOT / "metadata" / "competitors"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{date}.yaml").write_text(yaml.safe_dump(rows, sort_keys=False, allow_unicode=True, width=120))
    print(f"{len(rows)} long-form videos saved to metadata/competitors/{date}.yaml")
    summarise(rows)


def summarise(rows):
    for niche in NICHES:
        sub = [r for r in rows if niche in r["niches"]]
        if not sub:
            continue
        mins = sorted(r["minutes"] for r in sub[:15])
        print(f"\n== {niche}: {len(sub)} videos; top-15 median length {mins[len(mins)//2]} min")
        for r in sorted(sub, key=lambda r: r["est_watch_hours"], reverse=True)[:8]:
            print(f"  {r['views']:>11,} v  {r['views_per_day']:>8,.0f}/d  {r['minutes']:>5}m  x{r['outlier']:<6} "
                  f"{'CH ' if r['chapters'] else '   '}{'NT ' if r['no_talking'] else '   '}"
                  f"{r['published'][:4]}  {r['channel'][:22]:22}  {r['title'][:80]}")
        fresh = [r for r in sub if r["age_days"] < 400]
        for r in sorted(fresh, key=lambda r: r["views_per_day"], reverse=True)[:4]:
            print(f"  NEW {r['views']:>9,} v {r['views_per_day']:>7,.0f}/d {r['minutes']:>5}m x{r['outlier']:<6} "
                  f"{r['channel'][:20]:20} {r['title'][:80]}")
    words = Counter(w for r in rows[:120] for w in re.findall(r"[a-z]+", r["title"].lower()) if len(w) > 3)
    print("\nTop title words (top 120 by est. watch hours):", ", ".join(f"{w} {n}" for w, n in words.most_common(40)))


if __name__ == "__main__":
    main()
