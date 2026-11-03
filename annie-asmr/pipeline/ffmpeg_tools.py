from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not found. On the Mac: brew install ffmpeg")


def run(cmd: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess:
    cmd = [str(c) for c in cmd]
    if cmd[0] == "ffmpeg":
        cmd[1:1] = ["-hide_banner", "-nostdin"] + (["-loglevel", "error"] if quiet else [])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or proc.stdout).strip().splitlines()[-25:])
        raise RuntimeError(f"{cmd[0]} failed:\n{tail}")
    return proc


def duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path]).stdout
    return float(json.loads(out)["format"]["duration"])


def has_audio(path: Path) -> bool:
    out = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
               "-of", "csv=p=0", path]).stdout
    return bool(out.strip())


def x264(vcfg: dict) -> list[str]:
    fps = int(vcfg["fps"])
    return ["-c:v", "libx264", "-preset", vcfg.get("preset", "medium"), "-crf", str(vcfg.get("crf", 18)),
            "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 2), "-video_track_timescale", "90000"]


def loudnorm_measure(path: Path, i: float, tp: float, lra: float) -> dict:
    proc = run(["ffmpeg", "-i", path, "-af", f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json",
                "-f", "null", "-"], quiet=False)
    match = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.S)
    if not match:
        raise RuntimeError("Could not read loudness measurement from ffmpeg")
    return json.loads(match[-1])


def fmt_ts(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
