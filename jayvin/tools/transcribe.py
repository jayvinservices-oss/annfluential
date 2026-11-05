import sys
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8")
for f in sys.argv[1:]:
    import subprocess, numpy as np
    a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
    segs, _ = m.transcribe(a, vad_filter=False, no_speech_threshold=0.6, condition_on_previous_text=False)
    out = [(round(s.start,1), round(s.end,1), s.text.strip(), round(s.no_speech_prob,2), round(s.avg_logprob,2)) for s in segs]
    print("==", f)
    for o in out: print("  ", o)
