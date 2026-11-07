"""Search fixes for the old videos (Ann's yes on the board, 4 Nov 2026).

- adds ONE first line with the trigger words (and the video's playlist link when it is in one); the rest of the
  description stays exactly as it was
- removes tags that read as flirty
Backups of every original description and tag list: metadata/channel/seo-backup-<date>.yaml. Runs only once per
video (skips descriptions that already start with the new line).

  python tools/seo_descriptions.py           dry run: prints what would change
  python tools/seo_descriptions.py --apply   changes the videos on YouTube
"""
import re
import sys
import time
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.youtube import data_api  # noqa: E402

FLIRTY = re.compile(r"sexy|kiss|baby|girlfriend|seduc|\bhot\b|sensual|naughty|\blick", re.I)
apply = "--apply" in sys.argv
yt = data_api()
retitled = {r["id"]: r for r in yaml.safe_load((ROOT / "brand/retitles.yaml").read_text()) if r.get("id")}
plist = {}
for p in yaml.safe_load((ROOT / "metadata/channel/playlists.yaml").read_text()):
    tok = None
    while True:
        try:
            r = yt.playlistItems().list(part="contentDetails", playlistId=p["id"], maxResults=50, pageToken=tok).execute()
        except Exception:
            break
        for it in r["items"]:
            plist.setdefault(it["contentDetails"]["videoId"], p)
        tok = r.get("nextPageToken")
        if not tok:
            break
ids = [v["id"] for v in yaml.safe_load((ROOT / "metadata/channel/videos-2026-11-04.yaml").read_text())
       if v["privacy"] == "public"]


def first_line(vid, title):
    if vid in retitled:
        line = retitled[vid]["description"].split("\n\n")[0]
    else:
        t = re.sub(r"\s*[-|_]+\s*annie\s*asmr.*$", "", title, flags=re.I).strip(" -|_")
        t = re.sub(r"\s*\|\s*", ", ", t)
        t = re.sub(r"[^\w\s&+',!?()]", "", t)
        t = re.sub(r"\s+", " ", t).strip(" ,")
        line = f"{t}: up-close ASMR sounds for tingles, relaxing and sleep."
    p = plist.get(vid)
    if p:
        line += f"\nMore like this: {p['title']} https://www.youtube.com/playlist?list={p['id']}"
    return line


backup, changed = [], 0
for i in range(0, len(ids), 50):
    for v in yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute()["items"]:
        sn = v["snippet"]
        old_d, old_t = sn.get("description", ""), sn.get("tags") or []
        head = first_line(v["id"], sn["title"])
        new_d = old_d if old_d.startswith(head.split("\n")[0]) else head + "\n\n" + old_d
        new_t = [t for t in old_t if not FLIRTY.search(t)]
        if new_d == old_d and new_t == old_t:
            continue
        backup.append({"id": v["id"], "title": sn["title"], "description": old_d, "tags": old_t})
        removed = [t for t in old_t if t not in new_t]
        print(f"\n{v['id']} {sn['title'][:60]}\n  + {head.splitlines()[0][:110]}" + (f"\n  - tags: {removed}" if removed else ""))
        if apply:
            body = {"id": v["id"], "snippet": {"title": sn["title"], "categoryId": sn["categoryId"],
                                              "description": new_d[:5000], "tags": new_t}}
            if sn.get("defaultLanguage"):
                body["snippet"]["defaultLanguage"] = sn["defaultLanguage"]
            yt.videos().update(part="snippet", body=body).execute()
            time.sleep(0.4)
        changed += 1
if apply:
    out = ROOT / f"metadata/channel/seo-backup-{date.today()}.yaml"
    out.write_text(yaml.safe_dump(backup, sort_keys=False, allow_unicode=True, width=160))
    print(f"\nchanged {changed} videos; originals saved in {out.name}")
else:
    print(f"\n{changed} videos would change (dry run)")
