"""Etsy listing images for the purring product (2000 x 1600, brand colours and fonts)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "shop/ace-purring"; F = "/home/user/fonts"
W, H = 2000, 1600
COCOA, CREAM, PINK, MAUVE = (0x2B, 0x18, 0x13), (0xF7, 0xEE, 0xEA), (0xF3, 0xC6, 0xCF), (0xA8, 0x47, 0x5F)
def font(n, s): return ImageFont.truetype(f"{F}/{n}.ttf", s)
def bg(src):
    im = Image.open(src).convert("RGB"); r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    return im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
def shade(im, frac=0.55, top=False):
    m = Image.new("L", (W, H)); d = ImageDraw.Draw(m)
    for y in range(H):
        t = (1 - y / (H * frac)) if top else (y - H * (1 - frac)) / (H * frac)
        d.line([(0, y), (W, y)], fill=int(max(0, min(1, t)) ** 1.2 * 235))
    return Image.composite(Image.new("RGB", (W, H), COCOA), im, m)
def pill(d, x, y, text, size=56):
    f = font("Figtree", size); tw = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + tw + 70, y + size + 40), radius=(size + 40) // 2, fill=MAUVE)
    d.text((x + 35, y + 16), text, font=f, fill=CREAM)
A = ROOT / "prompts/reference/ace/bedroom"
# 1 cover
im = shade(bg(A / "ace-face-closeup.png")); d = ImageDraw.Draw(im)
pill(d, 110, 860, "1 HOUR  ·  INSTANT DOWNLOAD")
d.text((105, 980), "Real Cat Purring", font=font("Gloock", 168), fill=CREAM)
d.text((105, 1170), "for Sleep", font=font("Gloock", 168), fill=CREAM)
d.text((112, 1400), "Ace's real purr  ·  no music  ·  no talking  ·  MP3", font=font("Figtree", 58), fill=PINK)
im.save(OUT / "listing-1-cover.jpg", quality=92)
# 2 what's included
im = shade(bg(A / "ace-sleeping-loaf.png"), 0.75, top=True); d = ImageDraw.Draw(im)
d.text((110, 110), "What's included", font=font("Gloock", 140), fill=CREAM)
items = ["Part 1 · 30 min real cat purring (MP3)", "Part 2 · 30 min real cat purring (MP3)",
         "Bonus · 10 min nap version (high quality MP3)", "Recorded from Ace, a real tuxedo cat",
         "No music, no talking, no ads"]
for i, t in enumerate(items):
    d.ellipse((120, 345 + i * 120, 150, 375 + i * 120), fill=PINK)
    d.text((190, 330 + i * 120), t, font=font("Figtree", 64), fill=CREAM)
im.save(OUT / "listing-2-included.jpg", quality=92)
# 3 how to use
im = Image.new("RGB", (W, H), COCOA); d = ImageDraw.Draw(im)
side = bg(A / "ace-lying-on-blanket.png").crop((900, 0, 2000, 1600)).filter(ImageFilter.GaussianBlur(1))
im.paste(side, (900, 0))
grad = Image.new("L", (W, H)); g = ImageDraw.Draw(grad)
for x in range(900, 1300): g.line([(x, 0), (x, H)], fill=int(255 * (1 - (x - 900) / 400)))
im = Image.composite(Image.new("RGB", (W, H), COCOA), im, grad); d = ImageDraw.Draw(im)
d.text((110, 140), "Use it for", font=font("Gloock", 140), fill=CREAM)
for i, t in enumerate(["Falling asleep", "Calm & focus", "Restless pets & little ones", "Missing your cat",
                       "Naps & meditation"]):
    d.text((120, 380 + i * 140), "·  " + t, font=font("Figtree", 72), fill=PINK if i % 2 else CREAM)
d.text((120, 1420), "Loop it on any phone, speaker or sleep app.", font=font("Figtree", 50), fill=CREAM)
im.save(OUT / "listing-3-uses.jpg", quality=92)
print("ok")
