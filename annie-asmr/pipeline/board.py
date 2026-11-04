"""Phone-friendly production board: numbers, to-dos, every video's status and, for manual mode,
every prompt with a copy button and the exact file name to save it as.

  python -m pipeline board   -> renders/board.html (Claude publishes it as a private page)
"""
from __future__ import annotations

import html
from datetime import date, datetime
from zoneinfo import ZoneInfo

import yaml

from .assemble import find_voice_file, render_path
from .config import EPISODES, METADATA, RENDERS, ROOT, config
from .episode import load_episode, used_shot_ids, voice_lines
from .generate import clips_for_shot
from .metadata import upload_record
from .prompts import build_prompt

e = html.escape


def _load(name: str) -> dict:
    p = METADATA / name
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def _episodes() -> list[dict]:
    eps = []
    for p in sorted(EPISODES.glob("*.yaml")):
        try:
            eps.append(load_episode(str(p)))
        except SystemExit:
            continue
    return sorted(eps, key=lambda ep: (ep.get("priority") or 99, str(ep.get("made_by") or "")))


def _drive_link(key: str, label: str) -> str:
    url = (_load("todo.yaml").get("drive") or {}).get(key) or (_load("todo.yaml").get("drive") or {}).get("clips")
    return f'<a href="{e(url)}">{e(label)}</a>' if url else f"<code>{e(label)}</code>"


def _chip(text: str, kind: str) -> str:
    return f'<span class="chip {kind}">{e(text)}</span>'


def _episode_card(ep: dict, takes: int) -> str:
    slug = ep["slug"]
    shots = used_shot_ids(ep)
    have = sum(1 for s in shots if clips_for_shot(slug, s))
    lines = voice_lines(ep)
    have_v = sum(1 for l in lines if find_voice_file(slug, l["id"]))
    rendered = render_path(slug).exists()
    uploaded = upload_record(slug).exists()
    minutes = sum(float(s["minutes"]) for s in ep["segments"])
    chips = [
        _chip(f"clips {have}/{len(shots)}", "ok" if have == len(shots) else "todo"),
        _chip(f"voice {have_v}/{len(lines)}", "ok" if have_v == len(lines) else "todo"),
        _chip("rendered" if rendered else "not rendered", "ok" if rendered else "todo"),
        _chip("private draft" if uploaded else "not uploaded", "ok" if uploaded else "todo"),
    ]
    dates = []
    if ep.get("made_by"):
        late = not rendered and date.fromisoformat(str(ep["made_by"])) < date.today()
        dates.append(f"make by {date.fromisoformat(str(ep['made_by'])):%a %d %b}" + (" (late)" if late else ""))
    if ep.get("publish_after"):
        dates.append(f"publish from {date.fromisoformat(str(ep['publish_after'])):%a %d %b}")
    chapters = "".join(f"<li><span class=\"num\">{float(s['minutes']):g} min</span> {e(s['chapter'])}</li>"
                       for s in ep["segments"])
    shot_rows = []
    for sid in shots:
        prompt, negative = build_prompt(ep, sid)
        names = " ".join(f"<code>{e(sid)}__t{k}.mp4</code>" for k in range(1, takes + 1))
        done = bool(clips_for_shot(slug, sid))
        shot_rows.append(f"""
        <div class="shot{' done' if done else ''}">
          <div class="shot-head"><strong>{e(sid)}</strong>{_chip('have it', 'ok') if done else ''}</div>
          <div class="label">Save as</div><div class="names">{names}</div>
          <div class="copyrow"><div class="label">Prompt</div><button type="button" class="copy" data-target="p-{e(slug)}-{e(sid)}">Copy prompt</button></div>
          <pre id="p-{e(slug)}-{e(sid)}">{e(prompt)}</pre>
          <details><summary>Negative prompt (things to avoid)</summary>
            <div class="copyrow"><span></span><button type="button" class="copy" data-target="n-{e(slug)}-{e(sid)}">Copy</button></div>
            <pre id="n-{e(slug)}-{e(sid)}">{e(negative)}</pre></details>
        </div>""")
    voice = "".join(f"<li><code>{e(l['id'])}</code> <span class=\"muted\">{e(l['style'])}, {l['at']:.0f}s</span> {e(l['text'])}</li>"
                    for l in lines)
    return f"""
    <article class="ep" id="{e(slug)}">
      <header>
        <div class="eyebrow">{e(ep['_theme']['name'])} · {minutes:g} min</div>
        <h3>{e(ep['title'])}</h3>
        <div class="dates">{' · '.join(dates) if dates else 'date not set'}</div>
        <div class="chips">{''.join(chips)}</div>
      </header>
      <details><summary>Chapters</summary><ol class="chapters">{chapters}</ol></details>
      <details><summary>Voice lines ({len(lines)})</summary><ul class="voice">{voice}</ul></details>
      <details class="prompts"><summary>Clip prompts for manual mode ({len(shots)} shots × {takes} takes)</summary>
        <p class="hint">Make each clip in your video app from the reference image, download it, rename it exactly as shown,
        and upload it to Google Drive: {_drive_link(f"clips/{slug}", f"Annie ASMR › clips › {slug}")}.</p>
        {''.join(shot_rows)}
      </details>
    </article>"""


def _img_data(path, width: int, quality: int = 78) -> str:
    """Small JPEG data URI for a brand draft, so the private page carries its own pictures."""
    import base64
    import io
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


WHO = {"claude": ("Claude does it", "ok"), "ann": ("You", "todo"), "access": ("Access for Claude", "todo")}


def _rebrand_section() -> str:
    acts_p = ROOT / "brand" / "rebrand-actions.yaml"
    if not acts_p.exists():
        return ""
    acts = [a for a in (yaml.safe_load(acts_p.read_text()) or []) if a.get("group") != "done"]
    assets = ROOT / "brand" / "assets"
    pics = ""
    try:
        pics = (f'<figure><img src="{_img_data(assets / "banner-preview-safe-area.jpg", 900)}" alt="Draft channel banner: '
                f'Annie ASMR over glossy lips and long nails on a cocoa background, safe areas outlined"><figcaption>Banner '
                f'(yellow box: the part every phone and TV shows)</figcaption></figure>'
                f'<figure><img src="{_img_data(assets / "banner-v2-preview-safe-area.jpg", 900)}" alt="Banner v2: lips on the right, '
                f'name on the left"><figcaption>Banner v2: lips on the right, clear of the profile picture</figcaption></figure>'
                f'<p class="note">Cartoon duo option (you in grey with locs, your friend in red and pink): '
                f'<a href="https://www.canva.com/M/MAHZ4Ndf7ec">open in Canva</a>. Realistic duo (the avatars\' faces): '
                f'<a href="https://www.canva.com/M/MAHZ4Lq0kqs">open in Canva</a>. Avatar stills (anonymous, generated): '
                f'<a href="https://www.canva.com/M/MAHZ4_ZnBo4">Annie gloss</a> · <a href="https://www.canva.com/M/MAHZ40zAVZc">Annie gum</a> · '
                f'<a href="https://www.canva.com/M/MAHZ43MLJNc">Bestie gloss</a> · <a href="https://www.canva.com/M/MAHZ401mkO4">duo split screen</a>. '
                f'All stills, named: <a href="https://www.canva.com/folder/FAHZ5ZSZi5g">Canva folder</a> · '
                f'<a href="https://drive.google.com/drive/folders/1uUA218LYI9TjHZ9QNQQJA5Tv8cF3s5eY">Drive › Annie ASMR › avatars</a></p>'
                f'<div class="pics2"><figure><img src="{_img_data(assets / "profile-800.png", 300)}" alt="Draft profile picture: '
                f'glossy lips and gloss tube in a gold ring"><figcaption>Profile picture</figcaption></figure>'
                f'<figure><img src="{_img_data(assets / "thumbnail-template-gloss.jpg", 640)}" alt="Draft thumbnail: 300 Layers, '
                f'Gloss Lab"><figcaption>Thumbnail style</figcaption></figure></div>')
    except FileNotFoundError:
        pics = '<p class="note muted">Artwork drafts not built yet (python tools/brand_assets.py).</p>'
    retitle = ""
    rt_p = ROOT / "brand" / "retitles.yaml"
    if rt_p.exists():
        cards = []
        for v in yaml.safe_load(rt_p.read_text()) or []:
            img = assets / "retitle" / f"{v.get('file')}.jpg"
            pic = (f'<img src="{_img_data(img, 360, 72)}" alt="Draft thumbnail: {e(" ".join(v["words"]))}">'
                   if v.get("file") and img.exists() else '<div class="nopic">thumbnail to come</div>')
            desc = e(v.get("description", "")).replace("\n", "<br>")
            cards.append(f'<li>{pic}<b>{e(v["new"])}</b><span class="muted">was: {e(v["old"])}</span>'
                         f'<details><summary>Description</summary><p class="note">{desc}</p></details></li>')
        retitle = (f'<details class="rt"><summary>Old videos: new titles, descriptions and thumbnails ({len(cards)})</summary>'
                   f'<p class="note muted">Round 2, after your notes: catchier, built on search words, not flirty. Your real videos, so no AI wording.</p><ul class="rtl">{"".join(cards)}</ul></details>')
    links = ('<div class="dl" hidden><button type="button" class="copy" data-file="brand/banner-2560x1440.jpg">Save full-size banner</button>'
             '<button type="button" class="copy" data-file="brand/banner-v2-2560x1440.jpg">Save banner v2</button>'
             '<button type="button" class="copy" data-file="brand/profile-800.png">Save profile picture</button></div>'
             '<p class="note">All documents: <a href="https://drive.google.com/drive/folders/1kkFfh3zVuPJBCUanP0iua_ePdmT-IyoW">Drive › Annie ASMR › brand</a> '
             '(style guide, rebrand plan and new titles, channel copy and SEO, monetisation plan)</p>')
    GROUPS = [("signin", "Your sign-ins"),
              ("approved", "Approved: Claude does these as soon as the sign-in works"),
              ("studio", "Only you, in YouTube Studio (about 2 minutes each)"),
              ("review", "Needs your eye again")]
    rows = []
    last_group = None
    for a in sorted(acts, key=lambda a: [g for g, _ in GROUPS].index(a.get("group", "review"))):
        if a.get("group") != last_group:
            last_group = a.get("group")
            rows.append(f'<li class="grp">{e(dict(GROUPS).get(last_group, ""))}</li>')
        who, kind = WHO.get(a["who"], (a["who"], "todo"))
        chips = f'<span class="chip {kind}">{e(who)}</span>'
        if a.get("needs_access"):
            chips += '<span class="chip todo">after access</span>'
        rows.append(f"""<li class="act" data-id="{e(a['id'])}">
  <div class="act-head"><strong>{e(a['title'])}</strong><div class="chips">{chips}<span class="chip state" data-state>waiting</span></div></div>
  <details><summary>What this means</summary><p class="note">{e(a['detail'])}</p></details>
  <div class="act-btns" hidden><button type="button" class="yes" data-v="yes">Yes</button><button type="button" class="no" data-v="later">Not now</button>
  <input type="text" class="act-note" maxlength="300" placeholder="Note for Claude (optional)" aria-label="Note for Claude about {e(a['title'])}"></div>
</li>""")
    return f"""
  <section id="rebrand">
    <h2>Channel rebrand</h2>
    <p class="note">Glossy, slow, up-close ASMR for sleep: gum, gloss, nails, crafts. The full style guide, plan,
    new titles, channel copy and monetisation plan are in Drive (link below). Tap Yes on what Claude may do; Claude reads your answers.</p>
    {pics}
    {links}

    <p class="note muted" id="rb-status">Loading your answers…</p>
    <ul class="acts">{''.join(rows)}</ul>
  </section>"""


NEEDS = [
    ("Full-size stills (the Drive copies are 199-pixel previews, too small to animate)",
     "In Canva, open each of these, then Share > Download > PNG, and put them in Drive > Annie ASMR > avatars "
     "(each is under 10 MB, so Claude can fetch them): presenter gum MAHZ6bGoPjI, hands MAHZ6W0Igdc, gloss MAHZ43MLJNc, "
     "duo split screen MAHZ401mkO4. Links are in the Canva folder 'Annie ASMR - Avatar stills'."),
    ("Video clips: pick one way",
     "Free: make the 10-second clips yourself in Kling (free daily credits) or Google Flow / Veo, starting from the still "
     "named in the storyboard and pasting the shot's prompt from the Videos section; keep the tool's own sound on (Claude "
     "uses it to time the real chews). Upload to Drive > Annie ASMR > clips > <video>. Hands-off: add a Replicate API "
     "token (REPLICATE_API_TOKEN) in the environment settings and Claude makes every clip, with a hard $20 cap built in. "
     "A 60-minute video needs only about 5 short clips (looped and slowed), roughly $3 to $6 a video at Kling-type "
     "prices, so $20 covers about 4 to 6 videos."),
    ("Sounds for Christmas and lip gloss",
     "Gum, crackling and knuckle sounds are ready (cut from your videos). Still missing: paper crinkle, tape peel, ribbon "
     "pull, tissue rustle, box tapping, glass bauble taps, pine and garland rustle, pen scribble, scissors, sticker peel, "
     "washi tear, rhinestone pour and tray, tweezer clicks, lip gloss tube and wand. Easiest: record 1 minute of each on "
     "your phone in a quiet room, close to the mic, and drop them in Drive > Annie ASMR > sfx. Or keep the video tool's own "
     "sound for these."),
    ("Voice (optional for the first video)",
     "'No talking' is the most searched add-on, so the first gum video can go out with no talking. For the whisper "
     "videos: a 1-minute whispered voice memo in a quiet room, to Drive > Annie ASMR > source."),
]


def _storyboard_section() -> str:
    p = METADATA / "storyboards.yaml"
    if not p.exists():
        return ""
    vids = yaml.safe_load(p.read_text()) or []
    blocks = []
    for v in vids:
        rows = "".join(
            f"<tr><td class=\"n\">{e(r['start'])}</td><td><b>{e(r['chapter'])}</b> ({r['minutes']} min)<br>"
            f"<span class=\"muted\">shots: {e(', '.join(r['shots']))}<br>sound: {e('; '.join(r['sounds']) or 'none')}"
            + (f"<br>voice: {e(' / '.join(r['voice']))}" if r['voice'] else "") + "</span></td></tr>"
            for r in v["rows"])
        blocks.append(f"<details><summary>{e(v['title'])}</summary><div class=\"scroll\"><table><tbody>{rows}"
                      f"</tbody></table></div></details>")
    needs = "".join(f"<li><b>{e(t)}</b><br><span class=\"muted\">{e(d)}</span></li>" for t, d in NEEDS)
    return f"""
  <section id="storyboards">
    <h2>Storyboards</h2>
    <p class="note">Presenter: the caramel-skinned character. Each chapter: when it starts, which shots, which sound, any
    whispers. Full version: brand/storyboards.md (and Drive > Annie ASMR > brand).</p>
    {''.join(blocks)}
    <h3 style="margin-top:16px">What Claude needs to make the videos</h3>
    <ol class="needs">{needs}</ol>
  </section>"""


def build_board() -> str:
    cfg = config()
    ch = cfg["channel"]
    stats = _load("channel-stats.yaml")
    todo = _load("todo.yaml")
    takes = int(cfg["generator"].get("takes_per_shot", 2))
    goal = float(ch["goal_watch_hours"])
    hours = float(stats.get("watch_hours_365", ch["baseline"]["watch_hours"]))
    subs = int(stats.get("subscribers", ch["baseline"]["subscribers"]))
    target = date.fromisoformat(str(ch["target_date"]))
    days = max(1, (target - date.today()).days)
    need = (goal - hours) / days
    l28 = stats.get("last_28_days") or {}
    p28 = stats.get("previous_28_days") or {}
    pace = float(l28.get("watch_hours", 0)) / 28
    pct = min(100, hours / goal * 100)
    now = datetime.now(ZoneInfo(ch.get("timezone", "America/Toronto")))

    def todo_list(items):
        return "".join(f'<li><span class="box" aria-hidden="true"></span><span>{e(t["text"])}</span></li>'
                       for t in items or [] if not t.get("done"))

    top = "".join(f"<tr><td>{e(v['title'])}</td><td class=\"n\">{v['views']}</td><td class=\"n\">{v['hours']:g}</td></tr>"
                  for v in stats.get("top_videos", []))
    lv = stats.get("latest_video") or {}
    eps = _episodes()
    def short(ep):
        n = ep["_theme"]["name"].split(" (")[0].split(" - ")[-1]
        return n.split(",")[0] if len(n) > 24 else n
    nav = "".join(f'<a href="#{e(ep["slug"])}">{e(short(ep))}</a>' for ep in eps)
    cards = "".join(_episode_card(ep, takes) for ep in eps)
    mode = cfg["generator"]["provider"]

    return f"""<title>Annie ASMR Board</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gloock&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one narrow column built for a phone; numbers first, then to-dos, then each video as a card. */
:root {{
  --bg: #f7eeea; --surface: #fffaf8; --ink: #2b1813; --muted: #7b5e55; --line: #e8d5ce;
  --accent: #a8475f; --accent-soft: #f3dde2; --ok: #2f7553; --ok-soft: #dcefe4; --todo: #8a5a1c; --todo-soft: #f6e7cf;
  --display: "Gloock", Georgia, "Times New Roman", serif;
  --body: "Figtree", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #170d0a; --surface: #22140f; --ink: #f4e7e1; --muted: #b89c92; --line: #3b2720;
  --accent: #e98fa5; --accent-soft: #3d1f27; --ok: #7fd0a4; --ok-soft: #173326; --todo: #e9b56c; --todo-soft: #3a2a14; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #170d0a; --surface: #22140f; --ink: #f4e7e1; --muted: #b89c92; --line: #3b2720;
  --accent: #e98fa5; --accent-soft: #3d1f27; --ok: #7fd0a4; --ok-soft: #173326; --todo: #e9b56c; --todo-soft: #3a2a14; color-scheme: dark }}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.5 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 20px 48px }}
.wrap {{ max-width: 680px; margin: 0 auto; display: grid; gap: 28px }}
h1, h2, h3 {{ font-family: var(--display); font-weight: 400; margin: 0; text-wrap: balance; letter-spacing: .005em }}
h1 {{ font-size: 2.1rem; line-height: 1.1 }}
h2 {{ font-size: 1.45rem; margin-bottom: 12px }}
h3 {{ font-size: 1.15rem; line-height: 1.25 }}
.eyebrow, .label {{ font-size: .72rem; letter-spacing: .09em; text-transform: uppercase; color: var(--muted); font-weight: 600 }}
.muted {{ color: var(--muted) }}
.top {{ display: grid; gap: 6px }}
.updated {{ color: var(--muted); font-size: .85rem }}
.goal {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px; display: grid; gap: 14px }}
.meter {{ height: 10px; background: var(--accent-soft); border-radius: 99px; overflow: hidden }}
.meter span {{ display: block; height: 100%; background: var(--accent); border-radius: 99px }}
.figs {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 18px }}
.fig b {{ display: block; font-family: var(--display); font-weight: 400; font-size: 1.6rem; line-height: 1.1; font-variant-numeric: tabular-nums }}
.fig span {{ font-size: .82rem; color: var(--muted) }}
.note {{ font-size: .9rem; margin: 0; max-width: 62ch }}
nav {{ display: flex; flex-wrap: wrap; gap: 8px }}
nav a {{ color: var(--accent); text-decoration: none; border: 1px solid var(--line); border-radius: 99px; padding: 4px 12px; font-size: .85rem; background: var(--surface) }}
.todo {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 10px }}
.todo li {{ display: grid; grid-template-columns: 18px minmax(0, 1fr); gap: 10px; align-items: start }}
.box {{ width: 16px; height: 16px; border: 2px solid var(--accent); border-radius: 4px; margin-top: 3px }}
.todo li.done {{ color: var(--muted); text-decoration: line-through }}
.todo li.done .box {{ background: var(--accent) }}
.two {{ display: grid; gap: 22px }}
.ep {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px; display: grid; gap: 12px; scroll-margin-top: 16px }}
.ep header {{ display: grid; gap: 6px }}
.dates {{ font-size: .88rem; color: var(--muted) }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px }}
.chip {{ font-size: .75rem; font-weight: 600; padding: 2px 9px; border-radius: 99px }}
.chip.ok {{ background: var(--ok-soft); color: var(--ok) }}
.chip.todo {{ background: var(--todo-soft); color: var(--todo) }}
details {{ border-top: 1px solid var(--line); padding-top: 10px }}
summary {{ cursor: pointer; font-weight: 600; color: var(--ink) }}
summary:focus-visible, button:focus-visible, nav a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px }}
.chapters, .voice {{ margin: 10px 0 0; padding-left: 20px; display: grid; gap: 4px }}
.num {{ font-variant-numeric: tabular-nums; color: var(--muted); font-size: .85rem; display: inline-block; min-width: 4.5em }}
a {{ color: var(--accent) }}
.hint {{ font-size: .88rem; color: var(--muted); max-width: 62ch }}
.shot {{ border: 1px solid var(--line); border-radius: 10px; padding: 12px; margin-top: 10px; display: grid; gap: 6px; min-width: 0 }}
.shot.done {{ opacity: .7 }}
.shot-head {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap }}
.names {{ display: flex; flex-wrap: wrap; gap: 6px }}
code, pre {{ font-family: var(--mono); font-size: .8rem }}
code {{ background: var(--accent-soft); padding: 1px 6px; border-radius: 5px; overflow-wrap: anywhere }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 10px; line-height: 1.45 }}
.copyrow {{ display: flex; justify-content: space-between; align-items: center; gap: 8px }}
button.copy {{ font: 600 .82rem var(--body); color: var(--surface); background: var(--accent); border: 0; border-radius: 8px; padding: 7px 12px; cursor: pointer; min-height: 34px }}
table {{ width: 100%; border-collapse: collapse; font-size: .88rem }}
td, th {{ padding: 6px 4px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top }}
th {{ font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted) }}
td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap }}
.scroll {{ overflow-x: auto }}
figure {{ margin: 0; display: grid; gap: 4px }}
figure img {{ width: 100%; height: auto; border-radius: 10px; display: block }}
figcaption {{ font-size: .8rem; color: var(--muted) }}
.pics2 {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 12px; margin-top: 12px; align-items: start }}
#rebrand > figure {{ margin-top: 4px }}
.dl {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 }}
.rt {{ margin-top: 12px }}
.needs {{ display: grid; gap: 10px; padding-left: 20px; font-size: .9rem }}
#storyboards details {{ margin-top: 8px }}
.rtl {{ list-style: none; padding: 0; margin: 10px 0 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px }}
.rtl li {{ display: grid; gap: 4px; font-size: .82rem; min-width: 0 }}
.rtl img {{ width: 100%; height: auto; border-radius: 8px; display: block }}
.rtl .muted {{ font-size: .75rem; overflow-wrap: anywhere }}
.nopic {{ aspect-ratio: 16 / 9; border: 1px dashed var(--line); border-radius: 8px; display: grid; place-items: center; color: var(--muted); font-size: .75rem }}
.grp {{ font-family: var(--display); font-size: 1.15rem; margin-top: 10px }}
.acts {{ list-style: none; margin: 14px 0 0; padding: 0; display: grid; gap: 10px }}
.act {{ background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px; display: grid; gap: 8px }}
.act-head {{ display: grid; gap: 6px }}
.act details {{ border-top: 0; padding-top: 0 }}
.act summary {{ font-weight: 500; color: var(--muted); font-size: .88rem }}
.act-btns {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center }}
.act-btns button {{ font: 600 .9rem var(--body); border-radius: 8px; padding: 8px 16px; min-height: 40px; cursor: pointer; border: 1px solid var(--accent) }}
.act-btns .yes {{ background: var(--accent); color: var(--surface) }}
.act-btns .no {{ background: transparent; color: var(--accent) }}
.act-btns button[aria-pressed="true"] {{ outline: 2px solid var(--ink); outline-offset: 2px }}
.act-note {{ flex: 1 1 180px; min-width: 0; font: .88rem var(--body); padding: 8px 10px; border: 1px solid var(--line); border-radius: 8px; background: var(--bg); color: var(--ink) }}
.chip.state.yes {{ background: var(--ok-soft); color: var(--ok) }}
.chip.state.later {{ background: var(--todo-soft); color: var(--todo) }}
.chip.state {{ background: var(--accent-soft); color: var(--accent) }}
@media (min-width: 640px) {{ .figs {{ grid-template-columns: repeat(4, minmax(0, 1fr)) }} }}
</style>

<div class="wrap">
  <div class="top">
    <div class="eyebrow">Annie ASMR · {e(ch['handle'])}</div>
    <h1>Production board</h1>
    <div class="updated">Updated {now:%a %d %b, %-I:%M %p} Toronto · clips mode: {e(mode)}</div>
  </div>

  <section class="goal" aria-label="Partner Program goal">
    <div>
      <div class="label">Public watch hours, last 365 days</div>
      <div class="fig"><b>{hours:,.0f} of {goal:,.0f}</b></div>
    </div>
    <div class="meter" role="img" aria-label="{pct:.0f}% of 4,000 hours"><span style="width:{pct:.1f}%"></span></div>
    <div class="figs">
      <div class="fig"><b>{subs:,}</b><span>subscribers ({int(ch['goal_subscribers']):,} needed{', met' if subs >= int(ch['goal_subscribers']) else ''})</span></div>
      <div class="fig"><b>{float(l28.get('watch_hours', 0)):g} h</b><span>last 28 days ({pace:.1f} a day; before: {float(p28.get('watch_hours', 0)):g} h)</span></div>
      <div class="fig"><b>{need:,.0f} h</b><span>a day needed to reach 4,000 by {target:%d %b}</span></div>
      <div class="fig"><b>{e(str(l28.get('avd', '')))}</b><span>average view, last 28 days (before {e(str(p28.get('avd', '')))})</span></div>
    </div>
    <p class="note">At the current pace the 17 January date is out of reach; the gap is about {need / pace if pace else 0:,.0f} times the current daily hours.
    The 365-day window keeps rolling, so every hour from new long videos still counts toward the goal.
    One video, the gum popping and crackling one, brought {sum(v['hours'] for v in stats.get('top_videos', [])[:1]):g} of the
    {float(l28.get('watch_hours', 0)):g} hours this month: make more like it, and longer.</p>
  </section>

  <nav aria-label="Videos">{nav}</nav>

{_storyboard_section()}

  <section>
    <h2>Waiting on you</h2>
    <p class="note muted">Drive folders (in the jayvin.services account): {_drive_link("source", "source")} ·
      {_drive_link("sfx", "sfx")} · {_drive_link("clips", "clips")}</p>
    <ul class="todo">{todo_list(todo.get('ann'))}</ul>
  </section>

  <section>
    <h2>Claude is working on</h2>
    <ul class="todo">{todo_list(todo.get('claude'))}</ul>
  </section>

  <section>
    <h2>Videos</h2>
    <div class="two">{cards}</div>
  </section>

  <section>
    <h2>What viewers watch</h2>
    <p class="note muted">Last 28 days, from YouTube Studio ({e(str(stats.get('updated', '')))}).
    Latest upload: {e(lv.get('title', ''))}: {lv.get('views', '')} views, {lv.get('ctr', '')}% click rate, {e(str(lv.get('avd', '')))} average view. {e(lv.get('note', ''))}</p>
    <div class="scroll"><table><thead><tr><th>Video</th><th class="n">Views</th><th class="n">Hours</th></tr></thead><tbody>{top}</tbody></table></div>
  </section>
</div>

<script>
document.addEventListener("click", (ev) => {{
  const b = ev.target.closest("button.copy");
  if (!b) return;
  const el = document.getElementById(b.dataset.target);
  const done = (msg) => {{ const t = b.textContent; b.textContent = msg; setTimeout(() => b.textContent = t, 1600); }};
  const select = () => {{ const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }};
  try {{
    navigator.clipboard.writeText(el.textContent).then(() => done("Copied"), () => {{ select(); done("Selected: copy it"); }});
  }} catch (err) {{ select(); done("Selected: copy it"); }}
}});
</script>
<script>
(async () => {{
  const box = document.querySelector(".dl");
  if (!box) return;
  let dl = null;
  try {{ dl = await claude.use("downloads"); }} catch (err) {{ dl = null; }}
  if (!dl) return;
  box.hidden = false;
  box.addEventListener("click", async ev => {{
    const b = ev.target.closest("button[data-file]");
    if (!b) return;
    const label = b.textContent;
    try {{
      const blob = await (await fetch(b.dataset.file)).blob();
      await dl.save({{filename: b.dataset.file.split("/").pop(), data: blob}});
      b.textContent = "Saved";
    }} catch (err) {{ b.textContent = err && err.code === "declined" ? label : "Could not save"; }}
    setTimeout(() => b.textContent = label, 2000);
  }});
}})();
</script>
<script>
(async () => {{
  const status = document.getElementById("rb-status");
  if (!status) return;
  const label = {{yes: "yes, go ahead", later: "not now"}};
  const show = (li, d) => {{
    const st = li.querySelector("[data-state]");
    const v = d && d.decision;
    st.textContent = v ? label[v] || v : "waiting";
    st.className = "chip state" + (v ? " " + v : "");
    li.querySelectorAll(".act-btns button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.v === v)));
    const n = li.querySelector(".act-note");
    if (d && typeof d.note === "string" && document.activeElement !== n) n.value = d.note;
  }};
  let db = null;
  try {{ db = await claude.use("db"); }} catch (err) {{ db = null; }}
  if (!db) {{ status.textContent = "Open this page signed in to claude.ai to answer here."; return; }}
  const items = [...document.querySelectorAll("li.act")];
  const timer = setTimeout(() => {{ status.textContent = "Your answers are slow to load. You can still tap; it saves when the connection is back."; }}, 10000);
  items.forEach(li => li.querySelector(".act-btns").hidden = false);
  db.collection("approvals").onSnapshot(snap => {{
    clearTimeout(timer);
    const byId = {{}};
    snap.docs.forEach(d => byId[d.id] = d.data());
    items.forEach(li => show(li, byId[li.dataset.id]));
    const yes = snap.docs.filter(d => (d.data() || {{}}).decision === "yes").length;
    status.textContent = `${{yes}} of ${{items.length}} approved. Tap Yes or Not now; add a note if you want something changed.`;
  }}, err => {{ clearTimeout(timer); status.textContent = "Could not load answers (" + err.code + ")."; }});
  const save = async (li, patch) => {{
    const ref = db.collection("approvals").doc(li.dataset.id);
    const note = li.querySelector(".act-note").value.trim();
    try {{
      await ref.set({{decision: patch.decision ?? (li.querySelector('[aria-pressed="true"]')?.dataset.v || null), note, at: new Date().toISOString()}});
    }} catch (err) {{ status.textContent = "Not saved (" + (err.code || "error") + "). Try again in a moment."; }}
  }};
  document.addEventListener("click", ev => {{
    const b = ev.target.closest(".act-btns button");
    if (b) save(b.closest("li.act"), {{decision: b.dataset.v}});
  }});
  document.addEventListener("change", ev => {{
    if (ev.target.classList.contains("act-note")) save(ev.target.closest("li.act"), {{}});
  }});
}})();
</script>
"""


def write_board() -> str:
    out = RENDERS / "board.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_board())
    print(f"Board: {out}")
    return str(out)
