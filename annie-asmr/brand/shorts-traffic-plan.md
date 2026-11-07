# Shorts and traffic plan (4 Nov 2026)

Channel data, last 12 months: 9,161 views, all long-form (no Shorts posted). Top sources: YouTube search 2,788,
suggested videos 1,767, channel pages 1,555, subscribers 1,369, playlists 751.
Shorts views do not count toward the 4,000 watch hours; their job is to bring new viewers to the long videos.

## Shorts
- 3 per long video, 35 seconds each, cut automatically from the loudest steady moment of the first 3 chapters
  (`python -m pipeline shorts <slug>`). No new generation cost.
- Title: "<chapter> ASMR (No Talking) #shorts". Description opens with the link to the full video.
- Posting: Claude uploads them as private drafts; Ann says yes on the board; Claude publishes or schedules them
  (`publish-short`), only after the full video is public. Spacing: day 1, day 3, day 5 after the long video, 9 pm Toronto.
- Linking: the description link is automatic. The Shorts "Related video" field cannot be set through the API,
  so Ann taps it once per Short in the YouTube app (Edit > Related video > the full video).
- Review after December: if Shorts bring fewer than 5% of long-form views, stop.

## Other traffic (by expected effect)
1. Search titles and descriptions: "No Talking", "for Sleep", trigger names first (done in the plans).
2. Same slot every week: Friday 9 pm Toronto Premiere (live-stream-plan.md). Subscribers are the 4th traffic source.
3. Playlists as sleep sessions: each new video goes into its trigger playlist on upload, so autoplay keeps viewers
   on the channel (playlists already bring 751 views; Claude adds new videos).
4. Old videos send viewers to new ones: Claude adds one line at the top of the 5 most-watched old videos'
   descriptions linking the newest related AI video (Ann's yes first).
5. End screens: Ann sets one end screen in Studio ("Best for viewer" + subscribe), then "Import from video"
   on each new one. The API cannot set end screens.
6. Thumbnail Test & Compare: Claude makes 3 thumbnails per video; Ann loads them in Studio (Studio only).
7. Monthly 3-hour sleep compilation (compilations/), the biggest watch-hour lever.
8. Pinned comment pointing to the playlist: Ann posts and pins it herself (Claude never posts comments).
