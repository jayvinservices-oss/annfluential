"""Re-apply the current description (incl. 'Ace's favourites' links) to videos already uploaded as drafts/public.
python tools/refresh_descriptions.py <slug> [<slug> ...] [--apply]   (dry run by default; title/tags unchanged)
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from pipeline.episode import load_episode  # noqa: E402
from pipeline.metadata import build, upload_record  # noqa: E402
from pipeline.youtube import data_api  # noqa: E402
apply = "--apply" in sys.argv
yt = data_api()
for slug in [a for a in sys.argv[1:] if not a.startswith("--")]:
    rec = upload_record(slug)
    if not rec.exists():
        print(slug, "not uploaded"); continue
    vid = json.loads(rec.read_text())["video_id"]
    meta = build(load_episode(slug))
    v = yt.videos().list(part="snippet", id=vid).execute()["items"][0]; sn = v["snippet"]
    if sn.get("description", "") == meta["description"]:
        print(slug, "already up to date"); continue
    print(slug, vid, "-> description will change" + ("" if apply else " (dry run)"))
    if apply:
        yt.videos().update(part="snippet", body={"id": vid, "snippet": {"title": sn["title"], "categoryId": sn["categoryId"],
            "description": meta["description"], "tags": sn.get("tags", []),
            **({"defaultLanguage": sn["defaultLanguage"]} if sn.get("defaultLanguage") else {})}}).execute()
        print("   updated")
