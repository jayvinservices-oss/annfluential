"""Make ASMR sounds slower without smearing them: each sound event stays as recorded, the quiet between events
is stretched (room tone is looped into the gaps), and an optional gentle tempo change on top.

Ann, 5 Nov: "it's all too fast, I like my ASMR slow".
python tools/slow_space.py in.wav out.wav [--space 1.8] [--tempo 0.92]
  --space: how much longer the gaps get (1.8 = 80% longer, about 45% fewer sounds per minute)
"""
import argparse
import subprocess

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--space", type=float, default=1.8)
ap.add_argument("--tempo", type=float, default=0.92)
ap.add_argument("--min-gap", type=float, default=0.06, help="seconds; shorter dips count as one event")
a = ap.parse_args()

x, sr = sf.read(a.src, always_2d=True)
mono = x.mean(axis=1)
hop = int(sr * 0.01)
n = len(mono) // hop
env = np.sqrt(np.mean(mono[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
db = 20 * np.log10(env)
floor = np.percentile(db, 20)
active = db > floor + 10                       # 10 dB over the quiet floor = a sound event
# close short dips so one pop/click isn't chopped up
gap_frames = int(a.min_gap / 0.01)
i = 0
while i < n:
    if not active[i]:
        j = i
        while j < n and not active[j]:
            j += 1
        if j - i < gap_frames and i > 0 and j < n:
            active[i:j] = True
        i = j
    else:
        i += 1
quiet = x[np.repeat(~active, hop)[: len(x)]] if (~active).any() else np.zeros((sr, x.shape[1]))
tone = quiet if len(quiet) > sr // 2 else np.zeros((sr, x.shape[1]))
out, pos, t_off = [], 0, 0
i = 0
while i < n:
    j = i
    while j < n and active[j] == active[i]:
        j += 1
    seg = x[i * hop: j * hop]
    if active[i]:
        out.append(seg)
    else:
        extra = int(len(seg) * (a.space - 1))
        fill = np.resize(tone[t_off % max(len(tone) - 1, 1):], (extra, x.shape[1])) if extra > 0 else seg[:0]
        t_off += extra
        out.append(seg)
        if extra > 0:
            ramp = np.linspace(0, 1, min(len(fill), int(sr * 0.01)))[:, None]
            fill[: len(ramp)] *= ramp
            fill[len(fill) - len(ramp):] *= ramp[::-1]
            out.append(fill)
    i = j
y = np.concatenate(out) if out else x
tmp = a.out + ".tmp.wav"
sf.write(tmp, y, sr)
af = f"atempo={a.tempo}" if a.tempo != 1 else "anull"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", af, a.out], check=True)
import os; os.remove(tmp)
print(f"{a.src}: {len(x)/sr:.1f}s -> {len(y)/sr/a.tempo:.1f}s, events {int(np.sum(np.diff(active.astype(int)) == 1))}")
