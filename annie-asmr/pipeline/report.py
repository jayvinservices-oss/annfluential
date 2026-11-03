"""Step 8: weekly report. Earn-tab watch hours (estimated), views and retention per video, and the pace needed.

The Earn tab counts public watch hours from long-form videos over the last 365 days. The API has no
single field for that number, so this report estimates it: watch time in the last 365 days on videos
that are public now and are not Shorts. Studio's figure is the official one; compare the two each week.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta

from .config import REPORTS, config
from .ffmpeg_tools import fmt_ts
from .youtube import analytics_api, data_api, my_channel


def iso_seconds(d: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def _videos(yt, uploads_playlist: str) -> dict:
    ids, page = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads_playlist, maxResults=50,
                                    pageToken=page).execute()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        page = r.get("nextPageToken")
        if not page:
            break
    out = {}
    for n in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,contentDetails,status,statistics", id=",".join(ids[n:n + 50])).execute()
        for v in r.get("items", []):
            secs = iso_seconds(v["contentDetails"].get("duration", ""))
            out[v["id"]] = {
                "title": v["snippet"]["title"], "published": v["snippet"].get("publishedAt", "")[:10],
                "privacy": v["status"]["privacyStatus"], "seconds": secs,
                "short": secs <= 180, "views_total": int(v.get("statistics", {}).get("viewCount", 0)),
            }
    return out


def _by_video(ya, start: date, end: date) -> dict:
    r = ya.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
                           metrics="estimatedMinutesWatched,views,averageViewDuration,averageViewPercentage",
                           dimensions="video", sort="-estimatedMinutesWatched", maxResults=200).execute()
    cols = [h["name"] for h in r.get("columnHeaders", [])]
    return {row[0]: dict(zip(cols[1:], row[1:])) for row in r.get("rows", []) or []}


def _retention(ya, video_id: str, start: date, end: date) -> dict:
    try:
        r = ya.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
                               metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio",
                               filters=f"video=={video_id}").execute()
    except Exception:
        return {}
    rows = r.get("rows") or []
    points = {}
    for target in (0.1, 0.25, 0.5, 0.75):
        best = min(rows, key=lambda row: abs(row[0] - target), default=None)
        if best:
            points[f"{int(target * 100)}%"] = round(best[1] * 100)
    return points


def weekly_report() -> str:
    cfg = config()["channel"]
    yt, ya = data_api(), analytics_api()
    ch = my_channel(yt)
    subs = int(ch["statistics"].get("subscriberCount", 0))
    videos = _videos(yt, ch["contentDetails"]["relatedPlaylists"]["uploads"])

    today = date.today()
    end = today - timedelta(days=1)
    year = _by_video(ya, today - timedelta(days=365), end)
    week = _by_video(ya, today - timedelta(days=7), end)

    def hours(rows, ids=None):
        return sum(float(v["estimatedMinutesWatched"]) for k, v in rows.items() if ids is None or k in ids) / 60

    eligible = {k for k, v in videos.items() if v["privacy"] == "public" and not v["short"]}
    earn_hours = hours(year, eligible)
    all_hours = hours(year)
    week_hours = hours(week, eligible)

    goal = float(cfg["goal_watch_hours"])
    remaining = max(0.0, goal - earn_hours)
    target = date.fromisoformat(str(cfg["target_date"]))
    cutoff = datetime.strptime(cfg["hard_cutoff"], "%Y-%m-%d %H:%M").date()
    days_t = max(1, (target - today).days)
    days_c = max(1, (cutoff - today).days)
    need_t = remaining / days_t
    pace = week_hours / 7

    lines = [
        f"# Annie ASMR weekly report, {today.isoformat()}", "",
        "## Where we are", "",
        f"- Subscribers: **{subs:,}** of {cfg['goal_subscribers']:,} {'(met)' if subs >= cfg['goal_subscribers'] else ''}",
        f"- Public long-form watch hours, last 365 days (estimate of the Earn tab): **{earn_hours:,.0f}** of {goal:,.0f}",
        f"- All watch hours incl. Shorts and private/unlisted: {all_hours:,.0f}",
        f"- Still needed: **{remaining:,.0f} hours**",
        f"- To hit {target:%d %b %Y}: **{need_t:,.1f} hours a day** for {days_t} days "
        f"(cutoff {cutoff:%d %b}: {remaining / days_c:,.1f} a day)",
        f"- Last 7 days: {week_hours:,.1f} hours, about **{pace:,.1f} a day** "
        f"({'on pace' if pace >= need_t else f'{need_t / pace:,.1f}x short of pace' if pace else 'no hours yet'})",
        "",
        "Check the Earn tab in Studio for the official number; the API cannot see exactly what it counts.", "",
        "## Videos, last 7 days", "",
        "| Video | Length | Status | Views | Hours | Avg viewed | Avg % |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for vid, row in sorted(week.items(), key=lambda kv: -float(kv[1]["estimatedMinutesWatched"])):
        v = videos.get(vid, {"title": vid, "seconds": 0, "privacy": "?", "short": False})
        kind = "Short" if v["short"] else v["privacy"]
        lines.append(f"| {v['title'][:60]} | {fmt_ts(v['seconds'])} | {kind} | {int(row['views'])} | "
                     f"{float(row['estimatedMinutesWatched']) / 60:.1f} | {fmt_ts(float(row['averageViewDuration']))} | "
                     f"{float(row['averageViewPercentage']):.0f}% |")

    recent = sorted((k for k in eligible), key=lambda k: videos[k]["published"], reverse=True)[:5]
    lines += ["", "## Retention, newest long videos (share of viewers still watching)", "",
              "| Video | at 10% | 25% | 50% | 75% |", "|---|---:|---:|---:|---:|"]
    for vid in recent:
        r = _retention(ya, vid, today - timedelta(days=90), end)
        lines.append(f"| {videos[vid]['title'][:60]} | " + " | ".join(f"{r.get(p, '-')}%" for p in ("10%", "25%", "50%", "75%")) + " |")

    lines += ["", "## Top 10 by watch hours, last 365 days", "", "| Video | Hours | Counts for Earn tab |", "|---|---:|---|"]
    for vid, row in list(year.items())[:10]:
        v = videos.get(vid, {"title": vid})
        lines.append(f"| {v['title'][:60]} | {float(row['estimatedMinutesWatched']) / 60:.1f} | {'yes' if vid in eligible else 'no'} |")

    REPORTS.mkdir(parents=True, exist_ok=True)
    md = REPORTS / f"{today.isoformat()}.md"
    md.write_text("\n".join(lines) + "\n")
    (REPORTS / f"{today.isoformat()}.json").write_text(json.dumps({
        "date": today.isoformat(), "subscribers": subs, "earn_hours_estimate": round(earn_hours, 1),
        "all_hours": round(all_hours, 1), "week_hours": round(week_hours, 1), "needed_per_day": round(need_t, 1),
    }, indent=2))
    print("\n".join(lines))
    print(f"\nSaved {md}")
    return str(md)
