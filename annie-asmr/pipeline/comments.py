"""Owner replies, human in the loop. Nothing here comments on its own.

  comments-pull  exports new viewer comments to metadata/comments/<date>.yaml with an empty reply
                 for each. Claude (in a chat) or you fill in reply drafts.
  comments-post  posts only replies you marked `approved: true`, asking once more for each.
"""
from __future__ import annotations

import re
from datetime import date

import yaml

from .config import METADATA
from .youtube import data_api, my_channel

DIR = METADATA / "comments"

FLAGS = {
    "request": r"\b(can you|could you|please do|do a|make a|request)\b",
    "roleplay/persona": r"\b(roleplay|role play|girlfriend|date me|marry|kiss|baby|babe)\b",
    "link/spam": r"(https?://|www\.|telegram|whatsapp|crypto|giveaway|dm me)",
    "question": r"\?",
}


def pull(max_threads: int = 200) -> str:
    yt = data_api()
    ch = my_channel(yt)
    channel_id = ch["id"]
    out, page, fetched = [], None, 0
    while fetched < max_threads:
        resp = yt.commentThreads().list(part="snippet,replies", allThreadsRelatedToChannelId=channel_id,
                                        maxResults=100, order="time", pageToken=page,
                                        textFormat="plainText").execute()
        for th in resp.get("items", []):
            fetched += 1
            top = th["snippet"]["topLevelComment"]["snippet"]
            if top.get("authorChannelId", {}).get("value") == channel_id:
                continue
            replies = th.get("replies", {}).get("comments", [])
            if any(r["snippet"].get("authorChannelId", {}).get("value") == channel_id for r in replies):
                continue  # already answered
            text = top.get("textOriginal") or top.get("textDisplay", "")
            flags = [name for name, rx in FLAGS.items() if re.search(rx, text, re.I)]
            out.append({
                "thread_id": th["id"], "video_id": th["snippet"].get("videoId"),
                "author": top.get("authorDisplayName"), "published": top.get("publishedAt"),
                "comment": text, "flags": flags,
                "reply": "", "approved": False, "posted": False,
            })
        page = resp.get("nextPageToken")
        if not page:
            break
    DIR.mkdir(parents=True, exist_ok=True)
    path = DIR / f"{date.today().isoformat()}.yaml"
    header = ("# Fill 'reply' for the ones worth answering, set approved: true, then run comments-post.\n"
              "# Rules: no requests taken, no roleplay or persona flirting. Leave spam blank and remove it in Studio.\n")
    path.write_text(header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=100))
    print(f"{len(out)} unanswered comment(s) written to {path}")
    return str(path)


def post(path: str, yes: bool = False) -> None:
    items = yaml.safe_load(open(path)) or []
    todo = [c for c in items if c.get("approved") and c.get("reply", "").strip() and not c.get("posted")]
    if not todo:
        print("Nothing approved to post.")
        return
    yt = data_api()
    for c in todo:
        print(f"\n{c['author']}: {c['comment'][:200]}\n  -> {c['reply']}")
        if not yes and input("Post this reply? [y/N] ").strip().lower() != "y":
            continue
        yt.comments().insert(part="snippet", body={"snippet": {"parentId": c["thread_id"],
                                                               "textOriginal": c["reply"].strip()}}).execute()
        c["posted"] = True
        print("  posted")
    with open(path, "w") as f:
        yaml.safe_dump(items, f, sort_keys=False, allow_unicode=True, width=100)
