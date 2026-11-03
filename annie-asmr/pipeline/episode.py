"""Episode plans (episodes/<slug>.yaml) and the themes they draw from."""
from __future__ import annotations

from pathlib import Path

import yaml

from .config import EPISODES, THEMES, project_path


def load_theme(theme_id: str) -> dict:
    path = THEMES / f"{theme_id}.yaml"
    if not path.exists():
        known = ", ".join(sorted(p.stem for p in THEMES.glob("*.yaml")))
        raise SystemExit(f"Unknown theme '{theme_id}'. Known themes: {known}")
    return yaml.safe_load(path.read_text())


def episode_path(slug: str) -> Path:
    p = Path(slug)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p
    return EPISODES / f"{slug}.yaml"


def load_episode(slug: str) -> dict:
    path = episode_path(slug)
    if not path.exists():
        raise SystemExit(f"No episode plan at {path}. Create one with: python -m pipeline new <theme> <slug>")
    ep = yaml.safe_load(path.read_text())
    ep.setdefault("slug", path.stem)
    ep["_path"] = str(path)
    ep["_theme"] = load_theme(ep["theme"])
    validate(ep)
    return ep


def all_episodes() -> list[dict]:
    out = []
    for p in sorted(EPISODES.glob("*.yaml")):
        data = yaml.safe_load(p.read_text()) or {}
        if "theme" in data:
            data.setdefault("slug", p.stem)
            out.append(data)
    return out


def shots(ep: dict) -> dict:
    """Theme shots, plus or overridden by the episode's own extra_shots."""
    merged = dict(ep["_theme"].get("shots", {}))
    merged.update(ep.get("extra_shots") or {})
    return merged


def used_shot_ids(ep: dict) -> list[str]:
    seen: list[str] = []
    for seg in ep["segments"]:
        for s in seg["shots"]:
            if s not in seen:
                seen.append(s)
    return seen


def sound_layers(seg: dict) -> list[dict]:
    """sound_bed may be a path, a {file, gain_db} dict, or a list of either."""
    bed = seg.get("sound_bed")
    if not bed:
        return []
    items = bed if isinstance(bed, list) else [bed]
    layers = []
    for item in items:
        if isinstance(item, str):
            item = {"file": item}
        layers.append({"file": project_path(item["file"]), "gain_db": float(item.get("gain_db", 0))})
    return layers


def voice_lines(ep: dict) -> list[dict]:
    """Every whispered/spoken line, with a stable id like 'intro-01'."""
    lines = []
    for seg in ep["segments"]:
        for i, line in enumerate(seg.get("voice") or [], start=1):
            lines.append({
                "id": f"{seg['id']}-{i:02d}",
                "segment": seg["id"],
                "at": float(line.get("at", 0)),
                "text": line["text"].strip(),
                "style": line.get("style", "whisper"),  # whisper | soft | brand (the "Annie ASMR" opener)
            })
    return lines


def validate(ep: dict) -> None:
    problems = []
    for key in ("slug", "theme", "title", "segments"):
        if key not in ep:
            problems.append(f"missing '{key}'")
    known = shots(ep) if "_theme" in ep else {}
    ids = set()
    for seg in ep.get("segments", []):
        sid = seg.get("id")
        if not sid:
            problems.append("a segment has no id")
            continue
        if sid in ids:
            problems.append(f"segment id '{sid}' used twice")
        ids.add(sid)
        if not seg.get("chapter"):
            problems.append(f"segment '{sid}' needs a chapter title")
        if float(seg.get("minutes", 0)) <= 0:
            problems.append(f"segment '{sid}' needs minutes > 0")
        for s in seg.get("shots", []):
            if s not in known:
                problems.append(f"segment '{sid}' uses unknown shot '{s}'")
        if not seg.get("shots"):
            problems.append(f"segment '{sid}' has no shots")
    if problems:
        raise SystemExit(f"Episode {ep.get('slug')} has problems:\n  - " + "\n  - ".join(problems))
