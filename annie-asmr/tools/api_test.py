"""Small paid test of the video route (Ann, 5 Nov): 2 clips x 5 s through the free-first router.

python tools/api_test.py            -> api-test/<shot>.mp4, api-test/report.md, ledger in metadata/spend.yaml
Checks the model's real input fields first and refuses to spend if the image field name is wrong.
"""
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.config import config  # noqa: E402
from pipeline.episode import load_episode  # noqa: E402
from pipeline.generate import still_for_shot  # noqa: E402
from pipeline.prompts import build_prompt  # noqa: E402
from pipeline.providers import get_provider  # noqa: E402
from pipeline.providers.router import spent_today, spent_usd  # noqa: E402

OUT = ROOT / "api-test"
OUT.mkdir(exist_ok=True)
report = ["# Video API test", ""]
gcfg = config()["generator"]
route = gcfg["router"]["routes"][0]
tok = os.environ.get("REPLICATE_API_TOKEN", "").strip()
if not tok:
    raise SystemExit("REPLICATE_API_TOKEN is not set in this session.")
h = {"Authorization": f"Bearer {tok}"}
acct = requests.get("https://api.replicate.com/v1/account", headers=h, timeout=30)
report.append(f"- Account check: HTTP {acct.status_code} ({acct.json().get('username', '?') if acct.ok else acct.text[:200]})")
m = requests.get(f"https://api.replicate.com/v1/models/{route['model']}", headers=h, timeout=30).json()
props = (((m.get("latest_version") or {}).get("openapi_schema") or {}).get("components", {})
         .get("schemas", {}).get("Input", {}).get("properties", {}))
report.append(f"- Model {route['model']}: input fields {', '.join(sorted(props))}")
for k in ("resolution", "num_frames", "frames_per_second", "image"):
    if k in props:
        p = props[k]
        report.append(f"  - {k}: default {p.get('default')!r} {('options ' + str(p.get('enum'))) if p.get('enum') else ''}")
if props and route["image_field"] not in props:
    (OUT / "report.md").write_text("\n".join(report))
    raise SystemExit(f"Image field '{route['image_field']}' is not an input of the model; nothing spent. See api-test/report.md")

ep = load_episode("gum-pops-knuckles-01")
router = get_provider("router", gcfg)
default = ROOT / "prompts/reference/avatar.png"
for shot in ("gum-pop", "knuckle-crack"):
    prompt, negative = build_prompt(ep, shot)
    img = still_for_shot(ep, shot, default)
    out = OUT / f"{shot}.mp4"
    meta = router.generate(prompt=prompt, negative=negative, image=img, seconds=5, out=out)
    pid = meta.get("prediction_id")
    pred = requests.get(f"https://api.replicate.com/v1/predictions/{pid}", headers=h, timeout=30).json() if pid else {}
    report.append(f"- {shot}: from {img.name}, {out.stat().st_size / 1e6:.1f} MB, prediction {pid}, "
                  f"run {pred.get('metrics', {}).get('predict_time', '?')} s, estimated ${meta['cost_usd']:.2f}")
report.append(f"- Spent (ledger estimate): today ${spent_today():.2f}, total ${spent_usd():.2f}. "
              "Check the real charge at replicate.com > Billing.")
(OUT / "report.md").write_text("\n".join(report) + "\n")
print("\n".join(report))
