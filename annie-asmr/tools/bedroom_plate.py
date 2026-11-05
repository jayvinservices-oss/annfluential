"""Empty pink/burgundy bedroom background plates (no people) for compositing behind the presenter stills.
Replicate black-forest-labs/flux-schnell, about $0.003 per image; caps from config apply; logged in metadata/spend.yaml.
python tools/bedroom_plate.py  -> prompts/reference/backgrounds/bedroom-pink-<n>.png
"""
import os, sys, time
from datetime import date, datetime
from pathlib import Path
import requests, yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.config import config  # noqa: E402
from pipeline.providers.router import LEDGER, _ledger, spent_today, spent_usd  # noqa: E402
PRICE = 0.003
PROMPTS = [
    "Photograph of an empty cosy bedroom at night, no people. A neatly made bed with dusty pink and deep burgundy "
    "bedding, velvet cushions, a knitted throw, a warm brass bedside lamp glowing, string fairy lights, a frosted "
    "window with snowy pine trees outside (Canadian winter). Soft warm light, shallow depth of field, background "
    "softly out of focus, photorealistic, 16:9, no text.",
    "Photograph of an empty bedroom corner at night, no people, seen from a chair facing the bed: blush pink walls, "
    "burgundy velvet headboard, pink and wine-red pillows, a small vanity with a round mirror, warm lamp light and "
    "fairy lights, snow falling outside the window. Softly out of focus, photorealistic, 16:9, no text.",
]
r = config()["generator"]["router"]
budget, daily = float(r.get("budget_usd", 20)), float(r.get("daily_usd", 5))
h = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}", "Content-Type": "application/json", "Prefer": "wait"}
out = ROOT / "prompts/reference/backgrounds"; out.mkdir(parents=True, exist_ok=True)
for i, prompt in enumerate(PROMPTS, 1):
    for k in range(2):
        if spent_today() + PRICE > daily or spent_usd() + PRICE > budget:
            raise SystemExit("cap reached")
        p = requests.post("https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions", headers=h,
                          timeout=180, json={"input": {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "png",
                                                       "megapixels": "1", "seed": 100 + k}}).json()
        while p.get("status") not in ("succeeded", "failed", "canceled"):
            time.sleep(2); p = requests.get(p["urls"]["get"], headers=h, timeout=60).json()
        if p["status"] != "succeeded":
            print(i, k, p["status"], p.get("error")); continue
        url = p["output"][0] if isinstance(p["output"], list) else p["output"]
        f = out / f"bedroom-pink-{i}{'ab'[k]}.png"; f.write_bytes(requests.get(url, timeout=120).content)
        LEDGER.write_text(yaml.safe_dump(_ledger() + [{"date": date.today().isoformat(), "time": datetime.now().strftime("%H:%M"),
            "route": "flux-schnell (Replicate)", "clip": f"backgrounds/{f.name}", "seconds": 0, "free": False, "cost_usd": PRICE}], sort_keys=False))
        print("saved", f.name)
