"""Shorts as trailers for the long video: cut, describe, upload as private drafts, and publish only on Ann's yes.

python -m pipeline shorts <slug> [--n 3]       cut N vertical Shorts from the best moments, write their metadata
python -m pipeline upload <slug>-short1         private draft (same uploader as the long videos)
python -m pipeline publish-short <slug>-short1  public or scheduled, ONLY if metadata/publish-approvals.yaml says yes
                                                and the long video is already public.
Moments: one per chapter (first N chapters), the window with the highest steady loudness, skipping fades.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

from .assemble import render_path, timeline_path, trailer
from .config import METADATA, RENDERS, config
from .episode import load_episode, voice_lines
from .metadata import BANNED, meta_path, upload_record

APPROVALS = METADATA / "publish-approvals.yaml"


def loudness_track(src: Path, start: float, seconds: float) -> list[float]:
    """Momentary loudness every 0.1 s for a stretch of the render."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-ss", str(start), "-t", str(seconds), "-i", str(src),
                        "-vn", "-af", "aresample=8000,asetnsamples=800,ebur128=metadata=1,"
                        "ametadata=print:key=lavfi.r128.M", "-f", "null", "-"],
                       capture_output=True, text=True)   # 800 samples at 8 kHz = one value per 0.1 s
    return [max(float(m), -70.0) for m in re.findall(r"lavfi\.r128\.M=(-?[\d.]+)", p.stderr)]


def best_window(track: list[float], win: int) -> int:
    if len(track) <= win:
        return 0
    s = sum(track[:win])
    best, at = s, 0
    for i in range(1, len(track) - win):
        s += track[i + win - 1] - track[i - 1]
        if s > best:
            best, at = s, i
    return at


def short_title(ep: dict, chapter: str) -> str:
    base = re.sub(r"\s*&\s*", " & ", chapter).strip()
    t = f"{base} ASMR #shorts"
    if "no talking" in ep["title"].lower():
        t = f"{base} ASMR (No Talking) #shorts"
    return t[:100]


def make(slug: str, n: int = 3, seconds: float = 35) -> list[str]:
    ep = load_episode(slug)
    tl = timeline_path(slug)
    if not tl.exists():
        raise SystemExit(f"Render the long video first: python -m pipeline assemble {slug}")
    timeline = json.loads(tl.read_text())
    yt = config()["youtube"]
    up = upload_record(slug)
    link = f"https://youtu.be/{json.loads(up.read_text())['video_id']}" if up.exists() else "LINK_TO_FULL_VIDEO"
    made = []
    chs = timeline["chapters"]
    ends = [c["t"] for c in chs[1:]] + [timeline["seconds"]]
    for k, (ch, end) in enumerate(list(zip(chs, ends))[:n], start=1):
        lo, hi = ch["t"] + 15, min(end - 15, ch["t"] + 15 + 300)    # first 5 minutes of the chapter, no fades
        if hi - lo < seconds + 5:
            continue
        track = loudness_track(render_path(slug), lo, hi - lo)
        at = lo + best_window(track, int(seconds * 10)) / 10
        cut = trailer(ep, at, seconds, float(ep.get("short_x", 0.5)))  # 0 = left edge, 1 = right edge
        name = f"{slug}-short{k}"
        final = RENDERS / f"{name}.mp4"
        cut.replace(final)
        disc = yt["disclosure"] if voice_lines(ep) else yt.get("disclosure_no_voice", yt["disclosure"])
        title = short_title(ep, ch["title"])
        errors = [f"title uses '{b}'" for b in BANNED if re.search(rf"\b{re.escape(b)}\b", title.lower())]
        if "LINK_TO" in link:
            errors.append("upload the long video first so the Short can link to it")
        meta = {
            "slug": name, "file": str(final), "title": title,
            "description": f"The full {timeline['length']} video: {link}\n\n{ep['title']}\n\n"
                           f"{' '.join(disc.split())}\n\n#ASMR #Shorts #ASMRforSleep",
            "tags": list(yt.get("base_tags", []))[:5] + list(ep.get("tags") or [])[:5],
            "category_id": yt.get("category_id", "26"), "default_language": yt.get("default_language", "en"),
            "privacy_status": "private", "contains_synthetic_media": True, "made_for_kids": False,
            "parent": slug, "moment": {"chapter": ch["title"], "at": round(at, 1), "seconds": seconds},
            "checks": {"errors": errors, "warnings": ["after upload, set 'Related video' to the full video in the "
                                                      "YouTube app (the API cannot set it)"]},
        }
        meta_path(name).write_text(json.dumps(meta, indent=2, ensure_ascii=False))
        print(f"  {name}: {ch['title']} at {at:.0f}s -> {final.name}")
        made.append(name)
    return made


def approved(name: str) -> dict | None:
    if not APPROVALS.exists():
        return None
    a = (yaml.safe_load(APPROVALS.read_text()) or {}).get(name)
    return a if a and a.get("decision") == "yes" else None


def publish(name: str) -> None:
    """Public or scheduled, Shorts only, and only with Ann's recorded yes."""
    meta = json.loads(meta_path(name).read_text())
    if not meta.get("parent"):
        raise SystemExit("publish-short is for Shorts only; long videos are published by Ann in Studio.")
    ok = approved(name)
    if not ok:
        raise SystemExit(f"No yes from Ann for {name} in {APPROVALS.name}. Nothing changed.")
    rec_path = upload_record(name)
    if not rec_path.exists():
        raise SystemExit(f"Upload the private draft first: python -m pipeline upload {name}")
    rec = json.loads(rec_path.read_text())
    from .youtube import data_api
    yt = data_api()
    parent = json.loads(upload_record(meta["parent"]).read_text())["video_id"]
    pv = yt.videos().list(part="status", id=parent).execute()["items"][0]["status"]
    if pv.get("privacyStatus") != "public" and not pv.get("publishAt"):
        raise SystemExit("The full video is not public or scheduled yet; the Short would link to a private video.")
    status = {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True,
              "embeddable": True}
    when = ok.get("publish_at")
    if when:                      # YouTube schedules only while private, with publishAt set
        status.update(privacyStatus="private", publishAt=str(when))
    yt.videos().update(part="status", body={"id": rec["video_id"], "status": status}).execute()
    rec.update(privacy="scheduled" if when else "public", publish_at=str(when or ""),
               published_by="pipeline on Ann's yes", at=datetime.now().isoformat(timespec="seconds"))
    rec_path.write_text(json.dumps(rec, indent=2))
    print(f"{name}: {'scheduled for ' + str(when) if when else 'public'} - https://youtube.com/shorts/{rec['video_id']}")
