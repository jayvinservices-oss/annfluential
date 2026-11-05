"""Step 4: stitch and loop clips into a 20-60 minute video with crossfades, levelled audio and chapters.

How the loop stays smooth: each segment is built from "units". A unit is the segment's clips
crossfaded in a shuffled order, starting and ending on the same anchor frame, so units can be
joined back to back with no visible jump and no re-encoding. Several units with different clip
orders are cycled so the loop does not repeat identically. Segments (chapters) are then
crossfaded into one another, and one audio track is built to match exactly.
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime
from pathlib import Path

from .config import RENDERS, VOICE, config
from .episode import sound_layers, voice_lines
from .ffmpeg_tools import duration, fmt_ts, loudnorm_measure, require_ffmpeg, run, x264
from .generate import clips_for_shot

AUDIO_EXT = (".wav", ".mp3", ".m4a", ".aac", ".flac")


def render_path(slug: str) -> Path:
    return RENDERS / f"{slug}.mp4"


def timeline_path(slug: str) -> Path:
    return RENDERS / f"{slug}.timeline.json"


def _frames(seconds: float, fps: int) -> float:
    return round(seconds * fps) / fps


def _key(*parts) -> str:
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:10]


# ---------- video ----------

def normalize_clip(src: Path, work: Path, vcfg: dict, speed: float = 1.0) -> tuple[Path, float]:
    """Scale/crop to the channel frame, fixed fps, no audio, frame-exact length.
    speed < 1 = smooth slow motion with motion-interpolated in-between frames (episode `clip_speed`, e.g. 0.5)."""
    W, H, fps = vcfg["width"], vcfg["height"], int(vcfg["fps"])
    out = work / "norm" / f"{src.stem}-{_key(src.resolve(), src.stat().st_mtime, W, H, fps, speed)}.mp4"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        length = _frames(duration(src) / speed, fps) - 1 / fps
        slow = (f"setpts={1 / speed:.4f}*PTS,minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
                if speed < 1 else "")
        vf = (f"{slow}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"fps={fps},format=yuv420p,setsar=1")
        run(["ffmpeg", "-y", "-i", src, "-t", f"{length:.4f}", "-vf", vf, "-an", *x264(vcfg), out])
    return out, duration(out)


def build_unit(clips: list[tuple[Path, float]], out: Path, fade: float, vcfg: dict) -> float:
    """Crossfade clips in order and come back round to clip 0, cut so the end meets the start."""
    seq = clips + [clips[0]]
    for path, d in seq:
        if d <= 2 * fade + 0.2:
            raise SystemExit(f"Clip {path.name} is {d:.1f}s; it must be longer than {2 * fade + 0.2:.1f}s for the crossfade.")
    fps = int(vcfg["fps"])
    if out.exists():
        return duration(out)
    args, f = [], []
    for i, (path, _) in enumerate(seq):
        args += ["-i", path]
        f.append(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[n{i}]")
    prev, length, last_offset = "n0", seq[0][1], 0.0
    for i in range(1, len(seq)):
        last_offset = _frames(length - fade, fps)
        f.append(f"[{prev}][n{i}]xfade=transition=fade:duration={fade}:offset={last_offset:.4f}[x{i}]")
        length = last_offset + seq[i][1]
        prev = f"x{i}"
    end = last_offset + fade
    f.append(f"[{prev}]trim=start={fade}:end={end:.4f},setpts=PTS-STARTPTS[out]")
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", *args, "-filter_complex", ";".join(f), "-map", "[out]", "-an", *x264(vcfg), out])
    return duration(out)


def build_segment(ep: dict, seg: dict, work: Path, vcfg: dict, rng: random.Random) -> Path:
    pool, missing = [], []
    for shot_id in seg["shots"]:
        found = clips_for_shot(ep["slug"], shot_id)
        if not found:
            missing.append(shot_id)
        pool += found
    if missing:
        raise SystemExit(f"Segment '{seg['id']}' has no clips yet for: {', '.join(missing)} "
                         f"(expected in clips/{ep['slug']}/). Run: python -m pipeline generate {ep['slug']}")
    fps = int(vcfg["fps"])
    fade = _frames(float(vcfg.get("crossfade_seconds", 1.5)), fps)
    norm = [normalize_clip(p, work, vcfg, float(ep.get("clip_speed", 1.0))) for p in pool]
    anchor, rest = norm[0], norm[1:]

    n_variants = 1 if len(rest) < 2 else int(vcfg.get("loop_variants", 3))
    units, seen = [], set()
    for v in range(n_variants):
        order = rest[:]
        rng.shuffle(order)
        sig = tuple(p.name for p, _ in order)
        if sig in seen:
            continue
        seen.add(sig)
        out = work / "units" / f"{seg['id']}-{_key(anchor[0].name, sig, fade, fps)}.mp4"
        units.append((out, build_unit([anchor] + order, out, fade, vcfg)))

    target = float(seg["minutes"]) * 60
    playlist, total, i = [], 0.0, 0
    while not playlist or total + units[i % len(units)][1] / 2 < target:
        u = units[i % len(units)]
        playlist.append(u[0])
        total += u[1]
        i += 1
    listing = work / f"{seg['id']}.concat.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in playlist))
    out = work / f"seg-{seg['id']}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", out])
    return out


def join_segments(seg_files: list[Path], out: Path, sfade: float, vcfg: dict, crossfade: bool) -> list[float]:
    lengths = [duration(p) for p in seg_files]
    if len(seg_files) == 1 or not crossfade:
        listing = out.with_suffix(".concat.txt")
        listing.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_files))
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", out])
        return lengths
    for p, d in zip(seg_files, lengths):
        if d <= 2 * sfade:
            raise SystemExit(f"{p.name} is too short for a {sfade}s chapter crossfade")
    args, f, prev, length = [], [], "0:v", lengths[0]
    for i, p in enumerate(seg_files):
        args += ["-i", p]
    for i in range(1, len(seg_files)):
        offset = length - sfade
        f.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={sfade}:offset={offset:.4f}[j{i}]")
        prev, length = f"j{i}", offset + lengths[i]
    print(f"  encoding final picture ({fmt_ts(length)}), this is the slow part ...", flush=True)
    run(["ffmpeg", "-y", *args, "-filter_complex", ";".join(f), "-map", f"[{prev}]", "-an", *x264(vcfg), out])
    return lengths


# ---------- audio ----------

def find_voice_file(slug: str, line_id: str) -> Path | None:
    for ext in AUDIO_EXT:
        p = VOICE / slug / f"{line_id}{ext}"
        if p.exists():
            return p
    return None


def build_audio(ep: dict, starts: list[float], lengths: list[float], total: float, sfade: float,
                work: Path, acfg: dict, allow_missing_voice: bool) -> Path:
    sr = int(acfg["sample_rate"])
    fmt = f"aformat=sample_rates={sr}:channel_layouts=stereo"
    args, f, labels = [], [], []
    k = 0
    for seg, start, length in zip(ep["segments"], starts, lengths):
        ms = int(round(start * 1000))
        for layer in sound_layers(seg):
            if not layer["file"].exists():
                raise SystemExit(f"Sound bed not found: {layer['file']}")
            gain = float(acfg.get("bed_gain_db", 0)) + layer["gain_db"]
            args += ["-stream_loop", "-1", "-i", layer["file"]]
            f.append(f"[{k}:a]{fmt},atrim=0:{length:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={sfade},afade=t=out:st={length - sfade:.3f}:d={sfade},"
                     f"volume={gain}dB,adelay=delays={ms}:all=1[a{k}]")
            labels.append(f"[a{k}]")
            k += 1
    seg_start = {s["id"]: st for s, st in zip(ep["segments"], starts)}
    seg_len = {s["id"]: ln for s, ln in zip(ep["segments"], lengths)}
    missing = []
    for line in voice_lines(ep):
        p = find_voice_file(ep["slug"], line["id"])
        if not p:
            missing.append(line["id"])
            continue
        if line["at"] > seg_len[line["segment"]]:
            print(f"  warning: voice line {line['id']} starts after its segment ends")
        ms = int(round((seg_start[line["segment"]] + line["at"]) * 1000))
        args += ["-i", p]
        f.append(f"[{k}:a]{fmt},volume={float(acfg.get('voice_gain_db', 0))}dB,adelay=delays={ms}:all=1[a{k}]")
        labels.append(f"[a{k}]")
        k += 1
    if missing and not allow_missing_voice:
        raise SystemExit(f"Voice files missing for: {', '.join(missing)} (audio/voice/{ep['slug']}/). "
                         "Run: python -m pipeline voice <slug>   or assemble with --allow-missing-voice")
    if not labels:
        args += ["-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=stereo"]
        labels, f = ["[0:a]"], []
    mix = work / "mix.wav"
    tail = f"apad=whole_dur={total:.3f},atrim=0:{total:.3f}[mix]"
    if len(labels) == 1:
        f.append(f"{labels[0]}{tail}")
    else:
        f.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,{tail}")
    run(["ffmpeg", "-y", *args, "-filter_complex", ";".join(f), "-map", "[mix]", "-c:a", "pcm_s24le", "-ar", sr, mix])

    # two-pass loudness levelling
    i, tp, lra = acfg["target_lufs"], acfg["true_peak"], acfg["lra"]
    m = loudnorm_measure(mix, i, tp, lra)
    master = work / "master.wav"
    if float(m["input_i"]) == float("-inf") or m["input_i"] == "-inf":
        run(["ffmpeg", "-y", "-i", mix, "-c:a", "pcm_s24le", master])  # silent: nothing to level
    else:
        ln = (f"loudnorm=I={i}:TP={tp}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        run(["ffmpeg", "-y", "-i", mix, "-af", ln, "-ar", sr, "-c:a", "pcm_s24le", master])
    return master


# ---------- chapters + main ----------

def chapters(ep: dict, starts: list[float], sfade: float) -> list[dict]:
    out = []
    for n, (seg, st) in enumerate(zip(ep["segments"], starts)):
        t = 0 if n == 0 else int(round(st + sfade / 2))
        out.append({"t": t, "ts": fmt_ts(t), "title": seg["chapter"]})
    return out


def chapter_problems(chs: list[dict], total: float) -> list[str]:
    p = []
    if len(chs) < 3:
        p.append("YouTube needs at least 3 chapters to show them")
    ends = [c["t"] for c in chs[1:]] + [total]
    for c, end in zip(chs, ends):
        if end - c["t"] < 10:
            p.append(f"chapter '{c['title']}' is shorter than 10 seconds")
    return p


def write_ffmeta(path: Path, title: str, chs: list[dict], total: float) -> None:
    lines = [";FFMETADATA1", f"title={title}"]
    ends = [c["t"] for c in chs[1:]] + [total]
    for c, end in zip(chs, ends):
        safe = c["title"].replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(c['t'] * 1000)}", f"END={int(end * 1000)}", f"title={safe}"]
    path.write_text("\n".join(lines) + "\n")


def assemble(ep: dict, *, allow_missing_voice: bool = False, fast: bool = False, fresh: bool = False) -> Path:
    require_ffmpeg()
    cfg = config()
    vcfg, acfg = cfg["video"], cfg["audio"]
    work = RENDERS / ep["slug"] / "work"
    if fresh and work.exists():
        import shutil
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    rng = random.Random(ep["slug"])
    sfade = 0.0 if fast else _frames(float(vcfg.get("segment_crossfade_seconds", 2.0)), int(vcfg["fps"]))

    seg_files = []
    for seg in ep["segments"]:
        print(f"  segment {seg['id']}: {seg['minutes']} min from {', '.join(seg['shots'])}", flush=True)
        seg_files.append(build_segment(ep, seg, work, vcfg, rng))

    picture = work / "picture.mp4"
    lengths = join_segments(seg_files, picture, sfade, vcfg, crossfade=not fast)
    starts, t = [], 0.0
    for n, ln in enumerate(lengths):
        starts.append(t)
        t += ln - (sfade if n < len(lengths) - 1 else 0)
    total = duration(picture)

    print("  mixing and levelling audio ...", flush=True)
    master = build_audio(ep, starts, lengths, total, max(sfade, 0.5), work, acfg, allow_missing_voice)

    chs = chapters(ep, starts, sfade)
    meta = work / "chapters.ffmeta"
    write_ffmeta(meta, ep["title"], chs, total)
    out = render_path(ep["slug"])
    run(["ffmpeg", "-y", "-i", picture, "-i", master, "-i", meta, "-map", "0:v", "-map", "1:a",
         "-map_metadata", "2", "-map_chapters", "2", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
         "-ar", acfg["sample_rate"], "-shortest", "-movflags", "+faststart", out])

    final = duration(out)
    timeline = {
        "slug": ep["slug"], "render": str(out), "seconds": round(final, 2), "length": fmt_ts(final),
        "segments": [{"id": s["id"], "chapter": s["chapter"], "start": round(st, 2), "seconds": round(ln, 2)}
                     for s, st, ln in zip(ep["segments"], starts, lengths)],
        "chapters": chs, "chapter_problems": chapter_problems(chs, final),
        "built": datetime.now().isoformat(timespec="seconds"),
    }
    timeline_path(ep["slug"]).write_text(json.dumps(timeline, indent=2))
    print(f"\nRendered {out} ({fmt_ts(final)})")
    for p in timeline["chapter_problems"]:
        print(f"  chapter warning: {p}")
    if not 20 * 60 <= final <= 60 * 60:
        print(f"  note: length {fmt_ts(final)} is outside the 20 to 60 minute plan")
    return out


def trailer(ep: dict, start: float, seconds: float, x_offset: float = 0.5) -> Path:
    """Vertical Short cut from the long render, to point viewers to the full video."""
    require_ffmpeg()
    src = render_path(ep["slug"])
    if not src.exists():
        raise SystemExit("Render the long video first: python -m pipeline assemble " + ep["slug"])
    seconds = min(seconds, 59)
    out = RENDERS / f"{ep['slug']}-short.mp4"
    vcfg = config()["video"]
    vf = (f"crop=ih*9/16:ih:(iw-ih*9/16)*{x_offset}:0,scale=1080:1920,setsar=1,"
          f"fade=t=in:d=0.4,fade=t=out:st={seconds - 0.6:.2f}:d=0.6")
    af = f"afade=t=in:d=0.4,afade=t=out:st={seconds - 0.6:.2f}:d=0.6"
    run(["ffmpeg", "-y", "-ss", start, "-i", src, "-t", seconds, "-vf", vf, "-af", af,
         *x264(vcfg), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(f"Short trailer: {out}")
    return out


def thumbnail(ep: dict, at: float | None = None) -> Path:
    """Defaults to the opening shot (the first shot of the first chapter), so the click matches the first frame."""
    require_ffmpeg()
    src = render_path(ep["slug"])
    if not src.exists():
        raise SystemExit("Render the long video first: python -m pipeline assemble " + ep["slug"])
    if at is None:
        at = float((config().get("opening") or {}).get("thumbnail_at", 3))
    out = RENDERS / f"{ep['slug']}-thumb.jpg"
    run(["ffmpeg", "-y", "-ss", at, "-i", src, "-frames:v", "1", "-vf", "scale=1280:720", "-q:v", "2", out])
    print(f"Thumbnail frame: {out} (add any text in Canva)")
    return out
