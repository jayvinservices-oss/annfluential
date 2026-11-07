"""Ace's real photos, moved into the cosy bedroom with his look kept exactly (FLUX Kontext, about $0.04 each).
python tools/ace_stills.py [bedroom|fireplace|rainy-window|christmas-tree|snowy-cabin] -> prompts/reference/ace/<location>/<name>.png ; caps from config; logged in metadata/spend.yaml
"""
import base64, os, sys, time
from datetime import date, datetime
from pathlib import Path
import requests, yaml
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from pipeline.config import config  # noqa: E402
from pipeline.providers.router import LEDGER, _ledger, spent_today, spent_usd  # noqa: E402
PRICE = 0.04
KEEP = ("Keep this exact cat completely unchanged: same face, white nose blaze, white muzzle, pink nose, pale green "
        "eyes, white bib, white paws, short glossy black coat, same pose and size in frame. ")
LOCATIONS = {
  "bedroom": None,   # the original JOBS below
  "fireplace": "a cosy living room at night beside a glowing fireplace, a cream knitted blanket on a sofa, warm firelight, softly blurred background",
  "rainy-window": "a deep window seat at night with rain running down the glass, a soft pink cushion, city lights blurred outside, warm lamp glow",
  "christmas-tree": "under a decorated Christmas tree at night, a red velvet tree skirt, glowing warm fairy lights and wrapped gifts softly blurred around him",
  "snowy-cabin": "a wooden cabin window sill at night with heavy snow falling outside, a chunky grey knit blanket, candle glow, softly blurred background",
}
JOBS = {
  "ace-lying-on-blanket": KEEP + "Move him onto a bed with a dusty pink knit blanket and burgundy velvet pillows in a "
      "cosy bedroom at night, warm bedside lamp glow, golden fairy-light bokeh, softly blurred background. Photorealistic, no text.",
  "ace-face-closeup": KEEP + "Replace the background with a cosy bedroom at night: burgundy and pink bedding softly "
      "blurred behind him, warm lamp glow, golden fairy-light bokeh. Photorealistic, no text.",
  "ace-sleeping-loaf": KEEP + "Place him on a bed with burgundy velvet throw and pink pillows in a cosy dark bedroom at "
      "night, a frosted window with snow falling softly behind, warm lamp glow. Photorealistic, no text.",
}
loc = sys.argv[1] if len(sys.argv) > 1 else "bedroom"
if loc != "bedroom":
    scene = LOCATIONS[loc]
    JOBS = {n: KEEP + f"Place him, in the same pose, in {scene}. Photorealistic, no text." for n in JOBS}
r = config()["generator"]["router"]
h = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}", "Content-Type": "application/json", "Prefer": "wait"}
out = ROOT / "prompts/reference/ace" / loc; out.mkdir(parents=True, exist_ok=True)
for name, prompt in JOBS.items():
    if spent_today() + PRICE > float(r.get("daily_usd", 5)) or spent_usd() + PRICE > float(r.get("budget_usd", 20)):
        sys.exit("cap reached")
    src = next((ROOT / "prompts/reference/ace").glob(f"{name}*.jpg"))
    img = "data:image/jpeg;base64," + base64.b64encode(src.read_bytes()).decode()
    p = requests.post("https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions", headers=h,
                      timeout=180, json={"input": {"prompt": prompt, "input_image": img, "aspect_ratio": "16:9",
                                                   "output_format": "png", "safety_tolerance": 2}}).json()
    if "urls" not in p:
        print(name, "not started:", str(p)[:200]); time.sleep(15); continue
    while p.get("status") not in ("succeeded", "failed", "canceled"):
        time.sleep(3); p = requests.get(p["urls"]["get"], headers=h, timeout=60).json()
    if p["status"] != "succeeded":
        print(name, p["status"], p.get("error")); continue
    url = p["output"][0] if isinstance(p["output"], list) else p["output"]
    f = out / f"{name}.png"; f.write_bytes(requests.get(url, timeout=120).content)
    LEDGER.write_text(yaml.safe_dump(_ledger() + [{"date": date.today().isoformat(), "time": datetime.now().strftime("%H:%M"),
        "route": "flux-kontext-pro (Replicate)", "clip": f"ace/{loc}/{f.name}", "seconds": 0, "free": False, "cost_usd": PRICE}], sort_keys=False))
    print("saved", f.relative_to(ROOT), f"today ${spent_today():.2f}"); time.sleep(10)
