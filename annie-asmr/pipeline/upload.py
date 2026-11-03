"""Step 7: upload as a PRIVATE draft. This code cannot publish; you review and publish in YouTube Studio."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from .metadata import meta_path, print_checks, upload_record
from .youtube import data_api


def upload(slug: str, *, short: bool = False, yes: bool = False) -> str | None:
    mp = meta_path(slug, short)
    if not mp.exists():
        raise SystemExit(f"No metadata yet. Run: python -m pipeline metadata {slug}")
    meta = json.loads(mp.read_text())
    rec = upload_record(slug, short)
    if rec.exists():
        old = json.loads(rec.read_text())
        raise SystemExit(f"Already uploaded as {old['video_id']} ({old['studio_url']}). Delete {rec} to upload again.")
    video = Path(meta["file"] or "")
    if not video.exists():
        raise SystemExit(f"Video file not found: {video}")
    if not print_checks(meta):
        raise SystemExit("Fix the errors above (edit the episode plan, then re-run metadata) before uploading.")

    # Hard rule: drafts are private. Nothing in this pipeline can make a video public.
    if meta.get("privacy_status") != "private":
        raise SystemExit("Refusing: metadata privacy_status must be 'private'.")

    print(f"\nTitle:  {meta['title']}\nFile:   {video} ({video.stat().st_size / 1e9:.2f} GB)\nPrivacy: private draft")
    if not yes and input("Upload this as a private draft? [y/N] ").strip().lower() != "y":
        print("Not uploaded.")
        return None

    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": meta["category_id"],
            "defaultLanguage": meta["default_language"],
            "defaultAudioLanguage": meta["default_language"],
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,   # "Altered or synthetic content: Yes"
            "embeddable": True,
        },
    }
    yt = data_api()
    media = MediaFileUpload(str(video), chunksize=16 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response, retries = None, 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  uploaded {status.progress():.0%}", flush=True)
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and retries < 8:
                retries += 1
                time.sleep(2 ** retries)
                continue
            raise
        except (ConnectionError, TimeoutError, OSError):
            if retries >= 8:
                raise
            retries += 1
            time.sleep(2 ** retries)

    vid = response["id"]
    thumb = video.with_name(video.stem + "-thumb.jpg")
    if not short and thumb.exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
            print("  thumbnail set")
        except HttpError as e:
            print(f"  thumbnail not set ({e.resp.status}); add it in Studio. Custom thumbnails need a verified account.")

    record = {"video_id": vid, "studio_url": f"https://studio.youtube.com/video/{vid}/edit",
              "uploaded": datetime.now().isoformat(timespec="seconds"), "privacy": "private"}
    rec.write_text(json.dumps(record, indent=2))
    print(f"\nPrivate draft ready for your review: {record['studio_url']}")
    print("In Studio: watch it, check 'Altered content: Yes' is set, then publish or schedule yourself.")
    return vid
