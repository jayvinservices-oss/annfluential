"""Build a sound bank from Ann's own videos: talking-free stretches with the most pops/cracks/crunches.

Run in the voice environment (needs torch + silero-vad):
  /home/user/voice-env/bin/python tools/sound_bank.py [source-folder]
-> audio/sfx/bank/<category>/<source>-<mm-ss>.wav (+ a -slow version at 85% tempo, same pitch)
-> audio/sfx/bank/bank.yaml (where every clip came from) and audio/sfx/bank/_listen.mp3 (a preview of all)
Listen before use: the detector skips talking, but not every other noise.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml
from silero_vad import get_speech_timestamps, load_silero_vad

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/annie-src")
BANK = ROOT / "audio" / "sfx" / "bank"
SOURCES = {  # video -> category; videos with singing, shushing or flirting are left out
    "gum-popping-crackling": "gum", "gum-with-friend": "gum", "woman-crackling-gum": "gum",
    "gum-knuckle": "gum-knuckle", "cucumber": "crunch", "lollipop": "lollipop",
    "mouth-sounds-fast": "mouth-sounds",
}
SR, CLIP, PER_VIDEO = 16000, 30, 4   # analysis rate, clip seconds, clips kept per video


def load(path: Path, sr: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def transient_score(x: np.ndarray, sr: int) -> np.ndarray:
    """Per-second count of sharp onsets (pops, cracks, crunches)."""
    hop = sr // 100
    frames = x[: len(x) // hop * hop].reshape(-1, hop)
    env = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(env)
    rise = np.diff(db, prepend=db[0])
    onsets = (rise > 9) & (db > np.percentile(db, 40))
    per_sec = onsets[: len(onsets) // 100 * 100].reshape(-1, 100).sum(axis=1)
    return per_sec


vad = load_silero_vad()
manifest = []
for name, cat in SOURCES.items():
    video = SRC / f"{name}.mp4"
    if not video.exists():
        continue
    x = load(video, SR)
    speech = get_speech_timestamps(x, vad, sampling_rate=SR, threshold=0.4, min_silence_duration_ms=300)
    talk = np.zeros(len(x) // SR + 1, dtype=bool)
    for s in speech:
        talk[s["start"] // SR: s["end"] // SR + 2] = True
    score = transient_score(x, SR)
    n = min(len(score), len(talk))
    cands = []
    for start in range(2, n - CLIP, 5):
        if talk[start:start + CLIP].any():
            continue
        cands.append((float(score[start:start + CLIP].mean()), start))
    cands.sort(reverse=True)
    kept = []
    for sc, start in cands:
        if sc < 0.5 or any(abs(start - k) < CLIP for k in kept):
            continue
        kept.append(start)
        if len(kept) == PER_VIDEO:
            break
    out_dir = BANK / cat
    out_dir.mkdir(parents=True, exist_ok=True)
    for start in sorted(kept):
        stem = f"{name}-{start // 60:02d}-{start % 60:02d}"
        for suffix, tempo in (("", None), ("-slow", 0.85)):
            out = out_dir / f"{stem}{suffix}.wav"
            af = "highpass=f=60,loudnorm=I=-24:TP=-3:LRA=11" + (f",atempo={tempo}" if tempo else "")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(CLIP), "-i", str(video),
                            "-vn", "-ac", "2", "-ar", "48000", "-af", af + ",afade=t=in:d=0.5,areverse,afade=t=in:d=0.5,areverse",
                            str(out)], check=True)
        manifest.append({"file": f"{cat}/{stem}.wav", "slow": f"{cat}/{stem}-slow.wav", "source": f"{name}.mp4",
                         "at": f"{start // 60}:{start % 60:02d}", "seconds": CLIP,
                         "pops_per_second": round(float(score[start:start + CLIP].mean()), 2),
                         "talking": "none detected", "licence": "Ann's own recording"})
    talk_pct = 100 * talk[:n].mean() if n else 0
    print(f"{name}: {len(kept)} clips (talking in {talk_pct:.0f}% of the video)", flush=True)

(BANK / "bank.yaml").write_text("# Sound bank cut from Ann's own videos by tools/sound_bank.py. Listen before use.\n"
                                + yaml.safe_dump(manifest, sort_keys=False))
# a quick preview: the first 6 seconds of every clip, back to back
listen = BANK / "_listen.txt"
listen.write_text("".join(f"file '{BANK / m['file']}'\noutpoint 6\n" for m in manifest))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listen), "-b:a", "160k",
                str(BANK / "_listen.mp3")], check=True)
listen.unlink()
print(f"{len(manifest)} clips -> {BANK}")
