"""Free-first router: try each route in order, use free credits first, then the cheapest paid route, never past
the budget. Spending is logged in metadata/spend.yaml; `python -m pipeline generate <slug> --dry-run` shows the plan.

config.yaml -> generator.router:
  budget_usd: 20                 # hard stop for all paid generation together
  routes:                        # in order of preference; a route without its key set is skipped
    - {label: ..., provider: fal|replicate|runway, key_env: FAL_KEY, model: ..., price_per_second: 0.0,
       free_seconds: 0, free_period: day|once, ...provider fields}
"""
from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

import yaml

from ..config import METADATA
from .base import Provider

LEDGER = METADATA / "spend.yaml"


def _ledger() -> list[dict]:
    return yaml.safe_load(LEDGER.read_text()) or [] if LEDGER.exists() else []


def spent_usd() -> float:
    return round(sum(e.get("cost_usd", 0) for e in _ledger()), 2)


def free_used(label: str, period: str) -> float:
    today = date.today().isoformat()
    return sum(e["seconds"] for e in _ledger() if e["route"] == label and e.get("free")
               and (period == "once" or e["date"] == today))


class RouterProvider(Provider):
    name = "router"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.budget = float(cfg.get("budget_usd", 20))
        self.routes = [r for r in cfg.get("routes", []) if os.environ.get(r.get("key_env", ""), "").strip()]
        if not self.routes:
            names = ", ".join(r.get("key_env", "?") for r in cfg.get("routes", []))
            raise SystemExit(f"No video service key is set. Add one of these in the environment settings: {names}")

    def choose(self, seconds: int) -> tuple[dict, bool, float]:
        for r in self.routes:                       # 1) free credits, in order
            left = float(r.get("free_seconds", 0)) - free_used(r["label"], r.get("free_period", "day"))
            if left >= seconds:
                return r, True, 0.0
        paid = sorted(self.routes, key=lambda r: float(r.get("price_per_second", 1e9)))
        for r in paid:                              # 2) cheapest paid within budget
            cost = round(float(r["price_per_second"]) * seconds, 3)
            if spent_usd() + cost <= self.budget:
                return r, False, cost
        raise SystemExit(f"Budget reached: ${spent_usd():.2f} of ${self.budget:.2f} spent. Nothing more is generated.")

    def plan(self, clips: int, seconds: int) -> str:
        r, free, cost = self.choose(seconds)
        total = cost * clips if not free else 0
        return (f"{clips} clips x {seconds}s: first via {r['label']} ({'free credits' if free else f'${cost:.2f} each'}); "
                f"if all paid, about ${total:.2f}. Spent so far ${spent_usd():.2f} of ${self.budget:.2f}.")

    def generate(self, *, prompt, negative, image: Path | None, seconds, out):
        from . import get_provider
        r, free, cost = self.choose(seconds)
        inner = get_provider(r["provider"], {r["provider"]: r})
        meta = inner.generate(prompt=prompt, negative=negative, image=image, seconds=seconds, out=out)
        entry = {"date": date.today().isoformat(), "time": datetime.now().strftime("%H:%M"), "route": r["label"],
                 "clip": out.name, "seconds": seconds, "free": free, "cost_usd": 0.0 if free else cost}
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(yaml.safe_dump(_ledger() + [entry], sort_keys=False))
        return {**meta, "route": r["label"], "cost_usd": entry["cost_usd"]}
