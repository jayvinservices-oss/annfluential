"""Realism test (Ann approved 7 Nov 2026, this test only): premium image + video models on two shots.

Shot A: presenter hand stroking Ace between the ears (storyboard ace-bedtime-1min-test, shot 04).
Shot B: lips + nude gloss close-up, nose down.

Steps per shot: 2 start frames with google/nano-banana-pro (references: real Ace photo / presenter hand + lips
stills), then the first frame animated with kwaivgi/kling-v4.0 (5s, 720p) and google/veo-3.1-fast (6s, no audio).

Planned cost (Replicate pages, 7 Nov 2026): 4 images x $0.15 = $0.60; 2 x Kling 5s 720p ~$0.79 = $1.58;
2 x Veo 3.1 Fast 6s no audio $0.60 = $1.20. Total about $3.38. Hard cap $4.50: the script refuses to start a job
that would take the running estimate over the cap, and appends each paid job to metadata/spend.yaml.

Usage (needs REPLICATE_API_TOKEN):
  python tools/realism_test.py --dry-run     # prints model input schemas and the exact inputs, spends nothing
  python tools/realism_test.py               # runs the test once
Outputs: clips/realism-test-2026-11-07/ (start images, mp4s, inputs.json). Commit and push them.
"""
import argparse, base64, datetime, io, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "prompts" / "reference"
OUT = ROOT / "clips" / "realism-test-2026-11-07"
API = "https://api.replicate.com/v1"
CAP = 4.50
PRICE = {"google/nano-banana-pro": 0.15, "kwaivgi/kling-v4.0": 0.79, "google/veo-3.1-fast": 0.60}

STYLE = ("photorealistic, natural skin texture with visible pores, realistic hands and fingers with correct anatomy, "
         "no plastic skin, no CGI, no identity drift, soft warm lamp light, cosy bedroom at night, shallow depth of field")
SHOTS = {
    "A-hand-ace": {
        "refs": [REF / "ace" / "ace-face-closeup-2026-04-03.jpg", REF / "ace" / "ace-lying-on-blanket-2026-08-18.jpg",
                 REF / "stills" / "hands.png"],
        "image_prompt": ("Use the black-and-white tuxedo cat from the first two reference photos exactly as he is: same "
                         "markings, white chest and muzzle, pink nose, green eyes. He lies relaxed on a soft blanket, "
                         "eyes half closed. One woman's hand with caramel skin, long glossy nude coffin nails and a thin "
                         "gold ring rests between his ears, stroking him. Only the hand and forearm are visible, no face. "
                         "Close-up from slightly above. " + STYLE),
        "video_prompt": ("Very slow, gentle motion. The hand strokes once, slowly, from the top of the cat's head down "
                         "to his neck, then rests. The cat's eyes slowly close and his whiskers relax. Static locked-off "
                         "camera, no zoom, no cuts, calm and sleepy, realistic fur and fingers."),
    },
    "B-lips-gloss": {
        "refs": [REF / "stills" / "pink-glow" / "gloss-anon.png", REF / "stills" / "hands.png"],
        "image_prompt": ("Extreme close-up of a woman's lower face only, framed from just below the nose to the chin, "
                         "no eyes, no nose tip. Caramel skin, full lips with glossy nude-pink lip gloss. Her hand with "
                         "long glossy nude coffin nails and a thin gold ring holds a gloss wand near her lower lip. "
                         "Pink-glow bedroom light. " + STYLE),
        "video_prompt": ("Very slow, gentle motion. The gloss wand glides slowly once across the lower lip, then the lips "
                         "press together softly. Framing stays below the nose the whole time, no eyes. Static locked-off "
                         "camera, no zoom, no cuts, realistic lips and fingers."),
    },
}
START_KEYS = ["start_image", "first_frame_image", "image", "input_image", "image_url"]


def token():
    t = os.environ.get("REPLICATE_API_TOKEN")
    if not t:
        sys.exit("REPLICATE_API_TOKEN is not set in this session.")
    return t


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json",
                                          "Prefer": "wait=60"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def schema(model):
    m = call("GET", f"{API}/models/{model}")
    return m["latest_version"]["openapi_schema"]["components"]["schemas"]["Input"]["properties"]


def data_uri(path, max_side=1024):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def pick(props, key, value, inputs):
    if key in props:
        enum = props[key].get("enum")
        if enum and value not in enum:
            return
        inputs[key] = value


def image_inputs(props, shot):
    inp = {"prompt": shot["image_prompt"]}
    ref_key = next((k for k in ("image_input", "reference_images", "images") if k in props), None)
    if ref_key:
        inp[ref_key] = [data_uri(p) for p in shot["refs"]]
    pick(props, "aspect_ratio", "16:9", inp)
    pick(props, "resolution", "2K", inp)
    pick(props, "output_format", "png", inp)
    return inp


def video_inputs(props, model, prompt, start_uri):
    inp = {"prompt": prompt}
    key = next((k for k in START_KEYS if k in props), None)
    if not key:
        raise SystemExit(f"{model}: no start-image field in schema {sorted(props)}")
    inp[key] = start_uri
    if model.startswith("kwaivgi"):
        pick(props, "duration", 5, inp); pick(props, "resolution", "720p", inp); pick(props, "mode", "standard", inp)
    else:
        pick(props, "duration", 6, inp); pick(props, "resolution", "720p", inp); pick(props, "generate_audio", False, inp)
    pick(props, "aspect_ratio", "16:9", inp)
    pick(props, "negative_prompt", "full face, eyes, extra fingers, deformed hands, fast motion, camera shake", inp)
    return inp


def run(model, inputs):
    p = call("POST", f"{API}/models/{model}/predictions", {"input": inputs})
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(5)
        p = call("GET", p["urls"]["get"])
    if p["status"] != "succeeded":
        raise RuntimeError(f"{model} {p['status']}: {p.get('error')}")
    out = p["output"]
    return out[0] if isinstance(out, list) else out


def save(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, path)
    return path


def ledger(route, clip, seconds, cost):
    now = datetime.datetime.utcnow()
    with open(ROOT / "metadata" / "spend.yaml", "a") as f:
        f.write(f"- date: '{now:%Y-%m-%d}'\n  time: {now:%H:%M}\n  route: {route} (Replicate, realism test)\n"
                f"  clip: {clip}\n  seconds: {seconds}\n  free: false\n  cost_usd: {cost}\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    planned = 2 * 2 * PRICE["google/nano-banana-pro"] + 2 * (PRICE["kwaivgi/kling-v4.0"] + PRICE["google/veo-3.1-fast"])
    print(f"Planned cost ${planned:.2f} (cap ${CAP:.2f})")
    props = {m: schema(m) for m in PRICE}
    if a.dry_run:
        for m, p in props.items():
            print(m, "inputs:", sorted(p))
        for name, shot in SHOTS.items():
            print(name, "image inputs:", {k: (v if k == "prompt" or not isinstance(v, list) else f"{len(v)} refs")
                                          for k, v in image_inputs(props["google/nano-banana-pro"], shot).items()})
        return
    OUT.mkdir(parents=True, exist_ok=True)
    spent, log = 0.0, {}
    for name, shot in SHOTS.items():
        frames = []
        for i in (1, 2):
            if spent + PRICE["google/nano-banana-pro"] > CAP: sys.exit("cap reached")
            url = run("google/nano-banana-pro", image_inputs(props["google/nano-banana-pro"], shot))
            f = save(url, OUT / f"{name}-start-{i}.png"); frames.append(f)
            spent += PRICE["google/nano-banana-pro"]; ledger("nano-banana-pro", f.name, 0, PRICE["google/nano-banana-pro"])
            print(f"{f.name}  spent ${spent:.2f}")
        start = data_uri(frames[0], 1280)
        for model, tag in (("kwaivgi/kling-v4.0", "kling4"), ("google/veo-3.1-fast", "veo31fast")):
            if spent + PRICE[model] > CAP: sys.exit("cap reached")
            inp = video_inputs(props[model], model, shot["video_prompt"], start)
            url = run(model, inp)
            f = save(url, OUT / f"{name}-{tag}.mp4")
            spent += PRICE[model]; ledger(tag, f.name, inp.get("duration", 5), PRICE[model])
            log[f.name] = {k: v for k, v in inp.items() if not str(v).startswith("data:")}
            print(f"{f.name}  spent ${spent:.2f}")
    (OUT / "inputs.json").write_text(json.dumps(log, indent=2))
    print(f"Done. Estimated spend ${spent:.2f}. Files in {OUT}")


if __name__ == "__main__":
    main()
