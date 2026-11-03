"""Draft new-style thumbnails for existing videos from brand/retitles.yaml (drafts only, nothing uploaded).

python tools/retitle_thumbs.py [source-folder]   (default /home/user/annie-src, where the downloads are)
"""
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_assets import thumbnail  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/annie-src")
OUT = ROOT / "brand" / "assets" / "retitle"
OUT.mkdir(parents=True, exist_ok=True)
for v in yaml.safe_load((ROOT / "brand" / "retitles.yaml").read_text()):
    if not v.get("file") or not (SRC / f"{v['file']}.mp4").exists():
        continue
    src = SRC / f"{v['file']}.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout)
    frame = OUT / f"_{v['file']}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * v['frame'] / 8:.2f}", "-i", str(src), "-frames:v", "1",
                    str(frame)], check=True)
    im = Image.open(frame).convert("RGB")
    s = im.width / 240                       # centres were picked on a 240-pixel-wide contact sheet
    cw, ch = im.width / v["zoom"], im.height / v["zoom"]
    cx = min(max(v["centre"][0] * s, cw / 2), im.width - cw / 2)
    cy = min(max(v["centre"][1] * s, ch / 2), im.height - ch / 2)
    crop = im.crop((round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2)))
    thumbnail(crop, v["words"], f"retitle/{v['file']}.jpg", v["series"])
    frame.unlink()
    print("thumb", v["file"])
