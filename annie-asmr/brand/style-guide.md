# Annie ASMR style guide (v1, 3 Nov 2026)

Draft for Ann's approval. Artwork drafts are in `brand/assets/` (rebuild with `python tools/brand_assets.py`).

## What the channel is
**Glossy, slow, up-close ASMR for sleep: gum, lip gloss, nails and crafts.**
One sentence for the About page, the banner and every description's first line.

- Keep what already works: lower face only, glossy lips, gold chain, gum. The gum popping and crackling
  video brings about three quarters of the channel's watch hours.
- Change the setting. Old videos are bright and busy (ceiling lights, a patterned top, branded gum packs).
  New videos are dark, warm and close: deep brown backdrop, one soft light, nothing behind her.
- The presenter is an AI lower-face avatar speaking in Ann's cloned voice. Say so in every description
  (the disclosure line in `config.yaml`) and tick "Altered or synthetic content" in Studio.
- Beauty and crafts only. No roleplay, no pet names, no flirting, no requests for viewers' details.

## Look
| | |
|---|---|
| Framing | Tip of the nose to the upper neck. Eyes never in frame. Hands come up into the shot. |
| Skin and lips | Deep brown skin with a dewy sheen; very full lips, mauve-brown liner into pink-nude gloss, high shine. |
| Hands | Very long almond nails. Latte-nude by default; one seasonal colour per video (gold tips, red chrome). |
| Jewellery | One thin gold chain. Nothing else. |
| Light | One warm soft light from the front, background falling off to near black. No ceiling lights. |
| Props | One hero object per shot. No visible brand logos (gum and gloss without labels). |

## Colours
| Name | Hex | Use |
|---|---|---|
| Cocoa | `#2B1813` | Backgrounds, banner, thumbnail shade |
| Cream | `#F7EEEA` | Words on dark |
| Gloss pink | `#F3C6CF` | Small labels, the trigger list |
| Mauve | `#A8475F` | Series pill on thumbnails, buttons |
| Gold | `#C9A24B` | Profile ring, thin rules. Never for words |
| Latte | `#D9B79A` | Nails, warm accents in sets |

## Type
- **Gloock** (serif) for the name and thumbnail words. **Figtree** for small labels. Both free (Open Font License).
- Thumbnail words: 1 to 3 words, Gloock, cream, left side, bottom half. Never more than 3 words.

## Thumbnails
1. A real frame from the video's first 10 seconds, the strongest trigger, lips or hands filling the frame.
2. Left side shaded to cocoa so the words read on a phone.
3. Words name the trigger, not a feeling: "Gum Pops", "300 Layers", "Nail Taps". They must be in the video.
4. Series pill bottom left in mauve: GUM CLUB, GLOSS LAB, NAIL STUDIO, CRAFT CORNER, or the season.
5. No faces above the nose, no arrows, no red circles, no emoji, no clickbait.

## Titles
`ASMR <main trigger> & <second trigger> | <one detail> | <talking level>`
- e.g. `ASMR Fast Gum Popping & Knuckle Cracking | Up Close | Whispers`
- Main trigger in the first 40 characters (it is all a phone shows).
- Talking level is always one of: No Talking, Whispers, Soft Spoken.
- The channel name is not in the title (it already shows under every video). No ALL CAPS, no emoji.
- Everything in the title happens in the video (`python -m pipeline check` enforces it).

## Descriptions
1. Line 1: what you hear, in plain words (shows in search).
2. Chapters, one per trigger.
3. The disclosure line from `config.yaml`.
4. Two playlist links: the series and "Long ASMR for sleep".
5. No hashtags beyond three (#asmr plus two triggers).

## Opening of every video
- Trigger first. No hello, no intro, no talking for the first 30 seconds.
- The whispered brand line "Annie ASMR... Annie ASMR... Annie ASMR." over the first trigger.
- The thumbnail frame is the opening shot, so what viewers click is what they get.

## Voice
- Ann's cloned voice, whispered or soft spoken, short lines, long gaps. Thank viewers for requests;
  never promise a request. Goodnight at the end.

## Series (playlists)
| Series | What | Example |
|---|---|---|
| Gum Club | Gum chewing, popping, crackling | Fast Gum Popping & Knuckle Cracking |
| Gloss Lab | Lip gloss layering, tubes, wands | 300 Layers of Lip Gloss |
| Nail Studio | Nail tapping, scratching, long nails on objects | Nail Taps on Glass |
| Craft Corner | Rhinestones, cards, wrapping | Rhinestone With Me |
| Christmas 2026 | Seasonal videos, from 1 Dec | Unwrapping Gifts |
| Long ASMR for Sleep | Every video 30 minutes or longer | all long videos |

## Channel artwork (drafts)
- Banner `assets/banner-2560x1440.jpg`: name, the four triggers, "Long, slow, up-close ASMR for sleep",
  all inside the 1546 x 423 safe area so it reads on phones and TVs.
- Profile picture `assets/profile-800.png`: glossy lips and gloss tube inside a gold ring.
- Thumbnail templates `assets/thumbnail-template-*.jpg`.
