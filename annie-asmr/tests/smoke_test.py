"""End-to-end check of prompts -> assemble -> metadata -> trailer on synthetic clips. No API keys needed.

Run from annie-asmr/:   python tests/smoke_test.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def sh(*cmd):
    subprocess.run([str(c) for c in cmd], check=True, capture_output=True)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="annie-smoke-"))
    try:
        shutil.copytree(HERE / "prompts", tmp / "prompts")
        cfg = (HERE / "config.yaml").read_text()
        cfg = cfg.replace("width: 1920", "width: 640").replace("height: 1080", "height: 360").replace("preset: medium", "preset: ultrafast")
        (tmp / "config.yaml").write_text(cfg)
        for d in ("episodes", "clips/smoke", "audio/sfx", "audio/voice/smoke", "renders", "metadata"):
            (tmp / d).mkdir(parents=True, exist_ok=True)

        # synthetic clips (different colours / sizes / lengths, like real generator output)
        colors = ["red", "green", "blue", "orange", "purple", "teal"]
        shots = ["pick-gift", "pull-ribbon", "unwrap", "reveal"]
        for n, shot in enumerate(shots):
            for t in (1, 2):
                c = colors[(n + t) % len(colors)]
                sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c={c}:s=1280x720:r=24:d={5 + t}",
                   "-f", "lavfi", "-i", "sine=f=300:d=8", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   tmp / "clips/smoke" / f"{shot}__t{t}.mp4")
        sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anoisesrc=c=pink:d=3:a=0.2", tmp / "audio/sfx/paper.wav")
        sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=220:d=4", "-ac", "1", tmp / "audio/sfx/tap.wav")
        for line in ("a-01", "b-01"):
            sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=660:d=2", tmp / "audio/voice/smoke" / f"{line}.mp3")

        (tmp / "episodes/smoke.yaml").write_text("""
slug: smoke
theme: christmas-unwrapping
title: "ASMR Unwrapping Christmas Gifts | Kraft Paper & Ribbon | Whispers"
description: Test episode.
variation: {wrapping: brown kraft paper, ribbon: red satin ribbon, nail_colour: classic red}
objects: [kraft paper gifts, red satin ribbon]
sounds: [paper crinkle, ribbon pulling]
segments:
  - id: a
    chapter: The gift pile
    minutes: 0.4
    shots: [pick-gift, reveal]
    sound_bed: audio/sfx/paper.wav
    voice: [{at: 2, text: "Hi, welcome back."}]
  - id: b
    chapter: Ribbons and paper
    minutes: 0.5
    shots: [pull-ribbon, unwrap]
    sound_bed: [audio/sfx/paper.wav, {file: audio/sfx/tap.wav, gain_db: -6}]
    voice: [{at: 3, text: "Nice and slow."}]
  - id: c
    chapter: What's inside
    minutes: 0.3
    shots: [reveal]
    sound_bed: audio/sfx/tap.wav
""")
        env = dict(os.environ, ANNIE_ROOT=str(tmp), PYTHONPATH=str(HERE))

        def cli(*args):
            r = subprocess.run([sys.executable, "-m", "pipeline", *args], cwd=tmp, env=env, capture_output=True, text=True)
            print(r.stdout + r.stderr)
            if r.returncode:
                raise SystemExit(f"command failed: {args}")

        cli("prompts", "smoke")
        cli("generate", "smoke", "--dry-run")
        cli("assemble", "smoke")
        cli("metadata", "smoke")
        cli("trailer", "smoke", "--start", "5", "--seconds", "10")
        cli("thumb", "smoke", "--at", "3")

        tl = json.loads((tmp / "renders/smoke.timeline.json").read_text())
        meta = json.loads((tmp / "metadata/smoke.json").read_text())
        out = tmp / "renders/smoke.mp4"
        probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_chapters", "-show_streams", "-show_format",
                                           "-of", "json", out], capture_output=True, text=True).stdout)
        vdur = float(next(s for s in probe["streams"] if s["codec_type"] == "video")["duration"])
        adur = float(next(s for s in probe["streams"] if s["codec_type"] == "audio")["duration"])
        loud = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128", "-f", "null", "-"],
                              capture_output=True, text=True).stderr
        integrated = float(loud.rsplit("I:", 1)[1].split("LUFS")[0])

        assert abs(vdur - adur) < 0.15, (vdur, adur)
        assert abs(tl["seconds"] - 72) < 15, tl["seconds"]      # 0.4+0.5+0.3 min, loops round to whole units
        assert len(probe["chapters"]) == 3, probe["chapters"]
        assert [c["title"] for c in tl["chapters"]] == ["The gift pile", "Ribbons and paper", "What's inside"]
        assert tl["chapters"][0]["t"] == 0
        assert "0:00 The gift pile" in meta["description"]
        assert meta["contains_synthetic_media"] is True and meta["privacy_status"] == "private"
        assert not meta["checks"]["errors"], meta["checks"]
        assert abs(integrated - (-18)) < 1.5, integrated
        assert (tmp / "renders/smoke-short.mp4").exists() and (tmp / "renders/smoke-thumb.jpg").exists()
        short = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                           "stream=width,height", "-of", "json", tmp / "renders/smoke-short.mp4"],
                                          capture_output=True, text=True).stdout)["streams"][0]
        assert (short["width"], short["height"]) == (1080, 1920), short

        # honesty checks must catch a misleading title
        sys.path.insert(0, str(HERE))
        os.environ["ANNIE_ROOT"] = str(tmp)
        from pipeline.episode import load_episode
        from pipeline.metadata import check_title
        ep = load_episode(str(tmp / "episodes/smoke.yaml"))
        ep["title"] = "ASMR 1 Hour Girlfriend Roleplay | No Talking | Glass Fruit"
        errs, warns = check_title(ep, tl["seconds"])
        joined = " ".join(errs + warns)
        assert "girlfriend" in joined and "roleplay" in joined and "no talking" in joined and "1 hour" in joined
        assert "fruit" in joined, warns

        print(f"\nSMOKE TEST PASSED: {tl['length']} video, {len(probe['chapters'])} chapters, {integrated:.1f} LUFS")
    finally:
        if os.environ.get("KEEP_SMOKE"):
            print(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
