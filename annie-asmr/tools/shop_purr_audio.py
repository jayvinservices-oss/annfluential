"""Etsy product audio: Ace's real purring, looped to 60 minutes without an audible repeat pattern.
Rounds of the purring recordings in a different order each round, joined with 4 s crossfades, gentle fade in/out.
python tools/shop_purr_audio.py -> shop/ace-purring/*.mp3 (Etsy: max 20 MB per file, so the hour is 2 x 30 min)
"""
import random, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
ROOT = Path(__file__).resolve().parents[1]
SRC = sorted(p for p in (ROOT / "audio/sfx/bank/cat").glob("ace-purr-*.wav") if "close-mic" not in p.name)
OUT = ROOT / "shop/ace-purring"; OUT.mkdir(parents=True, exist_ok=True)
SR, XF = 48000, 4.0
clips = []
for p in SRC:
    x, sr = sf.read(p, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != SR:
        raise SystemExit(f"{p} is {sr} Hz")
    clips.append(x)
def build(minutes, seed):
    rnd, out, n = random.Random(seed), np.zeros(0, np.float32), int(XF * SR)
    ramp = np.linspace(0, 1, n, dtype=np.float32)
    while len(out) < minutes * 60 * SR:
        order = list(range(len(clips))); rnd.shuffle(order)
        for i in order:
            c = clips[i]
            if len(out) == 0:
                out = c.copy(); continue
            out[-n:] = out[-n:] * (1 - ramp) + c[:n] * ramp
            out = np.concatenate([out, c[n:]])
    out = out[: minutes * 60 * SR]
    f = int(8 * SR); out[:f] *= np.linspace(0, 1, f); out[-f:] *= np.linspace(1, 0, f)
    return out
def mp3(x, name, kbps):
    tmp = OUT / "tmp.wav"; sf.write(tmp, x, SR)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "highpass=f=25,loudnorm=I=-20:TP=-2:LRA=7",
                    "-ac", "1", "-codec:a", "libmp3lame", "-b:a", f"{kbps}k",
                    "-metadata", "title=" + name.replace("-", " "), "-metadata", "artist=Annie ASMR",
                    OUT / f"{name}.mp3"], check=True)
    tmp.unlink()
mp3(build(30, 1), "ace-real-cat-purring-for-sleep-part-1-30min", 64)
mp3(build(30, 2), "ace-real-cat-purring-for-sleep-part-2-30min", 64)
mp3(build(10, 3), "ace-real-cat-purring-10min-nap", 128)
for f in sorted(OUT.glob("*.mp3")):
    print(f.name, f"{f.stat().st_size / 1e6:.1f} MB")
