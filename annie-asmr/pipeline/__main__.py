"""Annie ASMR pipeline.  Run from the annie-asmr folder:  python -m pipeline <command> ...

  new <theme> <slug>        start an episode plan with a fresh variation
  prompts <slug>            write the prompt sheet for review
  generate <slug>           make clips with the chosen video generator
  voice <slug>              make the whisper/talking lines in your cloned voice
  assemble <slug>           stitch, loop, crossfade, level audio, chapters -> renders/<slug>.mp4
  trailer <slug> --start S  vertical Short cut that points to the long video
  thumb <slug> [--at S]     thumbnail frame, from the opening shot unless --at is given
  metadata <slug>           build title/description/chapters and run the honesty checks
  check <slug>              run the checks only
  upload <slug> [--short]   upload as a PRIVATE draft (you publish in Studio)
  comments-pull             export unanswered comments for reply drafts
  comments-post <file>      post replies you approved
  whoami                    check which channel the YouTube sign-in reaches
  analyze <video> ...       study your best videos cut by cut (frames, measurements, opening)
  voice-ref <video> --start --end --name   cut a clean voice sample for cloning
  report                    weekly hours / views / retention report
  status                    what is done for every episode
  board                     phone-friendly production board -> renders/board.html
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

import yaml

from .config import EPISODES, RENDERS, VOICE
from .episode import load_episode, load_theme, used_shot_ids, voice_lines


def cmd_new(a):
    from .variety import pick_fresh_variation
    theme = load_theme(a.theme)
    path = EPISODES / f"{a.slug}.yaml"
    if path.exists():
        raise SystemExit(f"{path} already exists")
    from .config import config
    brand = (config().get("opening") or {}).get("brand_whisper", "Annie ASMR... Annie ASMR... Annie ASMR.")
    shot_ids = list(theme["shots"])
    chapters = theme.get("chapter_ideas") or ["Part 1", "Part 2", "Part 3"]
    per = round(a.minutes / len(chapters), 1)
    segments = []
    for n, ch in enumerate(chapters):
        segments.append({
            "id": f"s{n + 1}", "chapter": ch, "minutes": per,
            "shots": [shot_ids[n % len(shot_ids)], shot_ids[(n + 1) % len(shot_ids)]],
            "sound_bed": "audio/sfx/CHOOSE-A-SOUND.wav",
            "voice": [{"at": 3, "text": brand, "style": "brand"}] if n == 0 else [],
        })
    plan = {
        "slug": a.slug, "theme": a.theme,
        "title": "TODO: write a title that says exactly what is in the video",
        "description": "TODO: two honest sentences about what happens in this video.",
        "made_by": None, "publish_after": None,
        "variation": pick_fresh_variation(a.theme),
        "objects": [], "sounds": list(theme.get("sounds", []))[:4], "tags": [],
        "segments": segments,
    }
    EPISODES.mkdir(exist_ok=True)
    path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True, width=100))
    print(f"Created {path}. Edit the TODOs, chapters, shots and sound beds, then run: python -m pipeline check {a.slug}")


def cmd_prompts(a):
    from .config import PROMPTS
    from .prompts import prompt_sheet
    ep = load_episode(a.slug)
    out = PROMPTS / "out" / f"{ep['slug']}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(prompt_sheet(ep))
    print(out.read_text() if a.show else f"Prompt sheet: {out}")


def cmd_generate(a):
    from .generate import generate
    generate(load_episode(a.slug), provider_name=a.provider, takes=a.takes, only=a.only, dry_run=a.dry_run)


def cmd_voice(a):
    from .voice import make_voice
    make_voice(load_episode(a.slug), provider=a.provider, redo=a.redo)


def cmd_assemble(a):
    from .assemble import assemble
    assemble(load_episode(a.slug), allow_missing_voice=a.allow_missing_voice, fast=a.fast, fresh=a.fresh)


def cmd_trailer(a):
    from .assemble import trailer
    trailer(load_episode(a.slug), a.start, a.seconds, a.x)


def cmd_thumb(a):
    from .assemble import thumbnail
    thumbnail(load_episode(a.slug), a.at)


def cmd_metadata(a, write=True):
    from .metadata import build, build_short, meta_path, print_checks
    ep = load_episode(a.slug)
    meta = build(ep)
    if getattr(a, "short", False):
        meta = build_short(ep)
    print(f"Title: {meta['title']}\n")
    if write:
        print(meta["description"] + "\n")
    ok = print_checks(meta)
    print(f"\nSaved {meta_path(ep['slug'], getattr(a, 'short', False))}")
    return ok


def cmd_check(a):
    sys.exit(0 if cmd_metadata(a, write=False) else 1)


def cmd_compile(a):
    from .compilation import compile_video
    compile_video(a.slug)


def cmd_upload(a):
    from .upload import upload
    upload(a.slug, short=a.short, yes=a.yes)


def cmd_comments_pull(a):
    from .comments import pull
    pull(a.max)


def cmd_comments_post(a):
    from .comments import post
    post(a.file, yes=a.yes)


def cmd_analyze(a):
    from .analyze import analyze_video, summary
    for v in a.videos:
        analyze_video(v, scene=a.scene)
    print("\n" + summary())


def cmd_voice_ref(a):
    from .analyze import voice_ref
    voice_ref(a.video, a.start, a.end, a.name)


def cmd_whoami(a):
    from .youtube import data_api, my_channel
    ch = my_channel(data_api())
    st = ch.get("statistics", {})
    print(f"Signed in to: {ch['snippet']['title']} ({ch['snippet'].get('customUrl', ch['id'])})")
    print(f"  subscribers {st.get('subscriberCount', '?')} · videos {st.get('videoCount', '?')} · views {st.get('viewCount', '?')}")


def cmd_board(a):
    from .board import write_board
    write_board()


def cmd_report(a):
    from .report import weekly_report
    weekly_report()


def cmd_status(a):
    from .generate import clips_for_shot
    from .assemble import find_voice_file, render_path
    from .metadata import meta_path, upload_record
    today = date.today()
    rows = []
    for p in sorted(EPISODES.glob("*.yaml")):
        try:
            ep = load_episode(str(p))
        except SystemExit as e:
            rows.append((p.stem, f"plan has problems: {str(e).splitlines()[0]}"))
            continue
        shots = used_shot_ids(ep)
        have_shots = sum(1 for s in shots if clips_for_shot(ep["slug"], s))
        lines = voice_lines(ep)
        have_voice = sum(1 for l in lines if find_voice_file(ep["slug"], l["id"]))
        made_by = ep.get("made_by")
        late = made_by and not render_path(ep["slug"]).exists() and date.fromisoformat(str(made_by)) < today
        parts = [
            f"clips {have_shots}/{len(shots)}",
            f"voice {have_voice}/{len(lines)}",
            "rendered" if render_path(ep["slug"]).exists() else "not rendered",
            "metadata" if meta_path(ep["slug"]).exists() else "no metadata",
            "uploaded (private)" if upload_record(ep["slug"]).exists() else "not uploaded",
        ]
        dates = f"make by {made_by}, publish from {ep.get('publish_after')}" if made_by else ""
        rows.append((ep["slug"], " | ".join(parts) + (f"  [{dates}]" if dates else "") + ("  LATE" if late else "")))
    if not rows:
        print("No episode plans yet. Start one: python -m pipeline new christmas-unwrapping xmas-unwrapping-01")
    for slug, info in rows:
        print(f"{slug:32} {info}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m pipeline", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new"); s.add_argument("theme"); s.add_argument("slug")
    s.add_argument("--minutes", type=float, default=30); s.set_defaults(fn=cmd_new)
    s = sub.add_parser("prompts"); s.add_argument("slug"); s.add_argument("--show", action="store_true"); s.set_defaults(fn=cmd_prompts)
    s = sub.add_parser("generate"); s.add_argument("slug"); s.add_argument("--provider")
    s.add_argument("--takes", type=int); s.add_argument("--only", nargs="*"); s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_generate)
    s = sub.add_parser("voice"); s.add_argument("slug"); s.add_argument("--provider"); s.add_argument("--redo", nargs="*")
    s.set_defaults(fn=cmd_voice)
    s = sub.add_parser("assemble"); s.add_argument("slug")
    s.add_argument("--allow-missing-voice", action="store_true")
    s.add_argument("--fast", action="store_true", help="hard cuts between chapters, no final re-encode")
    s.add_argument("--fresh", action="store_true", help="discard cached work files")
    s.set_defaults(fn=cmd_assemble)
    s = sub.add_parser("trailer"); s.add_argument("slug"); s.add_argument("--start", type=float, required=True)
    s.add_argument("--seconds", type=float, default=45); s.add_argument("--x", type=float, default=0.5,
                                                                         help="horizontal crop position 0 (left) to 1 (right)")
    s.set_defaults(fn=cmd_trailer)
    s = sub.add_parser("thumb"); s.add_argument("slug"); s.add_argument("--at", type=float, default=None,
                   help="seconds; default is the opening shot, so the thumbnail matches the first frame")
    s.set_defaults(fn=cmd_thumb)
    s = sub.add_parser("metadata"); s.add_argument("slug"); s.add_argument("--short", action="store_true"); s.set_defaults(fn=cmd_metadata)
    s = sub.add_parser("compile", help="join finished videos into a 2-3 hour sleep compilation"); s.add_argument("slug"); s.set_defaults(fn=cmd_compile)
    s = sub.add_parser("check"); s.add_argument("slug"); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("upload"); s.add_argument("slug"); s.add_argument("--short", action="store_true")
    s.add_argument("--yes", action="store_true"); s.set_defaults(fn=cmd_upload)
    s = sub.add_parser("comments-pull"); s.add_argument("--max", type=int, default=200); s.set_defaults(fn=cmd_comments_pull)
    s = sub.add_parser("comments-post"); s.add_argument("file"); s.add_argument("--yes", action="store_true")
    s.set_defaults(fn=cmd_comments_post)
    s = sub.add_parser("report"); s.set_defaults(fn=cmd_report)
    s = sub.add_parser("board"); s.set_defaults(fn=cmd_board)
    s = sub.add_parser("whoami", help="check the YouTube sign-in"); s.set_defaults(fn=cmd_whoami)
    s = sub.add_parser("analyze"); s.add_argument("videos", nargs="+")
    s.add_argument("--scene", type=float, default=0.3, help="cut sensitivity 0-1 (lower finds softer cuts)")
    s.set_defaults(fn=cmd_analyze)
    s = sub.add_parser("voice-ref"); s.add_argument("video"); s.add_argument("--start", required=True)
    s.add_argument("--end", required=True); s.add_argument("--name", default="annie-whisper"); s.set_defaults(fn=cmd_voice_ref)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
