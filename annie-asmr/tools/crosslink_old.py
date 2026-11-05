"""Put one line at the top of the most-watched old videos' descriptions pointing viewers to the new videos.
Ann said yes (5 Nov). Backs up every description first; running it again replaces the line instead of stacking.
python tools/crosslink_old.py [--apply] [--n 5] [--line "..."]
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from pipeline.youtube import data_api  # noqa: E402
MARK = "▸ New:"
ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--n", type=int, default=5)
ap.add_argument("--line", default="▸ New: slow, no-talking ASMR for sleep every Tuesday & Friday, 9 pm ET: "
                                  "https://www.youtube.com/playlist?list=PLFu20MWdwakI")
a = ap.parse_args()
yt = data_api()
up = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
ids, tok = [], None
while True:
    r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=tok).execute()
    ids += [i["contentDetails"]["videoId"] for i in r["items"]]; tok = r.get("nextPageToken")
    if not tok: break
vids = []
for i in range(0, len(ids), 50):
    vids += yt.videos().list(part="snippet,statistics,status", id=",".join(ids[i:i + 50])).execute()["items"]
vids = [v for v in vids if v["status"]["privacyStatus"] == "public"]
vids.sort(key=lambda v: -int(v["statistics"].get("viewCount", 0)))
backup = ROOT / f"metadata/channel/crosslink-backup-{datetime.now():%Y-%m-%d-%H%M}.json"
backup.write_text(json.dumps([{"id": v["id"], "description": v["snippet"]["description"]} for v in vids[:a.n]], indent=2, ensure_ascii=False))
for v in vids[:a.n]:
    sn = v["snippet"]; desc = sn.get("description", "")
    lines = desc.split("\n")
    if lines and lines[0].startswith(MARK):
        lines = lines[1:]
        while lines and not lines[0].strip(): lines = lines[1:]
    new = a.line + "\n\n" + "\n".join(lines)
    print(f"{v['statistics'].get('viewCount'):>7} views  {v['id']}  {sn['title'][:60]}")
    if a.apply and new != desc:
        body = {"id": v["id"], "snippet": {"title": sn["title"], "description": new[:5000], "categoryId": sn["categoryId"],
                                           "tags": sn.get("tags", []), **({"defaultLanguage": sn["defaultLanguage"]} if sn.get("defaultLanguage") else {})}}
        yt.videos().update(part="snippet", body=body).execute(); print("   updated")
print("backup:", backup.relative_to(ROOT), "" if a.apply else "(dry run; add --apply)")
