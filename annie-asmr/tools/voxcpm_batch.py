"""Run inside the VoxCPM environment: python voxcpm_batch.py jobs.json
jobs.json = {"model": ..., "reference": wav, "cfg_value": 2.0, "timesteps": 10, "denoise": false,
             "prompt_wav": wav, "prompt_text": "exact words in prompt_wav",
             "lines": [{"text": ..., "control": ..., "out": path}, ...]}
Loads the model once and writes one WAV per line.
"""
import json
import sys

import soundfile as sf
from voxcpm import VoxCPM

job = json.load(open(sys.argv[1]))
model = VoxCPM.from_pretrained(job.get("model", "openbmb/VoxCPM2"), load_denoiser=bool(job.get("denoise", False)),
                               optimize=False, device="cpu")
sr = model.tts_model.sample_rate
for line in job["lines"]:
    text = f"({line['control']}){line['text']}" if line.get("control") else line["text"]
    extra = {}
    if job.get("prompt_wav"):            # continuation mode: copies the delivery (e.g. whisper) much more closely
        extra = {"prompt_wav_path": job["prompt_wav"], "prompt_text": job["prompt_text"]}
    wav = model.generate(text=text, reference_wav_path=job.get("reference"),
                         cfg_value=float(job.get("cfg_value", 2.0)),
                         inference_timesteps=int(job.get("timesteps", 10)),
                         denoise=bool(job.get("denoise", False)), **extra)
    sf.write(line["out"], wav, sr)
    print(f"  made {line['out']} ({len(wav) / sr:.1f}s)", flush=True)
