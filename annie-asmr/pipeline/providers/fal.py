"""Any video model on fal.ai (queue API). Field names come from the route in config.yaml."""
from __future__ import annotations

from pathlib import Path

import requests

from ..config import secret
from .base import Provider, data_uri, download, poll


class FalProvider(Provider):
    name = "fal"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.model = cfg["model"]
        self.headers = {"Authorization": f"Key {secret(cfg.get('key_env', 'FAL_KEY'))}", "Content-Type": "application/json"}

    def generate(self, *, prompt, negative, image: Path | None, seconds, out):
        c = self.cfg
        inp = dict(c.get("extra_input") or {})
        inp[c.get("prompt_field", "prompt")] = prompt
        if c.get("negative_field"):
            inp[c["negative_field"]] = negative
        if c.get("duration_field"):
            inp[c["duration_field"]] = str(seconds) if c.get("duration_as_text") else seconds
        if c.get("image_field") and image and image.exists():
            inp[c["image_field"]] = data_uri(image)
        r = requests.post(f"https://queue.fal.run/{self.model}", json=inp, headers=self.headers, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"fal refused the request ({r.status_code}): {r.text[:500]}")
        job = r.json()

        def fetch():
            g = requests.get(job["status_url"], headers=self.headers, timeout=60)
            g.raise_for_status()
            return g.json()

        poll(fetch, done=lambda j: j.get("status") == "COMPLETED", failed=lambda j: j.get("status") in ("FAILED", "ERROR"))
        res = requests.get(job["response_url"], headers=self.headers, timeout=60).json()
        video = res.get("video") or (res.get("videos") or [{}])[0]
        download(video["url"], out)
        return {"provider": self.name, "model": self.model, "request_id": job.get("request_id")}
