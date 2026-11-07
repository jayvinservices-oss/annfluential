"""Step 5: whispers and talking in Ann's cloned voice -> audio/voice/<slug>/<line-id>.mp3|wav.

Providers (config.yaml -> voice.provider):
  elevenlabs  hosted; needs ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env
  voicestudio VoiceStudio backend (github.com/debpalash/VoiceStudio). It cannot run on an Intel Mac,
              so it runs on another machine (e.g. the rented cloud GPU); needs VOICESTUDIO_URL,
              VOICESTUDIO_API_KEY and VOICESTUDIO_PROFILE_ID (your saved cloned-voice profile)
  voxcpm      VoxCPM2 (free, Apache 2.0, commercial use allowed), cloned from audio/voice-ref/<name>.wav.
              Runs on CPU in the cloud session or any Linux/Apple Silicon machine; set voice.voxcpm.python
  local       runs any text-to-speech command on the Mac
  manual      writes a script sheet; you record or export each line with the given file name
"""
from __future__ import annotations

import shlex
import subprocess
import tempfile
from pathlib import Path

import requests

from .assemble import find_voice_file
from .config import VOICE, config, secret
from .episode import voice_lines


def script_sheet(ep: dict) -> str:
    out = [f"# Voice script: {ep['slug']}", "", "Save each line as audio/voice/<slug>/<id>.wav (or .mp3).", ""]
    for line in voice_lines(ep):
        out.append(f"- `{line['id']}` ({line['style']}, at {line['at']:.0f}s into its chapter): {line['text']}")
    return "\n".join(out) + "\n"


def _elevenlabs(text: str, style: str, out: Path, c: dict) -> None:
    tag = c.get("whisper_tag", "") if style in ("whisper", "brand") else ""
    body = {
        "text": f"{tag} {text}".strip(),
        "model_id": c.get("model_id", "eleven_v3"),
        "voice_settings": {"stability": c.get("stability", 0.5), "similarity_boost": c.get("similarity_boost", 0.85),
                           "style": c.get("style", 0.0)},
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{secret('ELEVENLABS_VOICE_ID')}"
    r = requests.post(url, params={"output_format": c.get("output_format", "mp3_44100_128")}, json=body,
                      headers={"xi-api-key": secret("ELEVENLABS_API_KEY")}, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"ElevenLabs refused line ({r.status_code}): {r.text[:300]}")
    out.write_bytes(r.content)


def _voicestudio(text: str, style: str, out: Path, c: dict) -> None:
    import time
    base = secret("VOICESTUDIO_URL").rstrip("/")
    form = {
        "text": text,
        "profile_id": secret("VOICESTUDIO_PROFILE_ID"),
        "num_step": str(c.get("num_step", 32)),
        "speed": str(c.get("speed", 0.95)),
        "effect_preset": c.get("effect_preset", "broadcast"),
        "wav_bits": "24",
    }
    if style in ("whisper", "brand"):
        form["instruct"] = "whisper"
    if c.get("seed") is not None:
        form["seed"] = str(c["seed"])
    if c.get("engine"):
        form["engine"] = c["engine"]
    headers = {"Authorization": f"Bearer {secret('VOICESTUDIO_API_KEY')}"}
    for attempt in range(6):
        r = requests.post(f"{base}/generate", data=form, headers=headers, timeout=600)
        if r.status_code in (429, 503) and attempt < 5:  # model loading / busy
            time.sleep(int(r.headers.get("Retry-After", 30)))
            continue
        if r.status_code >= 400 or not r.headers.get("content-type", "").startswith("audio"):
            raise RuntimeError(f"VoiceStudio refused line ({r.status_code}): {r.text[:300]}")
        out.write_bytes(r.content)
        return


def _local(text: str, out: Path, c: dict) -> None:
    template = c.get("command", "").strip()
    if not template:
        raise SystemExit("voice.local.command is empty in config.yaml. Use provider 'voicestudio' or 'manual'.")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        tf.write(text)
    cmd = template.format(text_file=shlex.quote(tf.name), out=shlex.quote(str(out)))
    subprocess.run(cmd, shell=True, check=True)


def _check_model_download(model: str) -> None:
    """Fail fast with a clear message when the model weights cannot be downloaded."""
    from pathlib import Path as _P
    cached = list((_P.home() / ".cache/huggingface/hub" / f"models--{model.replace('/', '--')}" / "snapshots").glob("*/*.safetensors"))
    if cached:
        return
    try:
        r = requests.head(f"https://huggingface.co/{model}/resolve/main/model.safetensors", allow_redirects=True, timeout=20)
        ok = r.status_code < 400
    except requests.RequestException:
        ok = False
    if not ok:
        raise SystemExit("The voice model's files cannot be downloaded from here. In the cloud environment settings "
                         "(Network access) allow '*.hf.co' (the model files come from us.aws.cdn.hf.co), then start "
                         "a new session.")


def _voxcpm_batch(todo: list[tuple[dict, Path]], c: dict) -> None:
    import json
    import os
    from .config import ROOT, project_path
    py = os.environ.get("VOXCPM_PYTHON") or c.get("python") or "python3"
    ref = project_path(c.get("reference", "audio/voice-ref/annie-whisper.wav"))
    if not ref.exists():
        raise SystemExit(f"No voice sample at {ref}. Make one: python -m pipeline voice-ref <video> --start --end")
    lines = []
    for line, out in todo:
        control = c.get("whisper_control", "") if line["style"] in ("whisper", "brand") else c.get("soft_control", "")
        lines.append({"text": line["text"], "control": control, "out": str(out)})
    job = {"model": c.get("model", "openbmb/VoxCPM2"), "reference": str(ref),
           "cfg_value": c.get("cfg_value", 2.0), "timesteps": c.get("timesteps", 10), "lines": lines}
    _check_model_download(job["model"])
    jf = todo[0][1].parent / "_voxcpm_jobs.json"
    jf.write_text(json.dumps(job, indent=2))
    subprocess.run([py, str(ROOT / "tools" / "voxcpm_batch.py"), str(jf)], check=True)


def make_voice(ep: dict, provider: str | None = None, redo: list[str] | None = None) -> None:
    vcfg = config()["voice"]
    provider = provider or vcfg["provider"]
    d = VOICE / ep["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "_script.md").write_text(script_sheet(ep))
    missing, batch = [], []
    for line in voice_lines(ep):
        existing = find_voice_file(ep["slug"], line["id"])
        if existing and not (redo and line["id"] in redo):
            print(f"  have   {existing.name}")
            continue
        if provider == "manual":
            missing.append(line["id"])
            continue
        ext = ".mp3" if provider == "elevenlabs" else ".wav"
        out = d / f"{line['id']}{ext}"
        if provider == "voxcpm":
            batch.append((line, out))
            continue
        print(f"  voice  {line['id']}: {line['text'][:60]}", flush=True)
        if provider == "elevenlabs":
            _elevenlabs(line["text"], line["style"], out, vcfg.get("elevenlabs", {}))
        elif provider == "voicestudio":
            _voicestudio(line["text"], line["style"], out, vcfg.get("voicestudio", {}))
        elif provider == "local":
            _local(line["text"], out, vcfg.get("local", {}))
        else:
            raise SystemExit(f"Unknown voice provider '{provider}'")
    if batch:
        print(f"  voxcpm: making {len(batch)} line(s) (first run downloads the model, about 5 GB) ...", flush=True)
        _voxcpm_batch(batch, vcfg.get("voxcpm", {}))
    if missing:
        print(f"\n{len(missing)} line(s) to record or export. Script: {d / '_script.md'}")
    print("Listen to every line before assembling; re-make one with --redo <line-id>.")
