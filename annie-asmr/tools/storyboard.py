"""Storyboards for every video plan: timeline, shots and the still each clip starts from, sounds and voice.

python tools/storyboard.py   -> brand/storyboards.md (and the data the production board shows)
"""
import glob
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.episode import load_episode, shots as ep_shots  # noqa: E402
from pipeline.config import config  # noqa: E402

AV = yaml.safe_load((ROOT / "prompts/avatar.yaml").read_text())
STILLS = AV.get("stills", {})
CANVA = "https://www.canva.com/M/"
# Where each planned sound comes from. bank = cut from Ann's own videos (audio/sfx/bank, list in brand/sound-bank.yaml).
SOUND_SOURCES = {
    "gum-pop-fast-01": "bank: gum (Ann's gum videos)",
    "gum-pop-slow-01": "bank: gum, slowed versions",
    "knuckle-crack-01": "bank: gum-knuckle (Ann's knuckle video)",
    "finger-crack-01": "bank: gum-knuckle, slowed versions",
}


def still_for(shot_id: str, shot: dict) -> str:
    text = (shot.get("action", "") + " " + shot_id).lower()
    if "gum" in text or "pop" in text or "bubble" in text:
        key = "gum"
    elif "knuckle" in text or "finger" in text or "stretch" in text:
        key = "hands"
    elif "gloss" in text:
        key = "gloss"
    else:
        key = "gloss"
    mid = STILLS.get(key) or STILLS.get("gloss")
    return f"{key} still ({CANVA}{mid})" if mid else f"{key} still (to make)"


def sound_names(seg):
    sb = seg.get("sound_bed")
    items = sb if isinstance(sb, list) else [sb] if sb else []
    out = []
    for it in items:
        f = it["file"] if isinstance(it, dict) else it
        name = Path(f).stem
        out.append(f"{name} ({SOUND_SOURCES.get(name, 'to record or source')})")
    return out


def board(slug):
    ep = load_episode(slug)
    shots = ep_shots(ep)
    clip_s = int(config()["generator"].get("clip_seconds", 10))
    t = 0
    lines = [f"## {ep['title']}", f"`{slug}` · {sum(s['minutes'] for s in ep['segments'])} minutes · "
             f"make by {ep.get('made_by') or 'not set'} · publish from {ep.get('publish_after') or 'not set'}", ""]
    rows = []
    for seg in ep["segments"]:
        start = f"{t // 60}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{(t % 3600) // 60:02d}:{t % 60:02d}"
        loops = seg["minutes"] * 60 // clip_s
        lines.append(f"### {start} · {seg['chapter']} ({seg['minutes']} min)")
        for sid in seg["shots"]:
            sh = shots.get(sid, {})
            lines.append(f"- **{sid}**: {sh.get('action', '').strip()}  \n  starts from: {still_for(sid, sh)}")
        lines.append(f"- clips: {len(seg['shots'])} shots x 2 takes of {clip_s}s, cut slowly in turn (about {loops} cuts of footage)")
        for s in sound_names(seg):
            lines.append(f"- sound: {s}")
        for v in seg.get("voice") or []:
            lines.append(f"- voice at +{v['at']}s ({v.get('style', 'whisper')}): \"{v['text']}\"")
        lines.append("")
        rows.append({"chapter": seg["chapter"], "start": start, "minutes": seg["minutes"], "shots": seg["shots"],
                     "sounds": sound_names(seg), "voice": [v["text"] for v in seg.get("voice") or []]})
        t += seg["minutes"] * 60
    return "\n".join(lines), {"slug": slug, "title": ep["title"], "rows": rows}


if __name__ == "__main__":
    parts, data = ["# Annie ASMR storyboards", "",
                   "Presenter: the caramel-skinned character (prompts/avatar.yaml). Every clip starts from one of her stills;",
                   "slow movements, long holds, no fast cuts. Sounds: from the bank where marked, otherwise to record or source.", ""], []
    for f in sorted(glob.glob(str(ROOT / "episodes/*.yaml"))):
        md, d = board(Path(f).stem)
        parts.append(md); data.append(d)
    (ROOT / "brand/storyboards.md").write_text("\n".join(parts))
    (ROOT / "metadata/storyboards.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120))
    print("storyboards for", len(data), "videos")
