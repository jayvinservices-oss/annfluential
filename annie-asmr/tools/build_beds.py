"""Build the looping sound beds the video plans name (audio/sfx/<name>.wav) from the sound bank.

Each bed = the bank clips for that sound, joined with 2-second crossfades, so the assembler can loop it.
python tools/build_beds.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK, SFX = ROOT / "audio/sfx/bank", ROOT / "audio/sfx"
BEDS = {  # bed name -> bank clips (glob, inside audio/sfx/bank)
    "gum-pop-fast-01": "gum/*[0-9].wav",
    "gum-pop-slow-01": "gum/*-slow.wav",
}
# knuckle-crack-01 / finger-crack-01: the whole knuckle video's audio (no talking in it), finger = 85% tempo:
#   ffmpeg -i annie-src/gum-knuckle.mp4 -vn -af "highpass=f=60,loudnorm=I=-24:TP=-3:LRA=11" audio/sfx/knuckle-crack-01.wav
#   ffmpeg -i audio/sfx/knuckle-crack-01.wav -af atempo=0.85 audio/sfx/finger-crack-01.wav
for name, pattern in BEDS.items():
    clips = sorted(BANK.glob(pattern))
    if not clips:
        print("no bank clips for", name); continue
    inputs = sum((["-i", str(c)] for c in clips), [])
    chain, last = [], "[0:a]"
    for i in range(1, len(clips)):
        out = f"[a{i}]"
        chain.append(f"{last}[{i}:a]acrossfade=d=2:c1=tri:c2=tri{out}")
        last = out
    filt = ";".join(chain) if chain else "[0:a]anull[a0]"
    if not chain:
        last = "[a0]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", filt, "-map", last, "-ar", "48000",
                    "-ac", "2", str(SFX / f"{name}.wav")], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              str(SFX / f"{name}.wav")], capture_output=True, text=True).stdout)
    print(f"{name}.wav: {len(clips)} clips, {d / 60:.1f} min")
