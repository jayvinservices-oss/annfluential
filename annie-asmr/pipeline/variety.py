"""Checks that a new episode is not a near copy of an earlier one (brief: vary each video)."""
from __future__ import annotations

import random

from .episode import all_episodes, load_theme


def fingerprint(ep: dict) -> set[str]:
    items = {f"theme:{ep['theme']}"}
    for k, v in (ep.get("variation") or {}).items():
        items.add(f"{k}:{str(v).lower()}")
    for o in ep.get("objects") or []:
        items.add(f"object:{o.lower()}")
    for s in ep.get("sounds") or []:
        items.add(f"sound:{s.lower()}")
    for seg in ep.get("segments") or []:
        items.add("chapter:" + str(seg.get("chapter", "")).lower())
        for layer in (seg.get("sound_bed") if isinstance(seg.get("sound_bed"), list) else [seg.get("sound_bed")]):
            if layer:
                items.add("bed:" + str(layer["file"] if isinstance(layer, dict) else layer).lower())
    return items


def similarity(a: dict, b: dict) -> float:
    fa, fb = fingerprint(a), fingerprint(b)
    return len(fa & fb) / max(1, len(fa | fb))


def check(ep: dict, warn_at: float = 0.6, block_at: float = 0.85) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings) comparing this episode with every other plan."""
    errors, warnings = [], []
    for other in all_episodes():
        if other["slug"] == ep["slug"]:
            continue
        s = similarity(ep, other)
        if s >= block_at:
            errors.append(f"{s:.0%} the same as '{other['slug']}': change objects, sounds or variation")
        elif s >= warn_at:
            warnings.append(f"{s:.0%} similar to '{other['slug']}'")
        if other["theme"] == ep["theme"] and (other.get("variation") or {}) == (ep.get("variation") or {}):
            errors.append(f"same theme and identical variation as '{other['slug']}'")
        if other.get("title", "").strip().lower() == ep.get("title", "").strip().lower():
            errors.append(f"same title as '{other['slug']}'")
    return errors, warnings


def pick_fresh_variation(theme_id: str, seed: int | None = None) -> dict:
    """Choose a variation for a theme that no existing episode of that theme has used."""
    theme = load_theme(theme_id)
    pools = theme.get("variation_pools") or {}
    used = [tuple(sorted((e.get("variation") or {}).items())) for e in all_episodes() if e["theme"] == theme_id]
    rng = random.Random(seed)
    for _ in range(200):
        choice = {k: rng.choice(v) for k, v in pools.items()}
        if tuple(sorted(choice.items())) not in used:
            return choice
    return {k: rng.choice(v) for k, v in pools.items()}
