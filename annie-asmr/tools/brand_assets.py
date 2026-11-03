"""Draft channel artwork from the avatar reference: banner, profile picture, thumbnail template.

python tools/brand_assets.py  -> brand/assets/*.png|jpg  (drafts for Ann's approval, nothing is uploaded)
Fonts: Gloock and Figtree (Google Fonts, OFL). Set BRAND_FONTS to the folder holding Gloock.ttf / Figtree.ttf.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "assets"
FONTS = Path(os.environ.get("BRAND_FONTS", "/home/user/fonts"))
COCOA, CREAM, GLOSS, GOLD, MAUVE = (43, 24, 19), (247, 238, 234), (243, 198, 207), (201, 162, 75), (168, 71, 95)
ref = Image.open(ROOT / "prompts/reference/annie-lips.jpg")  # full three-panel reference from Drive.convert("RGB")
W, H = ref.size
panels = [ref.crop((0, 0, 552, H)), ref.crop((559, 0, 1111, H)), ref.crop((1124, 0, W, H))]


def font(name, size):
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)


def fade(im, side, width):
    """Fade an image edge into cocoa."""
    mask = Image.new("L", im.size, 255)
    d = ImageDraw.Draw(mask)
    for i in range(width):
        a = int(255 * i / width)
        x = i if side == "left" else im.width - 1 - i
        d.line([(x, 0), (x, im.height)], fill=a)
    bg = Image.new("RGB", im.size, COCOA)
    return Image.composite(im, bg, mask)


def spaced(draw, xy, text, f, fill, tracking, anchor_center=True):
    widths = [draw.textlength(c, font=f) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x, y = xy
    if anchor_center:
        x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=f, fill=fill)
        x += w + tracking


def banner():
    # 2560x1440; everything that matters inside the 1546x423 centre safe area.
    b = Image.new("RGB", (2560, 1440), COCOA)
    lips = ImageOps.fit(panels[1], (1100, 1440), centering=(0.5, 0.35))
    lips = fade(fade(lips, "left", 380), "right", 380)
    b.paste(lips, (1460 - 0, 0))
    hands = ImageOps.fit(panels[2], (900, 1440), centering=(0.5, 0.45)).filter(ImageFilter.GaussianBlur(2))
    hands = fade(fade(hands, "left", 300), "right", 300)
    b.paste(Image.blend(hands, Image.new("RGB", hands.size, COCOA), 0.45), (220, 0))
    d = ImageDraw.Draw(b)
    cx = 1080
    d.text((cx, 600), "Annie ASMR", font=font("Gloock", 150), fill=CREAM, anchor="mm")
    spaced(d, (cx, 700), "GUM  ·  GLOSS  ·  NAILS  ·  CRAFTS", font("Figtree", 34), GLOSS, 4)
    d.line([(cx - 90, 772), (cx + 90, 772)], fill=GOLD, width=3)
    d.text((cx, 812), "Long, slow, up-close ASMR for sleep", font=font("Figtree", 34), fill=CREAM, anchor="mm")
    b.save(OUT / "banner-2560x1440.jpg", quality=92)
    # preview with the safe areas marked, for checking only
    p = b.copy(); pd = ImageDraw.Draw(p)
    pd.rectangle([507, 508, 2053, 931], outline=(255, 255, 0), width=4)       # all devices
    pd.rectangle([0, 508, 2559, 931], outline=(0, 200, 255), width=2)        # desktop max
    p.resize((1280, 720)).save(OUT / "banner-preview-safe-area.jpg", quality=85)


def profile():
    p = ImageOps.fit(panels[1], (800, 800), centering=(0.5, 0.42))
    ring = Image.new("RGB", (800, 800), COCOA)
    mask = Image.new("L", (800, 800), 0)
    ImageDraw.Draw(mask).ellipse([28, 28, 772, 772], fill=255)
    ring.paste(p, (0, 0), mask)
    ImageDraw.Draw(ring).ellipse([22, 22, 778, 778], outline=GOLD, width=10)
    ring.save(OUT / "profile-800.png")


def thumbnail(shot, words, out, series):
    t = ImageOps.fit(shot, (1280, 720), centering=(0.5, 0.4))
    # darken the left third for the words
    grad = Image.new("L", (1280, 720), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(700):
        gd.line([(x, 0), (x, 720)], fill=int(200 * (1 - x / 700) ** 1.4))
    t = Image.composite(Image.new("RGB", t.size, COCOA), t, grad)
    d = ImageDraw.Draw(t)
    y = 250
    for w in words:
        d.text((64, y), w, font=font("Gloock", 120), fill=CREAM, stroke_width=2, stroke_fill=COCOA)
        y += 128
    d.rounded_rectangle([64, 610, 64 + d.textlength(series, font=font("Figtree", 30)) + 40, 660], 24, fill=MAUVE)
    d.text((84, 635), series, font=font("Figtree", 30), fill=CREAM, anchor="lm")
    t.save(OUT / out, quality=90)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    banner(); profile()
    thumbnail(ref, ["300", "Layers"], "thumbnail-template-gloss.jpg", "GLOSS LAB")
    thumbnail(panels[2].resize((1104, 1888)), ["Nail", "Taps"], "thumbnail-template-nails.jpg", "NAIL STUDIO")
    print("wrote", sorted(p.name for p in OUT.iterdir()))
