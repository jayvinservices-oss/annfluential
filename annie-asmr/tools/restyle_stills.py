"""Swap the backdrop of the presenter stills for a pink/burgundy bedroom, keeping the person unchanged.

Replicate black-forest-labs/flux-kontext-pro (about $0.04 per image). Logged in metadata/spend.yaml, and the router's
$5/day and $20 total caps apply. python tools/restyle_stills.py [still ...]  -> prompts/reference/stills/bedroom/
"""
import base64
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.config import config  # noqa: E402
from pipeline.providers.router import LEDGER, _ledger, spent_today, spent_usd  # noqa: E402

MODEL = "black-forest-labs/flux-kontext-pro"
PRICE = 0.04
PROMPT = ("Keep the woman exactly the same: same face, lips, skin tone, curly hair, earrings, hands, nails, clothing, "
          "pose and framing. Replace only the dark background with a softly blurred cosy bedroom at night: a bed "
          "with pink and burgundy bedding and pillows, a warm bedside lamp, string fairy lights, a frosted winter "
          "window. Warm, soft, shallow depth of field, photorealistic, no text.")
r = config()["generator"]["router"]
budget, daily = float(r.get("budget_usd", 20)), float(r.get("daily_usd", 5))
tok = os.environ["REPLICATE_API_TOKEN"]
h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "Prefer": "wait"}
out_dir = ROOT / "prompts/reference/stills/bedroom"
out_dir.mkdir(parents=True, exist_ok=True)
names = sys.argv[1:] or ["gum", "gloss"]
for name in names:
    if spent_today() + PRICE > daily or spent_usd() + PRICE > budget:
        raise SystemExit(f"Cap reached (today ${spent_today():.2f}/{daily}, total ${spent_usd():.2f}/{budget}).")
    src = ROOT / f"prompts/reference/stills/{name}.png"
    img = "data:image/png;base64," + base64.b64encode(src.read_bytes()).decode()
    p = requests.post(f"https://api.replicate.com/v1/models/{MODEL}/predictions", headers=h, timeout=180,
                      json={"input": {"prompt": PROMPT, "input_image": img, "aspect_ratio": "match_input_image",
                                      "output_format": "png", "safety_tolerance": 2}}).json()
    if "urls" not in p:
        print("Replicate did not start it (probably a rate limit):", str(p)[:300]); time.sleep(15); continue
    while p.get("status") not in ("succeeded", "failed", "canceled"):
        time.sleep(3)
        p = requests.get(p["urls"]["get"], headers=h, timeout=60).json()
    if p["status"] != "succeeded":
        print(f"{name}: {p['status']} {p.get('error')}")
        continue
    url = p["output"][0] if isinstance(p["output"], list) else p["output"]
    out = out_dir / f"{name}.png"
    out.write_bytes(requests.get(url, timeout=120).content)
    LEDGER.write_text(yaml.safe_dump(_ledger() + [{"date": date.today().isoformat(), "time": datetime.now().strftime("%H:%M"),
                      "route": "flux-kontext-pro (Replicate)", "clip": f"stills/bedroom/{name}.png", "seconds": 0,
                      "free": False, "cost_usd": PRICE}], sort_keys=False))
    time.sleep(10)
    print(f"{name}: saved {out.relative_to(ROOT)} (${PRICE:.2f}); today ${spent_today():.2f}")
