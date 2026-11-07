"""Study your best videos cut by cut, every frame, so new videos copy what works.

  analyze <video> [<video> ...]   per video: every cut, shot lengths, per-frame brightness/colour/motion,
                                  loudness, the first 15 seconds in detail, and a full-size reference frame
                                  from every shot (prompts/reference/<name>/) for the avatar and prompts.
  voice-ref <video> --start --end  cut a clean sample of your voice for cloning (audio/voice-ref/).

Reports go to analysis/<name>/report.md, with analysis/summary.md comparing all videos analysed.
Your own videos: download them from YouTube Studio (Content -> the video -> three dots -> Download).
"""
from __future__ import annotations

import json
import re
import statistics as st
import subprocess
from pathlib import Path

from .config import AUDIO, PROMPTS, ROOT
from .ffmpeg_tools import fmt_ts, require_ffmpeg, run

ANALYSIS = ROOT / "analysis"


def parse_ts(v: str | float) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).split(":")]
    t = 0.0
    for p in parts:
        t = t * 60 + p
    return t


def _probe(video: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
               "-of", "json", video]).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return {"width": v["width"], "height": v["height"], "fps": round(float(num) / float(den), 2),
            "seconds": float(j["format"]["duration"]),
            "has_audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def _metadata_series(path: Path, keys: list[str]) -> list[tuple[float, dict]]:
    """Parse ffmpeg metadata=print output: blocks of 'frame:.. pts_time:T' then key=value lines."""
    rows, cur = [], None
    for line in path.read_text().splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            cur = (float(m.group(1)), {})
            rows.append(cur)
        elif cur and "=" in line:
            k, v = line.strip().split("=", 1)
            short = k.split(".")[-1]
            if short in keys:
                try:
                    cur[1][short] = float(v)
                except ValueError:
                    pass
    return rows


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 2) if xs else None


def _loud_mean(xs):
    """Average loudness in the energy domain, as LUFS."""
    import math
    xs = [x for x in xs if x is not None and x > -70]
    if not xs:
        return None
    return round(10 * math.log10(st.mean(10 ** (x / 10) for x in xs)), 1)


def analyze_video(video: Path, name: str | None = None, scene: float = 0.3, min_shot: float = 0.4,
                  max_frames: int = 80) -> dict:
    require_ffmpeg()
    video = Path(video)
    name = name or re.sub(r"[^a-z0-9]+", "-", video.stem.lower()).strip("-")[:50]
    out = ANALYSIS / name
    frames_dir = PROMPTS / "reference" / name
    out.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    info = _probe(video)
    print(f"  {video.name}: {info['width']}x{info['height']} {info['fps']}fps {fmt_ts(info['seconds'])}", flush=True)

    # 1. cuts
    proc = run(["ffmpeg", "-i", video, "-vf", f"scale=320:-2,select='gt(scene,{scene})',showinfo",
                "-an", "-f", "null", "-"], quiet=False)
    cuts = [float(t) for t in re.findall(r"pts_time:([\d.]+)", proc.stderr)]

    # 2. every frame: brightness + saturation, then motion (difference between consecutive frames)
    stats_file, motion_file = out / "frames.txt", out / "motion.txt"
    run(["ffmpeg", "-y", "-i", video, "-vf", f"scale=320:-2,signalstats,metadata=print:file={stats_file}",
         "-an", "-f", "null", "-"])
    run(["ffmpeg", "-y", "-i", video, "-vf",
         f"scale=320:-2,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file={motion_file}",
         "-an", "-f", "null", "-"])
    frames = _metadata_series(stats_file, ["YAVG", "SATAVG", "HUEAVG"])
    motion = _metadata_series(motion_file, ["YAVG"])

    # 3. loudness every 100 ms
    loud = []
    if info["has_audio"]:
        lf = out / "loudness.txt"
        run(["ffmpeg", "-y", "-i", video, "-vn", "-af", f"ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file={lf}",
             "-f", "null", "-"])
        loud = [(t, d.get("M")) for t, d in _metadata_series(lf, ["M"])]
        lf.unlink(missing_ok=True)
    stats_file.unlink(missing_ok=True)
    motion_file.unlink(missing_ok=True)

    # 4. shots
    bounds = [0.0] + [c for c in cuts if c > min_shot] + [info["seconds"]]
    shots = []
    for a, b in zip(bounds, bounds[1:]):
        if shots and b - a < min_shot:
            shots[-1]["end"] = b
            continue
        shots.append({"start": a, "end": b})

    def window(series, a, b, key):
        return [d.get(key) if isinstance(d, dict) else d for t, d in series if a <= t < b]

    step = max(1, len(shots) // max_frames + (1 if len(shots) % max_frames else 0))
    for i, s in enumerate(shots):
        a, b = s["start"], s["end"]
        s.update({
            "n": i + 1, "seconds": round(b - a, 2), "ts": fmt_ts(a),
            "brightness": _mean(window(frames, a, b, "YAVG")),
            "saturation": _mean(window(frames, a, b, "SATAVG")),
            "motion": _mean(window(motion, a, b, "YAVG")),
            "loudness": _loud_mean(window(loud, a, b, None) if loud else []),
        })
        if i % step == 0:
            mid = a + (b - a) / 2
            jpg = frames_dir / f"shot-{i + 1:03d}-{int(a):05d}s.jpg"
            run(["ffmpeg", "-y", "-ss", f"{mid:.3f}", "-i", video, "-frames:v", "1", "-q:v", "2", jpg])
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(jpg), "-vf", "scale=1:1:flags=area",
                                  "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            s["frame"] = str(jpg.relative_to(ROOT))
            s["colour"] = "#" + raw[:3].hex() if len(raw) >= 3 else None

    # 5. the opening (first 15 s, second by second)
    opening = []
    for sec in range(0, min(15, int(info["seconds"]))):
        opening.append({"t": sec, "loudness": _loud_mean(window(loud, sec, sec + 1, None) if loud else []),
                        "motion": _mean(window(motion, sec, sec + 1, "YAVG")),
                        "cut": any(sec <= c < sec + 1 for c in cuts)})
    whole = _loud_mean([d for _, d in loud]) if loud else None
    first5 = _loud_mean(window(loud, 0, 5, None)) if loud else None
    jumps = [abs((b["loudness"] or -70) - (a["loudness"] or -70)) for a, b in zip(opening, opening[1:])]
    silent_start = next((o["t"] for o in opening if (o["loudness"] or -70) > -50), None)

    lengths = [s["seconds"] for s in shots]
    result = {
        "name": name, "file": video.name, **info,
        "cuts": len(cuts), "shots": len(shots),
        "shot_seconds": {"mean": _mean(lengths), "median": round(st.median(lengths), 2) if lengths else None,
                         "min": min(lengths) if lengths else None, "max": max(lengths) if lengths else None},
        "loudness_lufs": whole, "first5_lufs": first5,
        "first5_vs_rest_db": round(first5 - whole, 1) if first5 is not None and whole is not None else None,
        "biggest_jump_first15_db": round(max(jumps), 1) if jumps else None,
        "sound_starts_at_s": silent_start,
        "brightness": _mean([d.get("YAVG") for _, d in frames]),
        "saturation": _mean([d.get("SATAVG") for _, d in frames]),
        "opening": opening, "shots_detail": shots,
    }
    (out / "data.json").write_text(json.dumps(result, indent=2))
    _contact_sheet(frames_dir, out / "contact-sheet.jpg")
    (out / "report.md").write_text(_report(result))
    print(f"  -> {out / 'report.md'}  ({len(shots)} shots, frames in {frames_dir.relative_to(ROOT)})")
    return result


def _contact_sheet(frames_dir: Path, out: Path) -> None:
    files = sorted(frames_dir.glob("shot-*.jpg"))
    if not files:
        return
    cols = 6
    rows = (len(files) + cols - 1) // cols
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{f.resolve()}'\nduration 1\n" for f in files))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-vf",
         f"scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:-1:-1,tile={cols}x{rows}",
         "-frames:v", "1", "-q:v", "3", out])
    listing.unlink()


def _report(r: dict) -> str:
    o = r["opening"]
    lines = [
        f"# {r['file']}", "",
        f"- {r['width']}x{r['height']}, {r['fps']} fps, {fmt_ts(r['seconds'])}",
        f"- {r['shots']} shots; shot length mean {r['shot_seconds']['mean']}s, median {r['shot_seconds']['median']}s "
        f"(shortest {r['shot_seconds']['min']}s, longest {r['shot_seconds']['max']}s)",
        f"- Loudness {r['loudness_lufs']} LUFS overall; first 5 s {r['first5_lufs']} LUFS "
        f"({r['first5_vs_rest_db']:+} dB vs the rest)" if r["first5_vs_rest_db"] is not None else "- No audio",
        f"- Biggest second-to-second loudness jump in the first 15 s: {r['biggest_jump_first15_db']} dB",
        f"- Sound starts at {r['sound_starts_at_s']} s" if r["sound_starts_at_s"] is not None else "- Near-silent first 15 s",
        f"- Average brightness {r['brightness']} (0-255), saturation {r['saturation']}", "",
        "## First 15 seconds, second by second", "", "| s | loudness | motion | cut |", "|---:|---:|---:|---|",
    ]
    lines += [f"| {x['t']} | {x['loudness']} | {x['motion']} | {'cut' if x['cut'] else ''} |" for x in o]
    lines += ["", "## Every shot", "", "| # | at | length | brightness | saturation | motion | loudness | colour | frame |",
              "|---:|---|---:|---:|---:|---:|---:|---|---|"]
    for s in r["shots_detail"]:
        lines.append(f"| {s['n']} | {s['ts']} | {s['seconds']}s | {s['brightness']} | {s['saturation']} | {s['motion']} | "
                     f"{s['loudness']} | {s.get('colour') or ''} | {Path(s['frame']).name if s.get('frame') else ''} |")
    lines += ["", "Motion: average pixel change between frames (higher = more movement).",
              "Full-size frames are in the folder named in `frame`; contact-sheet.jpg shows them all."]
    return "\n".join(lines) + "\n"


def summary() -> str:
    rows = []
    for p in sorted(ANALYSIS.glob("*/data.json")):
        rows.append(json.loads(p.read_text()))
    lines = ["# Analysed videos", "",
             "| video | length | shots | median shot | LUFS | first 5 s vs rest | jump first 15 s | brightness |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['file'][:45]} | {fmt_ts(r['seconds'])} | {r['shots']} | {r['shot_seconds']['median']}s | "
                     f"{r['loudness_lufs']} | {r['first5_vs_rest_db']} | {r['biggest_jump_first15_db']} | {r['brightness']} |")
    text = "\n".join(lines) + "\n"
    (ANALYSIS / "summary.md").write_text(text)
    return text


def voice_ref(video: Path, start: str, end: str, name: str) -> Path:
    """Cut a clean voice sample for cloning: mono, 24 kHz, rumble removed, gentle denoise, levelled."""
    require_ffmpeg()
    a, b = parse_ts(start), parse_ts(end)
    out = AUDIO / "voice-ref" / f"{name}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-ss", a, "-to", b, "-i", video, "-vn", "-ac", "1", "-ar", "24000",
         "-af", "highpass=f=70,afftdn=nf=-30,loudnorm=I=-20:TP=-2", "-c:a", "pcm_s16le", out])
    secs = b - a
    print(f"Voice sample: {out} ({secs:.0f} s)")
    if secs < 8 or secs > 45:
        print("  tip: 10 to 30 seconds of only your voice (no gum or tapping over it) clones best")
    return out
