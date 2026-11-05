"""Step 3: generate clips for every shot in an episode and save them to clips/<slug>/."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import CLIPS, config, project_path
from .episode import used_shot_ids
from .prompts import build_prompt, prompt_sheet
from .providers import get_provider

VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv")


def clip_dir(slug: str) -> Path:
    return CLIPS / slug


def clips_for_shot(slug: str, shot_id: str) -> list[Path]:
    """All kept takes for a shot: files named <shot>__*.ext or <shot>.ext. Rejected takes go in _rejected/."""
    d = clip_dir(slug)
    found = [p for p in d.glob(f"{shot_id}*") if p.suffix.lower() in VIDEO_EXT
             and (p.stem == shot_id or p.stem.startswith(shot_id + "__"))]
    return sorted(found)


def still_for_shot(ep: dict, shot_id: str, default: Path) -> Path:
    """The presenter still a shot starts from: prompts/reference/stills/<gum|hands|gloss>.png when present."""
    from .episode import shots
    text = (shots(ep).get(shot_id, {}).get("action", "") + " " + shot_id).lower()
    key = ("gum" if any(w in text for w in ("gum", "pop", "bubble")) else
           "gloss" if any(w in text for w in ("lips", "gloss", "wand")) else
           "hands" if any(w in text for w in ("knuckle", "finger", "stretch", "nail", "tap", "hands")) else "gloss")
    look = ep.get("look")                 # bedroom (default) | night-mic | pink-glow  (Ann, 5 Nov: rotate all three)
    cands = []
    if look and look != "bedroom":
        base = "gloss" if key == "gloss" else "gum"      # each look has anonymous gum (hands at chin) and gloss stills
        cands.append(f"prompts/reference/stills/{look}/{base}-anon.png")
    cands += [f"prompts/reference/stills/{key}{ext}" for ext in (".png", ".jpg")]
    for c in cands:
        p = project_path(c)
        if p.exists():
            return p
    return default


def generate(ep: dict, *, provider_name: str | None = None, takes: int | None = None,
             only: list[str] | None = None, dry_run: bool = False) -> None:
    gcfg = config()["generator"]
    provider_name = provider_name or gcfg["provider"]
    takes = takes or int(gcfg.get("takes_per_shot", 1))
    seconds = int(gcfg.get("clip_seconds", 10))
    image = project_path(gcfg.get("reference_image", "prompts/reference/avatar.png"))
    d = clip_dir(ep["slug"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "_prompts.md").write_text(prompt_sheet(ep))

    provider = None if dry_run else get_provider(provider_name, gcfg)
    missing = []
    for shot_id in used_shot_ids(ep):
        if only and shot_id not in only:
            continue
        prompt, negative = build_prompt(ep, shot_id)
        shot_image = still_for_shot(ep, shot_id, image)
        for k in range(1, takes + 1):
            out = d / f"{shot_id}__t{k}.mp4"
            if out.exists():
                print(f"  have   {out.name}")
                continue
            if dry_run or not provider.creates_files:
                missing.append(out.name)
                continue
            print(f"  make   {out.name} via {provider.name} ...", flush=True)
            meta = provider.generate(prompt=prompt, negative=negative, image=shot_image, seconds=seconds, out=out)
            meta.update({"shot": shot_id, "take": k, "prompt": prompt, "negative": negative,
                         "created": datetime.now().isoformat(timespec="seconds")})
            out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
            print(f"  saved  {out.name}")

    if dry_run and provider_name == "router" and missing:
        try:
            print("  plan   " + get_provider("router", gcfg).plan(len(missing), seconds))
        except SystemExit as e:
            print(f"  plan   {e}")
    if missing:
        print(f"\n{len(missing)} clip(s) still needed. Prompts are in {d / '_prompts.md'}.")
        print("Make them in your generator's web app and save them with these names:")
        for name in missing:
            print(f"  clips/{ep['slug']}/{name}")
    print("\nWatch every take. Move any you do not want into a _rejected/ folder before assembling.")
