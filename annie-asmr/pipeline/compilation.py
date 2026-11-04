"""Monthly 2-3 hour "for sleep" compilations built from finished renders (no new generation cost).

compilations/<slug>.yaml:
  slug, title, description, tags, sources: [episode slugs, in play order]
python -m pipeline compile <slug>   -> renders/<slug>.mp4, renders/<slug>.timeline.json, metadata/<slug>.json
Upload is the normal private-draft upload: python -m pipeline upload <slug>
Every source must already be rendered AND uploaded (so the description can link back to the full videos).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from .assemble import render_path, timeline_path, write_ffmeta
from .config import METADATA, ROOT, config
from .episode import load_episode, voice_lines
from .ffmpeg_tools import duration, fmt_ts, require_ffmpeg, run
from .metadata import BANNED, meta_path, upload_record

COMPILATIONS = ROOT / "compilations"


def load(slug: str) -> dict:
    p = COMPILATIONS / f"{slug}.yaml"
    if not p.exists():
        raise SystemExit(f"No compilation plan at {p}")
    c = yaml.safe_load(p.read_text())
    c.setdefault("slug", slug)
    if len(c.get("sources") or []) < 2:
        raise SystemExit("a compilation needs at least 2 source videos")
    return c


def compile_video(slug: str) -> Path:
    require_ffmpeg()
    c = load(slug)
    work = ROOT / "renders" / slug / "work"
    work.mkdir(parents=True, exist_ok=True)
    chs, offset, parts, links, has_voice = [], 0.0, [], [], False
    for src in c["sources"]:
        tl = timeline_path(src)
        if not tl.exists():
            raise SystemExit(f"{src} is not rendered yet: python -m pipeline assemble {src}")
        t = json.loads(tl.read_text())
        parts.append(Path(t["render"]))
        ep = load_episode(src)
        has_voice |= bool(voice_lines(ep))
        for ch in t["chapters"]:
            ts = int(round(offset + ch["t"]))
            chs.append({"t": ts, "ts": fmt_ts(ts), "title": ch["title"]})
        up = upload_record(src)
        links.append((ep["title"].split("|")[0].strip(),
                      f"https://youtu.be/{json.loads(up.read_text())['video_id']}" if up.exists() else None))
        offset += float(t["seconds"])
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = work / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    total = duration(joined)
    meta = work / "chapters.ffmeta"
    write_ffmeta(meta, c["title"], chs, total)
    out = render_path(slug)
    run(["ffmpeg", "-y", "-i", joined, "-i", meta, "-map", "0", "-map_metadata", "1", "-map_chapters", "1",
         "-c", "copy", "-movflags", "+faststart", out])
    joined.unlink(missing_ok=True)
    final = duration(out)
    timeline_path(slug).write_text(json.dumps({"slug": slug, "render": str(out), "seconds": round(final, 2),
                                               "length": fmt_ts(final), "chapters": chs,
                                               "sources": c["sources"]}, indent=2))
    write_metadata(c, chs, final, links, has_voice, out)
    print(f"Rendered {out} ({fmt_ts(final)}, {len(chs)} chapters)")
    return out


def write_metadata(c, chs, seconds, links, has_voice, out) -> dict:
    yt = config()["youtube"]
    title = c["title"]
    errors, warnings = [], []
    low = title.lower()
    if len(title) > 100:
        errors.append(f"title is {len(title)} characters; YouTube allows 100")
    for b in BANNED:
        if re.search(rf"\b{re.escape(b)}\b", low):
            errors.append(f"title uses '{b}'")
    if "no talking" in low and has_voice:
        errors.append("title says 'no talking' but a source video has voice lines")
    for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h)\b", low):
        if abs(float(num) * 3600 - seconds) / seconds > 0.15:
            errors.append(f"title claims {num} {unit} but the video is {seconds / 3600:.1f} hours")
    if len(chs) > 100:
        warnings.append("more than 100 chapters; YouTube may not show them all")
    if any(u is None for _, u in links):
        warnings.append("some source videos are not uploaded yet, so the description cannot link to them")
    disc = yt["disclosure"] if has_voice else yt.get("disclosure_no_voice", yt["disclosure"])
    blocks = [c.get("description", "").strip(),
              "Made from these full videos:\n" + "\n".join(f"{t}: {u or 'link after upload'}" for t, u in links),
              "Chapters\n" + "\n".join(f"{ch['ts']} {ch['title']}" for ch in chs),
              " ".join(disc.split()), "#ASMR #ASMRforSleep"]
    description = "\n\n".join(b for b in blocks if b)
    if len(description) > 5000:
        errors.append(f"description is {len(description)} characters; YouTube allows 5000")
    tags, used = [], 0
    for t in list(yt.get("base_tags", [])) + list(c.get("tags") or []):
        cost = len(t) + (2 if " " in t else 0) + 1
        if t.lower() not in [x.lower() for x in tags] and used + cost <= 490:
            tags.append(t)
            used += cost
    meta = {"slug": c["slug"], "file": str(out), "title": title, "description": description, "tags": tags,
            "category_id": yt.get("category_id", "26"), "default_language": yt.get("default_language", "en"),
            "privacy_status": "private", "contains_synthetic_media": True, "made_for_kids": False,
            "publish_after": str(c.get("publish_after", "")), "checks": {"errors": errors, "warnings": warnings}}
    METADATA.mkdir(parents=True, exist_ok=True)
    meta_path(c["slug"]).write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    for e in errors:
        print(f"  ERROR    {e}")
    for w in warnings:
        print(f"  check    {w}")
    return meta
