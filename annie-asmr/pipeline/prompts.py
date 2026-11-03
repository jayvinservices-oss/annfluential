"""Builds generator prompts from the locked avatar look + theme + this episode's variation."""
from __future__ import annotations

import yaml

from .config import PROMPTS
from .episode import shots, used_shot_ids


def avatar() -> dict:
    return yaml.safe_load((PROMPTS / "avatar.yaml").read_text())


class _Blank(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def variation_text(ep: dict) -> str:
    template = ep["_theme"].get("variation_template", "")
    return " ".join(template.format_map(_Blank(ep.get("variation") or {})).split())


def build_prompt(ep: dict, shot_id: str) -> tuple[str, str]:
    a = avatar()
    theme = ep["_theme"]
    shot = shots(ep)[shot_id]
    uses_hands = shot.get("uses_hands", theme.get("uses_hands", False))
    parts = [
        a["face"],
        a["hands"] if uses_hands else "",
        theme.get("setting", ""),
        variation_text(ep),
        shot["action"],
        shot.get("camera", a["camera"]),
        a["style"],
    ]
    prompt = " ".join(" ".join(p.split()) for p in parts if p)
    negative = " ".join((a["negative"] + " " + shot.get("negative", "")).split())
    if "{" in prompt:
        raise SystemExit(f"Prompt for shot '{shot_id}' has an unfilled {{placeholder}}: fill 'variation' in the episode plan.")
    return prompt, negative


def prompt_sheet(ep: dict) -> str:
    """Markdown sheet of every prompt in an episode, for review or pasting into a web UI."""
    lines = [f"# Prompts: {ep['slug']}", "", f"Theme: {ep['_theme']['name']}", ""]
    for sid in used_shot_ids(ep):
        prompt, negative = build_prompt(ep, sid)
        lines += [f"## {sid}", "", "Prompt:", "", "```", prompt, "```", "", "Negative:", "", "```", negative, "```", ""]
    return "\n".join(lines)
