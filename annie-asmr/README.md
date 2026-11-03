# Annie ASMR pipeline

Turns an episode plan into a finished 20 to 60 minute video, a Short trailer, honest metadata and a
private YouTube draft, then reports weekly on watch hours. You approve every step; nothing publishes itself.

```
episode plan ──> prompts ──> clips ──┐
     │                              ├──> assemble (loop, crossfade, level, chapters) ──> metadata + checks ──> private draft ──> YOU publish
     └──────────> whisper script ──> voice ──┘                                                    └──> Short trailer
weekly: report (hours, views, retention)   ·   comments-pull ──> reply drafts ──> you approve ──> comments-post
```

## One-time setup on the Mac

```bash
cd annfluential/annie-asmr
brew install ffmpeg python@3.12
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then open .env in TextEdit and paste your keys there, not in chat
python tests/smoke_test.py    # should end with SMOKE TEST PASSED
```

Export the Canva reference (MAHZ22R5eUg, concept 2) as PNG to `prompts/reference/avatar.png`.

### Choose the video generator (config.yaml -> generator.provider)
| provider | what it is | key in .env |
|---|---|---|
| `manual` (default) | You paste prompts from `clips/<slug>/_prompts.md` into any web app and save files with the names it lists | none |
| `runway` | Runway image-to-video API, starts each clip from your reference image | `RUNWAY_API_KEY` |
| `replicate` | Any video model on Replicate (Kling, Wan, Hailuo, Veo...). Set `generator.replicate.model` and the field names from the model page | `REPLICATE_API_TOKEN` |

Check the provider's current docs before the first paid run; model names and fields change.

### Choose the voice (config.yaml -> voice.provider)
- `manual` (default): `audio/voice/<slug>/_script.md` lists each line and its file name; record or export them.
- `elevenlabs`: hosted cloned voice. Put `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in `.env`.
  The `eleven_v3` model takes a `[whispers]` tag; cloning from whispered samples gives the best whisper.
- `local`: a command on the Mac. VoiceStudio: if it only has an app (no command line), use `manual`
  and export each line from the app with the listed file name.

### YouTube API setup (once, about 20 minutes)
1. console.cloud.google.com -> new project "Annie ASMR pipeline".
2. Enable **YouTube Data API v3** and **YouTube Analytics API**.
3. OAuth consent screen: External, add your Google account as a test user.
4. Credentials -> OAuth client ID -> **Desktop app** -> download JSON to `.secrets/client_secret.json`.
5. First `upload` / `report` opens a browser: sign in as the account that owns Annie ASMR.

**Important:** YouTube locks videos uploaded through an *unaudited* API project to private, and they
stay private even if you change them in Studio. Before relying on API uploads for videos you will publish,
submit the **YouTube API Services audit** form for the project (free, takes a few weeks). Until it is
approved, upload final videos in Studio by hand using the title, description and tags from
`metadata/<slug>.json`, and use the API only for the report and comments. Ticking "Altered or synthetic
content: Yes" in Studio is then your step.

## Making a video

```bash
python -m pipeline new rhinestone-with-me xmas-rhinestone-02   # new plan, fresh variation picked for you
#   edit episodes/xmas-rhinestone-02.yaml: title, description, chapters, shots, sound beds, whispers
python -m pipeline check xmas-rhinestone-02      # honesty + variety checks, no ERROR lines allowed
python -m pipeline prompts xmas-rhinestone-02    # review prompts in prompts/out/
python -m pipeline generate xmas-rhinestone-02   # clips -> clips/<slug>/ (move bad takes to _rejected/)
python -m pipeline voice xmas-rhinestone-02      # whispers -> audio/voice/<slug>/
python -m pipeline assemble xmas-rhinestone-02   # -> renders/<slug>.mp4 with chapters
python -m pipeline thumb xmas-rhinestone-02 --at 600
python -m pipeline metadata xmas-rhinestone-02   # -> metadata/<slug>.json, prints checks
python -m pipeline upload xmas-rhinestone-02     # private draft, asks you first
python -m pipeline trailer xmas-rhinestone-02 --start 900 --seconds 45
python -m pipeline metadata xmas-rhinestone-02 --short && python -m pipeline upload xmas-rhinestone-02 --short
python -m pipeline status                        # every episode at a glance
```

Sound beds go in `audio/sfx/` (they loop); keep a note of each sound's source and licence.

### How assembly keeps it smooth
Each chapter is built from "loop units": that chapter's clips crossfaded in a shuffled order that starts
and ends on the same frame, so units join with no visible jump. Three different clip orders are cycled so
the loop does not repeat identically. Chapters crossfade into one another, audio is mixed to match,
levelled in two passes to -18 LUFS (config.yaml), and chapters are written both into the file and the
description. `--fast` skips the chapter crossfades (hard cuts, much quicker on an Intel Mac).

Rough timing on an Intel MacBook Pro: a 30 minute 1080p render is roughly 30 to 60 minutes of encoding.

### What the checks catch
- Title over 100 characters, banned words (roleplay, girlfriend, requests, "not AI"...), "no talking"
  when there are whispers, whispers claimed with none, "1 hour" when the video is 30 minutes.
- Title words that appear nowhere in the plan (flagged for you to confirm).
- A plan that is too close to an earlier one, same variation, or the same title (variety rule).
- Chapters YouTube will not show (fewer than 3, or shorter than 10 seconds).

### Talking segments (gum chewing with chat)
Generated clips do not move their lips in time with your voice. For chat videos, either keep talking
over closed-lip chewing shots, or run a lip-sync model (PersonaLive or similar) on a rented cloud GPU
over the assembled talking segments. That step is not built yet; add it before the first chat video.

## Weekly

```bash
python -m pipeline report          # reports/<date>.md: Earn-tab hours (estimate), views, retention, pace
python -m pipeline comments-pull   # metadata/comments/<date>.yaml; ask Claude to draft replies in it
#   read the drafts, edit, set approved: true on the ones to send
python -m pipeline comments-post metadata/comments/<date>.yaml   # asks before each reply
```

The report estimates the Earn-tab number from watch time on public, non-Short videos over 365 days.
Studio's Earn tab is the official figure; compare them each week.

## The numbers to keep in view
From 543 hours on 3 Nov 2026, reaching 4,000 by 17 Jan 2027 needs about **46 public watch hours a day**
for 75 days. The report tracks the real daily pace against that. Hours from Shorts do not count; hours
from scheduled live streams count once the archive is public.

## Christmas run (make by 24 Nov, publish from 1 Dec)
| plan | theme | suggested publish |
|---|---|---|
| `xmas-unwrapping-gifts` | unwrapping gifts | 1 Dec |
| `xmas-tree-decorating` | tree decorating | 4 Dec |
| `xmas-rhinestone-ornament` | rhinestone with me | 8 Dec |
| `xmas-festive-cards` | festive designing | 11 Dec |

The dates in each plan are suggestions; you set the real ones when you publish in Studio.
