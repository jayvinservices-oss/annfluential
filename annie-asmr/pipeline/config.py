"""Paths, settings and secrets. Secrets only ever come from .env / the environment."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional; plain environment variables also work
    load_dotenv = None

# ANNIE_ROOT lets the tests run against a scratch copy of the project.
ROOT = Path(os.environ.get("ANNIE_ROOT", Path(__file__).resolve().parent.parent))

PROMPTS = ROOT / "prompts"
THEMES = PROMPTS / "themes"
CLIPS = ROOT / "clips"
AUDIO = ROOT / "audio"
SFX = AUDIO / "sfx"
VOICE = AUDIO / "voice"
RENDERS = ROOT / "renders"
METADATA = ROOT / "metadata"
EPISODES = ROOT / "episodes"
REPORTS = ROOT / "reports"

if load_dotenv:
    load_dotenv(ROOT / ".env")


@lru_cache(maxsize=1)
def config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def secret(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(
            f"{name} is not set. Add it to annie-asmr/.env on your Mac (see .env.example). "
            "Do not paste keys into chat."
        )
    return value


def project_path(p: str | Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else ROOT / p
