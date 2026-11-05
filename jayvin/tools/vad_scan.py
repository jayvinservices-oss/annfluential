import sys, subprocess, numpy as np
from silero_vad import load_silero_vad, get_speech_timestamps
import torch
m = load_silero_vad()
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
    x = torch.from_numpy(np.frombuffer(raw, np.float32).copy())
    for th in (0.5,):
        ts = get_speech_timestamps(x, m, sampling_rate=16000, threshold=th, min_speech_duration_ms=300, return_seconds=True)
        tot = sum(t['end']-t['start'] for t in ts)
        print(f"{f} th={th}: {len(ts)} speech parts, {tot:.0f}s", [(round(t['start']),round(t['end'])) for t in ts][:12])
