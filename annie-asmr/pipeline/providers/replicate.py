"""Any video model hosted on Replicate (Kling, Wan, Hailuo, Veo ...). Field names come from config.yaml."""
from __future__ import annotations

from pathlib import Path

import requests

from ..config import secret
from .base import Provider, data_uri, download, poll

API = "https://api.replicate.com/v1"


class ReplicateProvider(Provider):
    name = "replicate"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        model = cfg.get("model", "")
        if "/" not in model or model.startswith("owner/"):
            raise SystemExit("Set generator.replicate.model in config.yaml to the model you chose, e.g. 'owner/name'.")
        self.model = model
        self.headers = {"Authorization": f"Bearer {secret('REPLICATE_API_TOKEN')}", "Content-Type": "application/json"}

    def generate(self, *, prompt, negative, image: Path | None, seconds, out):
        c = self.cfg
        inp = dict(c.get("extra_input") or {})
        inp[c.get("prompt_field", "prompt")] = prompt
        if c.get("negative_field"):
            inp[c["negative_field"]] = negative
        if c.get("duration_field"):
            inp[c["duration_field"]] = seconds
        if c.get("image_field") and image and image.exists():
            inp[c["image_field"]] = data_uri(image)
        r = requests.post(f"{API}/models/{self.model}/predictions", json={"input": inp},
                          headers=self.headers, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"Replicate refused the request ({r.status_code}): {r.text[:500]}")
        pred = r.json()

        def fetch():
            g = requests.get(pred["urls"]["get"], headers=self.headers, timeout=60)
            g.raise_for_status()
            return g.json()

        result = poll(fetch, done=lambda j: j.get("status") == "succeeded",
                      failed=lambda j: j.get("status") in ("failed", "canceled"))
        output = result["output"]
        url = output[0] if isinstance(output, list) else output
        download(url, out)
        return {"provider": self.name, "model": self.model, "prediction_id": pred["id"]}
