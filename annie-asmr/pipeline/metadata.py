"""Step 6: honest titles, descriptions, chapters, tags and the synthetic-content flag -> metadata/<slug>.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .assemble import timeline_path
from .config import METADATA, RENDERS, config
from .episode import shots, voice_lines
from .variety import check as variety_check

# Words that describe ASMR generally rather than a claim about this video's contents.
GENERIC = set("""
asmr a an and the with of for to in on my me your you i at by from up until no not soft softly gentle
relaxing relax relaxation sleep sleepy tingles tingly tingle whisper whispers whispered whispering sounds
sound triggers trigger cosy cozy calm close up closeup ear to ear minutes minute min mins hour hours hr
hrs layers layer long nails nail video part edition festive christmas holiday xmas sounds & | - + ! ? ,
satisfying slow slowly chill night tonight today new let's lets do it we time with me chat chit spoken
""".split())

BANNED = ["roleplay", "role play", "rp", "girlfriend", "boyfriend", "date night", "kiss", "kisses",
          "flirt", "flirty", "requests", "request", "taking requests", "real woman", "not ai", "no ai", "100% real"]


def meta_path(slug: str, short: bool = False) -> Path:
    return METADATA / f"{slug}{'-short' if short else ''}.json"


def upload_record(slug: str, short: bool = False) -> Path:
    return METADATA / f"{slug}{'-short' if short else ''}.upload.json"


def _corpus(ep: dict) -> str:
    parts = [ep["_theme"].get("name", ""), ep["_theme"].get("setting", ""), " ".join(ep.get("objects") or []),
             " ".join(ep.get("sounds") or []), " ".join(map(str, (ep.get("variation") or {}).values())),
             ep.get("description", ""), " ".join(ep.get("title_terms_ok") or [])]
    for seg in ep["segments"]:
        parts.append(seg["chapter"])
        parts += [shots(ep)[s]["action"] for s in seg["shots"]]
    parts += [l["text"] for l in voice_lines(ep)]
    return " ".join(parts).lower()


def _stem(w: str) -> str:
    for suf in ("ing", "es", "s", "ed"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def check_title(ep: dict, seconds: float | None) -> tuple[list[str], list[str]]:
    title = ep["title"]
    low = title.lower()
    errors, warnings = [], []
    if "todo" in low:
        errors.append("title still says TODO")
    if "TODO" in ep.get("description", "") or any("TODO" in l["text"] for l in voice_lines(ep)):
        errors.append("description or a voice line still says TODO")
    if len(title) > 100:
        errors.append(f"title is {len(title)} characters; YouTube allows 100")
    if "<" in title or ">" in title:
        errors.append("title cannot contain < or >")
    for b in BANNED:
        if re.search(rf"\b{re.escape(b)}\b", low):
            errors.append(f"title uses '{b}', which breaks the channel rules or misleads")
    has_voice = bool(voice_lines(ep))
    if "no talking" in low and has_voice:
        errors.append("title says 'no talking' but the plan has voice lines")
    if re.search(r"\bwhisper", low) and not has_voice:
        errors.append("title mentions whispers but there are no voice lines")
    if seconds:
        for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?|min)\b", low):
            claimed = float(num) * (3600 if unit.startswith("h") else 60)
            if abs(claimed - seconds) / seconds > 0.15:
                errors.append(f"title claims {num} {unit} but the video is {seconds / 60:.0f} minutes")
    corpus = _corpus(ep)
    for word in re.findall(r"[a-z']+", low):
        if word in GENERIC or len(word) < 3:
            continue
        if _stem(word) not in corpus:
            warnings.append(f"title word '{word}' does not appear in the plan: check it is really in the video "
                            "(or add it to title_terms_ok)")
    for n in re.findall(r"\b(\d{2,})\b", title):
        if not re.search(r"(hour|hr|min)", low[low.find(n):low.find(n) + 12]):
            warnings.append(f"title says '{n}': make sure the video really shows it (e.g. you counted {n} layers)")
    return errors, warnings


def _words(text: str) -> set[str]:
    return {_stem(w) for w in re.findall(r"[a-z']+", text.lower()) if w not in GENERIC and len(w) > 2}


def check_opening(ep: dict) -> list[str]:
    """The first seconds decide whether viewers stay: open on the promised trigger, no talking yet."""
    quiet = float((config().get("opening") or {}).get("quiet_seconds", 30))
    first = ep["segments"][0]
    warnings = []
    for line in voice_lines(ep):
        if line["segment"] == first["id"] and line["at"] < quiet and line["style"] != "brand":
            warnings.append(f"opening: voice line {line['id']} starts at {line['at']:.0f}s; only the whispered "
                            f"'Annie ASMR' brand line (style: brand) belongs in the first {quiet:.0f} seconds")
    if not _words(first["chapter"]) & _words(ep["title"]):
        warnings.append(f"opening: first chapter '{first['chapter']}' does not name a trigger from the title; "
                        "open on the trigger the title and thumbnail promise")
    if not first.get("sound_bed"):
        warnings.append("opening: first chapter has no sound bed, so the video opens silent")
    return warnings


def build(ep: dict) -> dict:
    cfg = config()
    yt = cfg["youtube"]
    tl_file = timeline_path(ep["slug"])
    timeline = json.loads(tl_file.read_text()) if tl_file.exists() else None
    seconds = timeline["seconds"] if timeline else None

    chapter_lines = [f"{c['ts']} {c['title']}" for c in timeline["chapters"]] if timeline else \
        ["(chapters are added after: python -m pipeline assemble " + ep["slug"] + ")"]
    objects = ", ".join(ep.get("objects") or [])
    sounds = ", ".join(ep.get("sounds") or [])
    blocks = [ep.get("description", "").strip()]
    if objects:
        blocks.append(f"In this video: {objects}.")
    if sounds:
        blocks.append(f"Sounds: {sounds}.")
    blocks.append("Chapters\n" + "\n".join(chapter_lines))
    disc = yt["disclosure"] if voice_lines(ep) else yt.get("disclosure_no_voice", yt["disclosure"])
    blocks.append(" ".join(disc.split()))
    hashtags = ep.get("hashtags") or ["#ASMR", "#ASMRbeauty"]
    blocks.append(" ".join(hashtags[:3]))
    description = "\n\n".join(b for b in blocks if b)

    tags, used = [], 0
    for t in list(yt.get("base_tags", [])) + list(ep.get("tags") or []):
        cost = len(t) + (2 if " " in t else 0) + 1
        if t.lower() not in [x.lower() for x in tags] and used + cost <= 490:
            tags.append(t)
            used += cost

    errors, warnings = check_title(ep, seconds)
    warnings += check_opening(ep)
    v_err, v_warn = variety_check(ep)
    errors += v_err
    warnings += v_warn
    if len(description) > 5000:
        errors.append(f"description is {len(description)} characters; YouTube allows 5000")
    if "<" in description or ">" in description:
        errors.append("description cannot contain < or >")
    if not timeline:
        warnings.append("not rendered yet, so no chapters or length check")
    else:
        warnings += [f"chapters: {p}" for p in timeline.get("chapter_problems", [])]

    meta = {
        "slug": ep["slug"],
        "file": timeline["render"] if timeline else None,
        "title": ep["title"],
        "description": description,
        "tags": tags,
        "category_id": yt.get("category_id", "26"),
        "default_language": yt.get("default_language", "en"),
        "privacy_status": "private",          # always: you publish by hand in Studio
        "contains_synthetic_media": True,     # the "altered or synthetic content" box
        "made_for_kids": False,
        "publish_after": str(ep.get("publish_after", "")),
        "checks": {"errors": errors, "warnings": warnings},
    }
    METADATA.mkdir(parents=True, exist_ok=True)
    meta_path(ep["slug"]).write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


def build_short(ep: dict) -> dict:
    yt = config()["youtube"]
    long_up = upload_record(ep["slug"])
    link = "LINK_TO_FULL_VIDEO"
    if long_up.exists():
        link = f"https://youtu.be/{json.loads(long_up.read_text())['video_id']}"
    title = ep.get("short_title") or (ep["title"].split("|")[0].strip() + " (trailer)")
    meta = {
        "slug": ep["slug"] + "-short",
        "file": str(RENDERS / f"{ep['slug']}-short.mp4"),
        "title": title[:100],
        "description": f"Short trailer. The full video is here: {link}\n\n{' '.join(yt['disclosure'].split())}\n\n#ASMR #Shorts",
        "tags": list(yt.get("base_tags", []))[:5],
        "category_id": yt.get("category_id", "26"),
        "default_language": yt.get("default_language", "en"),
        "privacy_status": "private",
        "contains_synthetic_media": True,
        "made_for_kids": False,
        "checks": {"errors": ["upload the long video first so the trailer can link to it"] if "LINK_TO" in link else [],
                   "warnings": []},
    }
    meta_path(ep["slug"], short=True).write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


def print_checks(meta: dict) -> bool:
    c = meta["checks"]
    for e in c["errors"]:
        print(f"  ERROR    {e}")
    for w in c["warnings"]:
        print(f"  check    {w}")
    if not c["errors"] and not c["warnings"]:
        print("  all checks passed")
    return not c["errors"]
