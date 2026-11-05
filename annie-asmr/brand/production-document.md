# Annie ASMR: production document (handover, last updated 5 Nov 2026, night)

For whoever picks this up next (Cowork or a new Claude session). Repository: jayvinservices-oss/annfluential,
branch `claude/ecstatic-bohr-j9y4k4`, folder `annie-asmr/`. Read `annie-asmr/CLAUDE.md` first: it holds the rules.

## The goal
YouTube Partner Program: 4,000 public watch hours by 17 Jan 2027 (hard cutoff 31 Jan). About 540 now (4 Nov).
Strategy: long, slow, no-talking sleep ASMR (60 min to 3 h), two uploads a week, Shorts as trailers, a monthly
3-hour compilation, Ace (Ann's real cat) purring videos, a face reveal mid-December.

## Rules that must not be broken
- Ann approves everything. Uploads are PRIVATE drafts; Ann publishes long videos herself. Shorts may be published
  by Claude only with Ann's recorded yes (metadata/publish-approvals.yaml) and only once the full video is public.
- Never post comments. Never delete Drive files (rename "DUPLICATE -" / move to _Holding).
- Never ask for API keys in chat. Presenter is an anonymous AI character: lower face only (nose down) until the
  face reveal. Ace is real: keep his real look (start clips from his photos).
- Spend caps in code: $5/day, $20 total (config.yaml generator.router). 5 Nov only: $7 (set back to 5 on 6 Nov;
  the helper session has a reminder for this).
- Titles must match what is in the video (`python -m pipeline check <slug>` shows no ERROR).

## Ann's decisions (5 Nov)
- NO GUM: video 1 (slow gum, private draft 30yBUNIU-zE) is on hold, not to be published; gum-xslow cancelled.
  Main series = Ace in different settings (tools/ace_stills.py <location>; episode ace_location).
  Mouth sounds (videos 2, 4) only if lip sync looks right (tools/sync_chews.py); otherwise replace with Ace.
- Replies on our channel: posted after Ann's approval (7 posted 5 Nov). Other channels: Claude drafts
  twice a week (Wed + Sat), Ann posts herself.
- Pace: SLOW for no-talking videos. Two versions tested as separate videos: slow (about 40% fewer sounds/min)
  and extra slow (about 60% fewer; titles "Extra Sleepy ... for Insomnia ... When Tingles Don't Work").
  Talking stays normal pace. Tool: tools/slow_space.py. Clips play in smooth slow motion (episode `clip_speed`).
- Backgrounds: rotate three looks, all cropped nose-down: bedroom, night + ASMR mic, pink glow + mic
  (episode `look`; stills in prompts/reference/stills/).
- Voice: Ann's REAL whisper recordings, cleaned with "crisp B" (config audio.real_voice_filter), in
  audio/voice/real/. She also likes the two clones (VoxCPM2 local, chatterbox on Replicate) to rotate for new
  lines. Most scheduled videos are no talking.
- Sounds: Ann will NOT record more. Available: gum (slow/xslow), mouth sounds (slow/xslow), knuckles, gloss +
  chewing, Ace purring, nail taps (short). Missing: nail tapping set, wax cracking, lip gloss layers, Christmas.
  Option given to her: free pixabay.com sound effects downloaded on her phone into Drive > 02 Sounds.
- Thumbnails: style guide (cocoa fade, Gloock words, mauve pill); tools/thumbnail.py; 3 per video for Studio
  Test & Compare.
- Takes: 3 per shot by default (variety; YouTube repetitive-content rules).

## Schedule (Tue + Fri, 9 pm Toronto)
| Date | Video (slug) | Status 5 Nov night |
|---|---|---|
| Fri 7 Nov | Petting My Cat Until He Purrs (ace-petting-purr-01) | 15 clips (presenter hand), assembling |
| Tue 11 Nov | Extra Sleepy Mouth Sounds for Insomnia (mouth-sounds-xslow-01) | 7 clips kept, to assemble |
| Fri 14 Nov | Real Cat Purring by the Fire (ace-fireplace-01) | plan ready; Ace fireplace stills + clips by 12 Nov |
| Tue 18 Nov | Slow Mouth Sounds (mouth-sounds-slow-01) | plan ready, clips to make by 15 Nov |
| Fri 21 Nov | 3 Hours Sleeping With My Cat (ace-sleeping-3h-01) | needs Ace sleeping photos |
| Tue 2 Dec | Christmas Cat Purring Under the Tree (ace-christmas-tree-01) | plan ready |
| Fri 5 Dec | 3-hour sleep compilation (compilations/sleep-compilation-2026-12.yaml) | after the sources are public |
| Mid-Dec | Face reveal (brand/face-reveal-plan.md) | plan only |
Christmas videos (xmas-*) and nail tapping / wax cracking / gloss layers are parked until sounds exist.

## How a video is made
1. Clips: a helper cloud session holds REPLICATE_API_TOKEN (session_017bBopu2AbLhvLz439HXKLb, "Annie ASMR:
   Replicate API test"). Send it: `python -m pipeline generate <slug>` (router: Wan 2.2 fast, about $0.10/clip).
   Ann has given it standing approval up to the daily cap. It pushes clips to the branch.
2. Check every clip (frame sheet): reject full faces/eyes, tongue, extra hands, wrong hand (presenter hand =
   caramel skin, long coffin nails, gold ring). Move rejects to clips/<slug>/_rejected/.
3. `python -m pipeline assemble <slug> --fast` (run in background with a long timeout; one render at a time).
4. `python -m pipeline metadata <slug>`, thumbnail (tools/thumbnail.py), `python -m pipeline upload <slug>`
   (private draft), `python -m pipeline shorts <slug>` + upload each short.
5. Republish the production board: `python -m pipeline board`, then the Artifact at
   https://claude.ai/artifact/4z2SrmNjKK1g7khP7XFKut.

## Waiting on Ann
- Review video 1's private draft; publish Fri 7 Nov 9 pm (or ask to schedule).
- Per Short: set "Related video" in the YouTube app. Once: end screen in Studio.
- Ace photos: curled up asleep, on the bed with face visible (by 20 Nov).
- Free sounds for the parked videos (list in the last chat; pixabay.com).
- Drive trash holds "Ace - conversation in bed, NOT FOR VIDEO" (not trashed by Claude); a copy is in _Holding.

- Ace series plan (draft, 10 videos): brand/ace-series-plan.md

## Business (beyond YouTube), started 5 Nov
Goal (Ann): about $10k/month from the Ace brand within 12-24 months, run by AI; Ann gives the word.
- Etsy product 1 READY: "Real Cat Purring for Sleep, 1 Hour" (annie-asmr/shop/ace-purring/: 3 MP3s, 3 images,
  listing.md). Needs listing in Ann's Etsy shop (Ann or Cowork with her browser).
- Amazon affiliate: waiting on Ann's Associates store ID (.ca or .com) + the names of Ace's products.
  Then an "Ace's favourites" block (with the Amazon disclosure) goes in every Ace description.
- Ace purr book (KDP): idea; photo picture book with a short story + scannable purr audio. Declare AI use.
- Full income research (2026 sources, ranked, 24-month plan): /reports/Cat brand income streams 2026.md (repo root). Base case: a few hundred/month by month 12, about CA$1-2.5k by month 24; $10k needs a breakout. Top 5: YouTube sleep-with-Ace (real footage), Etsy digital bundles, POD Ace merch, high-ticket affiliates (Litter-Robot CA 8%), paid UGC for pet brands.
- Security: Etsy 2FA backup codes are stored as plain text in Drive (two copies); Ann to move them to a
  password manager. Claude does not use them.

## Where things are
- Drive "Annie ASMR" (jayvin.services account): numbered 01 Voice ... 07 Brand & Plans, _Holding. Index doc
  "00 Index - Annie ASMR Drive"; repo copy brand/drive-index.md.
- YouTube: @annieasmrai. Playlists in metadata/channel/playlists.yaml (Ace playlist private until his video).
  The top 5 old videos now open with a link line to the sleep playlist (backup in metadata/channel/).
- Research: reports/competitors-2026-11-04.md, reports/cat-purring-2026-11-05.md; plans in brand/.
- Spend ledger: metadata/spend.yaml (about $6.70 of $20 by end of 5 Nov).
- Weekly report: scheduled task every Monday 7:23 Toronto.

## Known issues
- Disk is limited: delete renders/<slug>/work and the final mp4 after upload.
- Wan clips are energetic; use clip_speed slow motion and reject bad takes.
- Replicate sometimes fails a prediction ("Model not found ..."): generate skips it; retry once with --only.
- The image-editing model zooms out to the full face: always crop nose-down before use.
- Container memory: never run two heavy jobs (render + voice model + background removal) at once.
