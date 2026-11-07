"""Make chewing and popping sounds land exactly on the mouth movement of a clip.

  python tools/sync_chews.py oneshots                       cut single pops/chews from the sound bank
  python tools/sync_chews.py sync <clip.mp4> [--kind gum]   -> <clip>.chews.wav, one sound per jaw movement
  python tools/sync_chews.py check <real-video.mp4>         test the detector on a real video: how many
                                                            real pops fall on a detected mouth movement

Best: make clips with a video model that generates its own sound (Veo 3, Kling with audio) and use
--from-audio: the real sounds from the bank then replace the generated ones at exactly the same moments.
Otherwise: the mouth sits in the middle of every lower-face shot, so the movement in that area, frame by
frame, rises each time the jaw moves. Each peak gets one short sound from the bank, a little louder for bigger
movements, never the same sample twice in a row. Slow ASMR pacing: peaks closer than --min-gap are merged.
"""
import argparse
import random
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "audio" / "sfx" / "bank"
ONESHOTS = ROOT / "audio" / "sfx" / "oneshots"
SR = 48000


def mouth_motion(video: Path, fps: int = 30) -> np.ndarray:
    """Per-frame movement in the mouth area (centre of the frame, upper-middle band)."""
    w, h = 160, 90
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    roi = f[:, int(h * .3):int(h * .65), int(w * .3):int(w * .7)]       # lips (best on Ann's real videos)
    m = np.abs(np.diff(roi, axis=0)).mean(axis=(1, 2))
    m = np.convolve(np.concatenate([[0], m]), np.ones(3) / 3, mode="same")
    return m - np.convolve(m, np.ones(31) / 31, mode="same")              # drop slow head and camera sway


def peaks(sig: np.ndarray, fps: int, min_gap: float) -> list[int]:
    thr = np.median(sig) + 0.6 * sig.std()
    gap = max(1, int(min_gap * fps))
    out = []
    for i in range(1, len(sig) - 1):
        if sig[i] >= thr and sig[i] >= sig[i - 1] and sig[i] > sig[i + 1]:
            if out and i - out[-1] < gap:
                if sig[i] > sig[out[-1]]:
                    out[-1] = i
                continue
            out.append(i)
    return out


def load_audio(path: Path, sr: int = SR) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def audio_onsets(x: np.ndarray, sr: int) -> np.ndarray:
    hop = sr // 100
    fr = x[: len(x) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1) + 1e-12))
    rise = np.diff(db, prepend=db[0])
    idx = np.where((rise > 9) & (db > np.percentile(db, 40)))[0]
    keep = [i for n, i in enumerate(idx) if n == 0 or i - idx[n - 1] > 5]
    return np.array(keep) / 100.0


def cmd_oneshots(_):
    n = 0
    for wav in sorted(BANK.glob("*/*.wav")):
        if wav.stem.endswith("-slow"):
            continue
        x = load_audio(wav)
        out = ONESHOTS / wav.parent.name
        out.mkdir(parents=True, exist_ok=True)
        for t in audio_onsets(x, SR)[:40]:
            a, b = int((t - 0.03) * SR), int((t + 0.35) * SR)
            if a < 0 or b > len(x):
                continue
            seg = x[a:b].copy()
            fade = int(0.05 * SR)
            seg[-fade:] *= np.linspace(1, 0, fade)
            seg[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
            if np.abs(seg).max() < 0.02:
                continue
            sf.write(out / f"{wav.stem}-{int(t * 100):05d}.wav", seg, SR)
            n += 1
    print(f"{n} one-shot sounds in {ONESHOTS}")


def cmd_sync(a):
    fps = 30
    sig = mouth_motion(a.clip, fps)
    if a.from_audio:   # the clip's own generated sound marks each chew (Veo 3, Kling with audio): most exact
        on = audio_onsets(load_audio(a.clip, 16000), 16000)
        pk, last_t = [], -9.0
        for t in on:
            if t - last_t >= a.min_gap:
                pk.append(min(len(sig) - 1, int(t * fps))); last_t = t
        sig = np.maximum(sig, 0) + 1
    else:
        pk = peaks(sig, fps, a.min_gap)
    shots = sorted((ONESHOTS / a.kind).glob("*.wav"))
    if not shots:
        raise SystemExit(f"No one-shots for '{a.kind}'. Run: python tools/sync_chews.py oneshots")
    dur = len(sig) / fps
    out = np.zeros(int(dur * SR) + SR, np.float32)
    rnd, last = random.Random(7), None
    top = max(sig[pk]) if pk else 1
    for i in pk:
        choice = rnd.choice([s for s in shots if s != last] or shots)
        last = choice
        s, _ = sf.read(choice, dtype="float32")
        s = s if s.ndim == 1 else s.mean(axis=1)
        gain = 0.5 + 0.5 * float(sig[i] / top)
        at = int((i / fps - a.lead) * SR)
        at = max(at, 0)
        out[at:at + len(s)] += s[: len(out) - at] * gain
    out = out[: int(dur * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.7
    dst = a.clip.with_suffix(".chews.wav")
    sf.write(dst, out, SR)
    print(f"{len(pk)} mouth movements in {dur:.1f}s ({len(pk) / dur * 60:.0f} a minute) -> {dst}")


def cmd_check(a):
    """Share of real pops that land within 150 ms of a detected mouth movement, vs. chance."""
    fps = 30
    sig = mouth_motion(a.video, fps)
    pk = np.array(peaks(sig, fps, a.min_gap)) / fps
    on = audio_onsets(load_audio(a.video, 16000), 16000)
    near = lambda ts: np.mean([np.min(np.abs(pk - t)) < 0.15 for t in ts]) if len(pk) and len(ts) else 0
    rnd = np.random.default_rng(1).uniform(0, len(sig) / fps, len(on))
    print(f"{len(on)} pops, {len(pk)} mouth movements; on a movement: {near(on):.0%} (chance: {near(rnd):.0%})")


p = argparse.ArgumentParser()
sub = p.add_subparsers(required=True)
s = sub.add_parser("oneshots"); s.set_defaults(fn=cmd_oneshots)
s = sub.add_parser("sync"); s.add_argument("clip", type=Path); s.add_argument("--kind", default="gum")
s.add_argument("--min-gap", type=float, default=0.45, help="seconds between sounds at least (slow pacing)")
s.add_argument("--from-audio", action="store_true", help="time sounds from the clip's own generated audio")
s.add_argument("--lead", type=float, default=0.03, help="seconds the sound starts before the peak")
s.set_defaults(fn=cmd_sync)
s = sub.add_parser("check"); s.add_argument("video", type=Path); s.add_argument("--min-gap", type=float, default=0.3)
s.set_defaults(fn=cmd_check)
a = p.parse_args()
a.fn(a)
