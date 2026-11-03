# Annie ASMR: working notes for Claude

## The channel
- Annie ASMR (@annieasmr9051). 1,034 subscribers, 543 of 4,000 public watch hours (3 Nov 2026).
- Goal: YouTube Partner Program by 17 January 2027. Hard cutoff 31 January 2027, 18:59 Toronto.
- Ann approves everything before it is published. Nothing goes public without her yes.

## The look (locked in prompts/avatar.yaml)
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
