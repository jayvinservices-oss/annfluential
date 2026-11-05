"""Thumbnail per the style guide: real frame, left side shaded to cocoa, 1-3 Gloock words (cream, left, bottom half),
mauve pill (e.g. "No Talking"). python tools/thumbnail.py frame.png out.jpg "Slow|Chews" --pill "No Talking" [--sub "60 MIN"]
'|' splits lines. Fonts: /home/user/fonts/Gloock.ttf, Figtree.ttf (or $BRAND_FONTS).
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont
F = os.environ.get("BRAND_FONTS") or "/home/user/fonts"
ap = argparse.ArgumentParser(); ap.add_argument("frame"); ap.add_argument("out"); ap.add_argument("words")
ap.add_argument("--pill", default="No Talking"); ap.add_argument("--sub", default="")
a = ap.parse_args()
W, H = 1280, 720
im = Image.open(a.frame).convert("RGB")
r = max(W / im.width, H / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
shade = Image.new("L", (W, H), 0); d = ImageDraw.Draw(shade)
for x in range(W):                               # cocoa fade from the left 60%
    d.line([(x, 0), (x, H)], fill=int(max(0, 1 - x / (W * 0.6)) ** 1.3 * 225))
im = Image.composite(Image.new("RGB", (W, H), (0x2B, 0x18, 0x13)), im, shade)
d = ImageDraw.Draw(im)
lines = a.words.split("|")
size = 150 if max(len(l) for l in lines) <= 6 else 118
g = ImageFont.truetype(f"{F}/Gloock.ttf", size); fig = ImageFont.truetype(f"{F}/Figtree.ttf", 40)
y = H - 70 - len(lines) * int(size * 1.02)
for l in lines:
    d.text((58, y), l, font=g, fill=(0xF7, 0xEE, 0xEA)); y += int(size * 1.02)
if a.pill:
    tw = d.textlength(a.pill, font=fig); x0, y0 = 60, H - 70 - len(lines) * int(size * 1.02) - 78
    d.rounded_rectangle((x0, y0, x0 + tw + 44, y0 + 60), radius=30, fill=(0xA8, 0x47, 0x5F))
    d.text((x0 + 22, y0 + 7), a.pill, font=fig, fill=(0xF7, 0xEE, 0xEA))
if a.sub:
    d.text((60, H - 62), a.sub, font=ImageFont.truetype(f"{F}/Figtree.ttf", 34), fill=(0xF3, 0xC6, 0xCF))
im.save(a.out, quality=92); print(a.out)
