"""Runway image-to-video. Check model names and fields against https://docs.dev.runwayml.com before first use."""
from __future__ import annotations

from pathlib import Path

import requests

from ..config import secret
from .base import Provider, data_uri, download, poll


class RunwayProvider(Provider):
    name = "runway"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.base = cfg.get("endpoint", "https://api.dev.runwayml.com/v1").rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {secret('RUNWAY_API_KEY')}",
            "X-Runway-Version": cfg.get("api_version", "2024-11-06"),
            "Content-Type": "application/json",
        }

    def generate(self, *, prompt, negative, image: Path | None, seconds, out):
        if not image or not image.exists():
            raise SystemExit("Runway image-to-video needs the reference image at prompts/reference/avatar.png")
        # Runway has no negative prompt field; the avatar prompt already states what to avoid.
        body = {
            "model": self.cfg.get("model", "gen4_turbo"),
            "promptImage": data_uri(image),
            "promptText": prompt[:1000],
            "ratio": self.cfg.get("ratio", "1280:720"),
            "duration": 10 if seconds >= 10 else 5,
        }
        r = requests.post(f"{self.base}/image_to_video", json=body, headers=self.headers, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"Runway refused the request ({r.status_code}): {r.text[:500]}")
        task_id = r.json()["id"]

        def fetch():
            t = requests.get(f"{self.base}/tasks/{task_id}", headers=self.headers, timeout=60)
            t.raise_for_status()
            return t.json()

        result = poll(fetch, done=lambda j: j.get("status") == "SUCCEEDED",
                      failed=lambda j: j.get("status") in ("FAILED", "CANCELLED"))
        download(result["output"][0], out)
        return {"provider": self.name, "task_id": task_id, "model": body["model"], "duration": body["duration"]}
