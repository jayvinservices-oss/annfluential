"""Second voice-clone test (Ann, 5 Nov: the VoxCPM2 clone added a male-sounding artefact; she still wants a clone).
Replicate resemble-ai/chatterbox (open source, MIT). Reference = Ann's cleaned real whisper/soft memo.
Checks the model's input fields first; 4 short lines; caps from config apply; logged in metadata/spend.yaml.
python tools/clone_test.py  -> api-test/clone/*.wav + api-test/clone/report.md
"""
import base64, os, sys, time
from datetime import date, datetime
from pathlib import Path
import requests, yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.config import config  # noqa: E402
from pipeline.providers.router import LEDGER, _ledger, spent_today, spent_usd  # noqa: E402
MODEL, PRICE = "resemble-ai/chatterbox", 0.03
r = config()["generator"]["router"]
h = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}", "Content-Type": "application/json"}
out = ROOT / "api-test/clone"; out.mkdir(parents=True, exist_ok=True)
m = requests.get(f"https://api.replicate.com/v1/models/{MODEL}", headers=h, timeout=30).json()
props = (((m.get("latest_version") or {}).get("openapi_schema") or {}).get("components", {}).get("schemas", {})
         .get("Input", {}).get("properties", {}))
report = [f"# Clone test ({MODEL})", f"- input fields: {', '.join(sorted(props))}"]
text_f = "prompt" if "prompt" in props else "text"
ref_f = next((k for k in ("audio_prompt", "reference_audio", "speaker_wav", "audio") if k in props), None)
if not ref_f:
    (out / "report.md").write_text("\n".join(report + ["- no reference-audio field found; nothing spent"])); sys.exit(1)
refs = {"whisper": ROOT / "audio/voice/real/hi-its-annie-whisper.wav", "soft": ROOT / "audio/voice/reference/annie-soft-prompt.wav"}
lines = [("whisper", "Annie ASMR... Annie ASMR... Annie ASMR."), ("whisper", "Gold ones first. Nice and slow. Listen to this tissue paper."),
         ("soft", "Gold ones first. Nice and slow. Listen to this tissue paper."), ("soft", "Thank you for spending this time with me. Sleep well. Goodnight.")]
for k, (style, text) in enumerate(lines, 1):
    if spent_today() + PRICE > float(r.get("daily_usd", 5)) or spent_usd() + PRICE > float(r.get("budget_usd", 20)):
        sys.exit("cap reached")
    ref = "data:audio/wav;base64," + base64.b64encode(refs[style].read_bytes()).decode()
    inp = {text_f: text, ref_f: ref}
    if "exaggeration" in props: inp["exaggeration"] = 0.3
    if "cfg_weight" in props: inp["cfg_weight"] = 0.4
    p = requests.post(f"https://api.replicate.com/v1/models/{MODEL}/predictions", headers=h, json={"input": inp}, timeout=120).json()
    if "urls" not in p:
        report.append(f"- line {k}: not started: {str(p)[:200]}"); time.sleep(15); continue
    while p.get("status") not in ("succeeded", "failed", "canceled"):
        time.sleep(2); p = requests.get(p["urls"]["get"], headers=h, timeout=60).json()
    if p["status"] != "succeeded":
        report.append(f"- line {k}: {p['status']} {p.get('error')}"); continue
    url = p["output"][0] if isinstance(p["output"], list) else p["output"]
    f = out / f"{k}-{style}.wav"; f.write_bytes(requests.get(url, timeout=120).content)
    LEDGER.write_text(yaml.safe_dump(_ledger() + [{"date": date.today().isoformat(), "time": datetime.now().strftime("%H:%M"),
        "route": "chatterbox (Replicate)", "clip": f"clone/{f.name}", "seconds": 0, "free": False, "cost_usd": PRICE}], sort_keys=False))
    report.append(f"- line {k} ({style}): {f.name}, run {p.get('metrics', {}).get('predict_time', '?')} s")
    time.sleep(5)
report.append(f"- spent today ${spent_today():.2f}")
(out / "report.md").write_text("\n".join(report) + "\n"); print("\n".join(report))
