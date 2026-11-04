# Annie ASMR: working notes for Claude

## The channel
- Annie ASMR (@annieasmr9051). 1,030 subscribers, 539 of 4,000 public watch hours (4 Nov 2026, API).
- Goal: YouTube Partner Program by 17 January 2027. Hard cutoff 31 January 2027, 18:59 Toronto.
- Ann approves everything before it is published. Nothing goes public without her yes.

## The look (locked in prompts/avatar.yaml)
- Both avatars are ANONYMOUS generated characters (Ann, 3 Nov): not Ann's or her friend's likeness, no real photos.
  Identity reference: the generated duo portrait, Canva media MAHZ4Lq0kqs (Annie right, Bestie left).
- Claude may write its own Canva image prompts for avatar stills (Ann's yes, 3 Nov).
- AI avatar, lower face only: Black woman, deep brown skin, full glossy lips, nude-pink gloss, long almond nails.
- Reference image: Canva media MAHZ22R5eUg (concept 2), exported to prompts/reference/avatar.png.
- Talking and whispering in Ann's cloned voice. Real or curated sounds for gum, gloss, crafts.
- Beauty and crafts only. No roleplay, no requests, no persona flirting.

## Content
- Regular: lip gloss layering ("300 layers"), gum chewing with chat, nails. Glass fruit later. No snow.
- Christmas: made by 24 Nov, publish from 1 Dec. Unwrapping gifts, tree decorating, rhinestone with me,
  festive designing. Hands and long nails do the work.
- Long form first (20 to 60 min). Shorts only as trailers pointing to the long video.

## Rules Claude must keep
- Titles match what is in the video. `python -m pipeline check <slug>` must show no ERROR lines.
- Never post comments. Draft owner replies in metadata/comments/*.yaml for Ann to approve; she runs comments-post.
- Vary every video (theme, objects, sound). Do not copy an episode plan and change only the title.
- Uploads are private drafts only. Never add code that sets privacy to public or unlisted, or schedules publishing.
- Live streams: only scheduled ones, archived as public videos afterwards. No 24/7 loops.
- API keys live in .env on Ann's Mac. Never ask for them in chat and never write them to a file in git.
- Hardware: Intel MacBook Pro, no NVIDIA GPU. Anything needing CUDA (PersonaLive lip-sync) runs on a rented cloud GPU.

## How the folder works
- prompts/avatar.yaml + prompts/themes/*.yaml  -> the prompt library
- episodes/<slug>.yaml                          -> one plan per video (chapters, shots, sounds, whispers)
- clips/<slug>/  audio/sfx/  audio/voice/<slug>/ -> inputs;  renders/  metadata/  reports/ -> outputs
- Commands: see README.md. Smoke test: `python tests/smoke_test.py` (needs only ffmpeg).

## When asked to draft comment replies
Read the newest metadata/comments/*.yaml. Write a short, warm, honest `reply` for real comments only.
Decline requests politely without promising content; skip anything flagged roleplay/persona or link/spam.
Leave `approved: false`. Ann approves.

## Production board (Ann checks this on her phone)
- Private page: https://claude.ai/artifact/4z2SrmNjKK1g7khP7XFKut
- Rebuild with `python -m pipeline board`, then republish renders/board.html to that same URL (Artifact tool with `url`).
- Numbers come from metadata/channel-stats.yaml (update when Ann pastes Studio summaries); to-dos from metadata/todo.yaml.
- Clips mode is manual (free): Ann makes clips from the board's prompts and uploads them to Google Drive
  "Annie ASMR/clips/<slug>/"; source videos and the reference image go to "Annie ASMR/source", real
  sounds to "Annie ASMR/sfx". These folders are in the jayvin.services@gmail.com Drive (the connected
  one); folder IDs are in metadata/todo.yaml under `drive`.
- Voice: VoxCPM2 (Apache 2.0, commercial use allowed). Do NOT use VoiceStudio's default OmniVoice model:
  its weights are CC-BY-NC (non-commercial) and the channel is being monetised.

## Starting a new cloud session (the container is wiped between sessions)
1. `bash tools/cloud_setup.sh` (reinstalls VoxCPM2 and downloads its model; run in the background).
2. Re-fetch the reference photo from Drive ("Annie ASMR/source/Annie ASMr Videos - Top 10/Annie asmr lips.jpg",
   under 10 MB so the Drive connector works) and crop the middle panel:
   `ffmpeg -i annie-lips-triptych.jpg -vf "crop=552:944:559:0" prompts/reference/avatar.png`
   (left panel crop=552:944:0:0 -> pose-applying-gloss.png, right crop=556:944:1124:0 -> pose-nails-chin.png).
3. Videos over 10 MB cannot come through the Drive connector: download them with curl from
   drive.usercontent.google.com once Ann has allowed that host and shared the folder by link.

## Rebrand (started 3 Nov 2026)
- brand/style-guide.md, rebrand-plan.md, channel-copy.md, monetisation-plan.md, retitles.yaml (draft PG-13 titles),
  rebrand-actions.yaml (the approval list on the board). Copies as Google Docs in Drive "Annie ASMR/brand".
- Artwork: `python tools/brand_assets.py` (needs Gloock.ttf/Figtree.ttf in $BRAND_FONTS, from Google Fonts) and
  `python tools/retitle_thumbs.py` (needs the downloaded videos in /home/user/annie-src).
- Ann's answers: ArtifactData list, collection "approvals" on the board URL; doc id = action id,
  {decision: yes|later, note, at}. Act on "yes" only; nothing is changed on YouTube without it.
- The board publishes with capabilities {db: {}, downloads: true}; keep both on republish (omit `capabilities`).
- Cloud YouTube access: env vars YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN (set by Ann in
  the environment settings); check with `python -m pipeline whoami`.

## Channel changes made through the API (4 Nov 2026)
- Backup of settings before any change: metadata/channel/before-2026-11-04.json. Video list: metadata/channel/videos-2026-11-04.yaml.
- Done: banner v2, About + keywords, trailer -RTD9GAQDvE, watermark, 6 playlists (metadata/channel/playlists.yaml), 2 home sections.
- Freesound blocks this cloud server's IP (empty 403 even on its home page); Ann downloads CC0 sounds herself.
- httplib2 crashes on YouTube's empty 204 replies (watermarks.set); use requests with Accept-Encoding: identity.
- New playlists answer 404 to playlistItems.list for a while; insert items directly.
