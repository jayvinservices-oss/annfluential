"""Video generator adapters. Pick one in config.yaml -> generator.provider."""
from __future__ import annotations

from .base import Provider


def get_provider(name: str, cfg: dict) -> Provider:
    if name == "runway":
        from .runway import RunwayProvider
        return RunwayProvider(cfg.get("runway", {}))
    if name == "replicate":
        from .replicate import ReplicateProvider
        return ReplicateProvider(cfg.get("replicate", {}))
    if name == "router":
        from .router import RouterProvider
        return RouterProvider(cfg.get("router", {}))
    if name == "fal":
        from .fal import FalProvider
        return FalProvider(cfg.get("fal", {}))
    if name == "manual":
        from .manual import ManualProvider
        return ManualProvider(cfg)
    raise SystemExit(f"Unknown generator provider '{name}'. Use router, fal, runway, replicate or manual.")
