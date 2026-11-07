# Annie ASMR: realistic AI inserts, research findings

Research date: Saturday 7 November 2026. Web research only. Nothing was signed up for, bought or changed.

How prices were checked: Replicate model pages, fal.ai model pages, Google's Gemini API pricing and docs pages, YouTube Help pages and Higgsfield's own blog and help pages were downloaded directly on 7 Nov 2026, and the figures below come from the structured pricing data on those pages. Anything taken from a third-party blog, or not checked, is marked **(unverified)**.

---

## 1. The platform in the TikTok screenshot: Higgsfield AI (higgsfield.ai)

**Identification (confirmed).** The navigation on every higgsfield.ai page fetched today reads: "Explore, Image, Video, Audio, MCP, API, Genjutsu (New), Shorts Studio (New), Content Factory, Playable, Mangaka (New), AI Influencer, Academy (New), Katana, ...". "AI In..." in the screenshot is **AI Influencer**. The screenshot shows Higgsfield's image generator running Google's Nano Banana Pro with the Unlimited toggle.
Source: https://higgsfield.ai/pricing (navigation captured 7 Nov 2026)

### Pricing tiers (2026)

Higgsfield's official explainer, dated **24 Oct 2026**, says "Prices verified October 2026 on the Higgsfield pricing page":

| Plan | Price | Credits per month | Commercial use |
|---|---|---|---|
| Free | $0 | small allowance (BudgetPixel says 10 credits, **unverified**) | No (watermarked) |
| Starter | $15/mo | 200 | Yes |
| Plus | $49/mo | 1,000 | Yes |
| Ultra | $129/mo | 3,000 | Yes |
| Team | $79 per seat/mo (2 to 9 seats) | 1,000 per seat | Yes |
| Scale | $215 per seat/mo (5 to 15 seats) | 2,500 per seat | Yes |

Source: https://higgsfield.ai/blog/higgsfield-pricing-explained (24 Oct 2026)

Discrepancies to check on the live pricing page before paying, which is rendered in JavaScript and could not be read:
- Several September 2026 third-party guides list Starter at $19 (270 credits), Plus at $59 monthly or $47 a month billed annually, and Ultra at $129 monthly or $99 billed annually **(unverified)**. Examples: https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs and https://endless.app/blog/higgsfield-pricing
- Higgsfield's own 7-day bonus post (30 Oct 2026) uses the plan names "Pro, Plus, Max, Ultra", which differ from the 24 Oct names. The plan names seem to be changing, or differ by region or cohort.

Other plan facts from the 24 Oct explainer:
- Credits are spent per generation. Completed generations are charged even if you discard them, and failed ones are usually refunded.
- Unused credits do not roll over. Purchased credit packs expire after 90 days.
- Starter allows 2 video jobs at a time, Plus 6, Ultra 8. Start and End Frame control is only on Plus and Ultra.
- Example credit costs: Nano Banana Pro image 2 credits (4K: 4), Seedance 2.0 5s 720p 30, Seedance 2.5 5s 720p 35, 1080p 80, Veo 3 Fast 8s 720p with audio about 22, Veo 3 8s about 58.
- At the Plus rate (about $0.049 per credit), a Nano Banana Pro image costs about $0.10 and a 5s 720p Seedance 2.5 clip about $1.72.
- The API has its own dollar balance, so subscription credits do not work through the API.

### What "Unlimited" actually covers

- **What it is:** Unlimited means some models do not deduct credits while the Unlimited toggle is on. It is model-specific, resolution-capped and time-limited. It is not "everything free".
  Source: https://higgsfield.ai/creator-hub/help-center/credits/what-are-unlimited-models-and-which-plans-include-them (3 Aug 2026)
- **Two kinds:**
  - A **365-day set**: Seedream 5.0 Lite, FLUX.2 Pro 1K, Seedream 4.5, Nano Banana (the original), Kling O1 Image and GPT Image. Plus and Ultra get the full set. Starter gets only Seedream 5.0 Lite and FLUX.2 Pro 1K.
  - **7-day windows** on flagship models.
- **Nano Banana Pro is only ever in a 7-day window, and only up to 2K.**
  - Per the 24 Oct explainer: Ultra (monthly or annual) gets 7 days of Nano Banana Pro at 1K/2K. Plus gets only Nano Banana 2.
  - Per the 30 Oct "7-Day Unlimited Bonus" (a limited-time offer): Nano Banana Pro up to 2K for 7 days on Max and Ultra (monthly) and on all annual plans. Not on Starter.
  - Sources: https://higgsfield.ai/blog/higgsfield-pricing-explained and https://higgsfield.ai/blog/higgsfield-7-day-unlimited-bonus (30 Oct 2026)
- **The screenshot's 4K setting is not covered by Unlimited.** Unlimited is capped at 2K, so 4K Nano Banana Pro images would still cost credits (4 each) **(inferred from the published caps)**.
- **Limits that still apply:**
  - Unlimited runs in the slower standard queue. Credit generations get the priority queue.
  - Only 2 unlimited image jobs and 1 unlimited video job can run at once, across all models.
  - Unlimited works only on higgsfield.ai. It does not apply through MCP, CLI, API, Canvas, Supercomputer or Marketing Studio.
  - It stops working if the subscription lapses.
- **The XP promo** ("8 more images for +10 XP / 215 XP to your 7 Days Unlimited Nano Banana Pro reward") looks like an in-app gamified reward: you earn XP by generating and unlock a 7-day Unlimited window. No public documentation of the XP programme was found **(unverified)**. Expect it to have the same 2K cap and queue rules as above.
- Old "1 year unlimited Nano Banana Pro" deals were time-limited (Black Friday 2025) and have expired.

### Commercial-use terms

- Higgsfield Help Center (2 Aug 2026), citing Terms of Use section 4.4:
  - You own your inputs and outputs, and commercial use is not restricted. The help center explicitly lists "YouTube monetization".
  - Paid plans give watermark-free downloads.
  - Higgsfield may use your content to train its models until you delete it. Enterprise contracts are excluded. **This matters for photos of Ace and any reference images.**
  - You must have rights to anything you upload, including likeness consent for real people.
  - Indemnification is Enterprise only.
  - Source: https://higgsfield.ai/creator-hub/help-center/account/who-owns-my-generations-and-can-i-use-them-commercially
- Conflict: the 24 Oct pricing table marks Free as "Commercial use: No", while the help center says rights are not tied to plan. Treat the Free plan as non-commercial, if only because of the watermark.

### Video models on Higgsfield (site footer, 7 Nov 2026)

- Third-party models: Seedance 2.5, Seedance 2.0, Kling 3.0, Kling 4.0, Veo 3.1, WAN 2.6, Grok Imagine 1.5, Gemini Omni Flash.
- Higgsfield's own tools: Cinema Studio, Soul / Soul ID characters, Higgsfield Speak, Wan 2.5 Speak (lipsync), Genjutsu (video-to-video), Marketing Studio UGC.
- The blog also mentions MiniMax Hailuo 2.3 and Wan 3.0.
- Sora 2 still appears on some Higgsfield pages, but third parties report that OpenAI shut down the Sora API on 24 Sep 2026 **(unverified)**.

---

## 2. Nano Banana Pro (Gemini 3 Pro Image)

**What it is:** Google DeepMind's top image generation and editing model, launched 20 Nov 2025 (TechCrunch).
- It "thinks" before rendering, renders text well, and outputs 1K, 2K or 4K.
- Every output carries an invisible SynthID watermark.
- Google has since added cheaper siblings: Nano Banana 2 (Gemini 3.1 Flash Image) and Nano Banana 2.1.

**Reference images and character consistency (confirmed in Google docs):** Gemini 3 Pro Image accepts **up to 14 reference images**. That breaks down as up to 6 object images "with high fidelity", up to 5 character images "to maintain character consistency", and up to 3 style references.
For Annie, that means:
- Feed Ace's real photos as object/character references.
- Feed one or two "hero" frames of Annie's lips, nails and ring as character references.

Source: https://ai.google.dev/gemini-api/docs/image-generation (fetched 7 Nov 2026)

### Price per image (fetched 7 Nov 2026 unless marked)

| Where | 1K | 2K | 4K | Notes |
|---|---|---|---|---|
| Google Gemini API / AI Studio (`gemini-3-pro-image`) | $0.134 | $0.134 | $0.24 | Paid tier only, no free API tier (testable in AI Studio). Reference image input about $0.0011 each. Batch about half price (per third parties, **unverified**). https://ai.google.dev/gemini-api/docs/pricing |
| Replicate `google/nano-banana-pro` | $0.15 | $0.15 | $0.30 | Takes an `image_input` array for references; aspect ratios include 9:16. https://replicate.com/google/nano-banana-pro |
| fal.ai `fal-ai/nano-banana-pro` | $0.15 | $0.15 | $0.30 | +$0.015 if web search is used. https://fal.ai/models/fal-ai/nano-banana-pro |
| Replicate `google/nano-banana-2` (cheaper sibling) | $0.067 | $0.101 | $0.151 | https://replicate.com/google/nano-banana-2 |
| Google `gemini-nano-banana-2.1` | $0.034 | $0.050 | $0.113 | Google API only. https://ai.google.dev/gemini-api/docs/pricing |
| Higgsfield | 2 credits (about $0.075 to $0.15 depending on plan); 4K is 4 credits | | | 7-day Unlimited up to 2K on Ultra or annual plans (see section 1) |
| Freepik (now rebranded Magnific) | about $0.075/image on Premium monthly (75 credits); unlimited on its Pro plan | | | BudgetPixel, checked 24 Sep 2026 **(unverified)** |
| OpenArt | about $0.14/image on Starter (40 credits; 80 at 4K) | | | BudgetPixel, 24 Sep 2026 **(unverified)** |
| Krea | API $0.15 (4K $0.30); app image counts conflict | | | BudgetPixel, 24 Sep 2026 **(unverified)** |
| Gemini app (Google AI plans) | included with usage limits | | | No per-image price |

Third-party comparison: https://budgetpixel.com/data/ai-generation-price-index/nano-banana-pro (checked 24 Sep 2026; a competitor's page, so treat as indicative).

Commercial use: the Gemini API terms say "Google won't claim ownership over that content", and you are responsible for how you use it (https://ai.google.dev/gemini-api/terms, fetched 7 Nov 2026).

---

## 3. Realistic image-to-video models (Replicate preferred)

All the models below accept a start image (image-to-video). Replicate prices are per second of output unless noted, read from each model page on 7 Nov 2026. **ASMR inserts need no generated audio, so the "without audio" price is the relevant one.**

| Model (Replicate slug) | Price, no audio | 5s clip cost | Length | Useful extras |
|---|---|---|---|---|
| **Kling 4.0** `kwaivgi/kling-v4.0` | 720p $0.157/s; 1080p $0.235/s | $0.79 (720p) / $1.18 (1080p) | 3 to 30s | start image, **end image**, reference images, video editing |
| **Kling 3.0** `kwaivgi/kling-v3-video` | standard $0.168/s; pro $0.224/s; 4K $0.42/s | $0.84 / $1.12 | 3 to 15s | start and end image |
| Kling 2.6 `kwaivgi/kling-v2.6` | $0.07/s | $0.35 | 5 or 10s | start image (older generation) |
| **Veo 3.1 Fast** `google/veo-3.1-fast` | $0.10/s (with audio $0.15) | 4s $0.40, 6s $0.60 (no 5s option) | 4, 6 or 8s | start image + **last_frame** (good for loops), 720p/1080p, 9:16 |
| Veo 3.1 `google/veo-3.1` | $0.20/s (with audio $0.40) | 6s $1.20 | 4, 6 or 8s | top quality, pricey |
| Veo 3.1 Lite `google/veo-3.1-lite` | 720p $0.05/s; 1080p $0.08/s | 4s $0.20 | 4, 6 or 8s (1080p must be 8s) | budget Veo |
| **Gemini Omni 1.2 Flash** `google/gemini-omni-1.2-flash` | 720p $0.105/s; 1080p $0.155/s (audio native) | $0.53 (720p) | 3 to 15s | start image + reference images; Google says up to 6 refs for character consistency. Direct on the Gemini API it is about $0.07/s at 720p |
| **Seedance 2.0 Fast** `bytedance/seedance-2.0-fast` | 480p $0.07/s; 720p $0.15/s | $0.75 (720p) | up to 15s | first frame or reference images (not both together) |
| Seedance 2.0 `bytedance/seedance-2.0` | 720p $0.18/s; 1080p $0.45/s | $0.90 / $2.25 | up to 15s | multimodal references |
| Seedance 1.5 Pro `bytedance/seedance-1.5-pro` | 720p $0.026/s; 1080p $0.06/s | $0.13 / $0.30 | 4 to 12s | cheapest credible option to try |
| Hailuo 2.3 `minimax/hailuo-2.3` | 768p 6s $0.28 per video; 1080p 6s $0.49 | $0.28 (6s) | 6 or 10s | first frame |
| MiniMax H3 Lite `minimax/h3-lite` | 768p $0.02/s | $0.10 | 4 to 15s | first and last frame, references (successor to Hailuo) |
| **Wan 3.0** `alibaba/wan-3` | 480p $0.035/s; 720p $0.07/s; 1080p $0.14/s | $0.35 (720p) | 2 to 30s | first frame |
| Wan 2.7 i2v `wan-video/wan-2.7-i2v` | 720p $0.10/s; 1080p $0.15/s | $0.50 | 2 to 15s | first and last frame |
| Wan 2.2 i2v fast `wan-video/wan-2.2-i2v-fast` (current pipeline) | 480p $0.05 per video; 720p $0.11 | $0.05 | short | **The $0.05 the pipeline pays is the 480p tier**, which partly explains the fake look |
| Runway Gen-4.5 `runwayml/gen-4.5` | $0.12/s | $0.60 | 5 or 10s | first frame |
| Luma Ray 3.2 `luma/ray-3.2` | 720p SDR 5s $0.30; 1080p $1.20 | $0.30 | 5 or 10s | HDR options |

fal.ai comparisons (fetched 7 Nov 2026):
- Kling 3.0 Pro i2v: $0.112/s without audio, half of Replicate's $0.224. https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video
- Veo 3.1 Fast i2v: $0.10/s without audio, $0.15 with, at 720p/1080p. Same as Replicate. https://fal.ai/models/fal-ai/veo3.1/fast/image-to-video

**Strengths with hands, lips and animals.** No controlled public test of hands or cats was found, so everything in this paragraph is **unverified or anecdotal** and Ann's own test is the real answer.
- Reviewers rate Kling 3.0/4.0 strongest for human motion and "character beats".
- Reviewers rate Seedance strongest for product-style close-ups and prompt adherence.
- Reviewers rate Veo 3.1 strongest for lighting and texture, but one guide says Veo's consistency softens on close-up human shots.
- Wan 3.0 tops some leaderboards.
- Sources: https://higgsfield.ai/blog/5-Best-AI-Video-Models-2026-Tested-Compared and https://www.teamday.ai/blog/best-ai-video-models-2026
- Practical point: fast, cheap 480p tiers (such as the current Wan 2.2 fast) are where hands warp most. Moving up to a 720p or 1080p flagship tier, with prompts asking for slow, minimal motion, is the main realism lever.

---

## 4. Commercial use and YouTube rules

**Using the outputs commercially.**
- Replicate's terms (section 5.1) say the customer owns its "Customer Data", which includes Outputs. Marketplace models may also carry the provider's own terms, so check each model page **(not checked model by model)**. https://replicate.com/terms
- Google says it won't claim ownership of generated content.
- Higgsfield explicitly allows YouTube monetization on paid plans.
- None of these bans monetized YouTube use.

**YouTube disclosure rule (Help Center, fetched 7 Nov 2026).**
- Creators must disclose AI-generated or meaningfully altered content that seems realistic, using the **"AI use"** setting in YouTube Studio at upload. This covers content that "generates a realistic scene that didn't actually occur".
- Beauty filters, colour fixes, upscaling and AI help with scripts or thumbnails do not need disclosure.
- A photoreal AI hand stroking a cat, or AI lips, counts as realistic synthetic content, so **turn the disclosure on for any video that contains the AI inserts.**
- Source: https://support.google.com/youtube/answer/14328491
- Secondary reports say that since May 2026 the label for photoreal content shows directly under the player, and that YouTube can apply labels automatically (SynthID from Veo and Nano Banana is detectable) **(unverified)**: https://minimatters.com/youtube-ai-content-labeling-update-in-may-2026/
- YouTube says the label alone does not affect ranking. Repeated non-disclosure can lead to labels being added, content removed or YPP suspension.

**Monetization risk: "inauthentic content" (YPP policy, fetched 7 Nov 2026).**
- On 15 July 2025 YouTube renamed "repetitious content" to "inauthentic content". Mass-produced or repetitive content is not monetizable.
- The current policy lists as not monetizable:
  - channels relying on "generic templates";
  - "videos that stitch together unrelated or inconsistent AI clips";
  - AI personas giving health, legal, financial or political advice.
- It lists as monetizable: content using AI "to visualize a unique character and narrative you invented", where "the final product must still demonstrate your creative vision".
- Source: https://support.google.com/youtube/answer/1311392
- What this means for Annie:
  - Real footage of Ace, plus a consistent invented character, plus original ASMR audio fits the "allowed" side.
  - The risks are near-identical uploads (the same loop with a new title), heavy reuse of one AI clip across many videos, or inconsistent AI hands that look like "AI slop".
  - Keep each video distinct with different triggers, scenes and real audio.
  - Do not let "Annie" give sleep or health advice framed as expertise.

---

## 5. Recommendation

### Workflow that gives the most realistic result for the least money

1. **Make the start frames with Nano Banana Pro (Replicate `google/nano-banana-pro`, 2K, 9:16, $0.15 each).** Pass 3 to 5 **real photos of Ace** plus one Annie "hero" image (lips, nails, ring) as `image_input` references.
   - Better still for Ace: start from a **real frame of Ace from Ann's phone footage** and ask Nano Banana Pro to add the hand. This keeps his real markings, because the model only adds the hand.
2. **Animate with a flagship model at 720p, without audio.** Prompt for "very slow, gentle, minimal motion, static locked-off camera".
   - Where available, use start and end frames that match (Veo 3.1 Fast `last_frame`, Kling 4.0 `end_image`, Wan 2.7 `last_frame`) so clips loop seamlessly.
   - Slow the clips down a further 50 to 70% in the edit; ASMR suits that.
3. Upscale in the editor if needed. Upscaling does not need disclosure on its own.

### Realism test (two clips: hand stroking Ace, lips/gloss close-up)

**Option A, cheapest credible test: about $3.50 to $4.**

| Item | Cost |
|---|---|
| 6 Nano Banana Pro start frames (3 per shot) | $0.90 |
| Shot 1 hand + Ace: Kling 4.0 720p 5s ($0.79) and Veo 3.1 Fast 6s, no audio ($0.60) | $1.39 |
| Shot 2 lips: Kling 4.0 720p 5s ($0.79) and Veo 3.1 Fast 6s ($0.60) | $1.39 |
| **Total** | **about $3.68** |

**Option B, broader bake-off: about $7.**
Option A plus Seedance 2.0 Fast 720p ($0.75) and Wan 3.0 720p ($0.35) on each shot: $3.68 + $2.20 = **about $5.90**. Add one retry of the best model on each shot for about **$7**.

Option B shows within one evening which model handles Ace's fur and Annie's fingers best. No subscription is needed: Replicate is pay-as-you-go and already set up.

### Monthly budget, 2 long videos a week (about 8.7 a month), AI only for short inserts

Assumptions:
- Each finished insert is 5s.
- About 2.5 generations are needed per keeper.
- 40 images a month for start frames ($6), up to 100 in the heavier scenario ($15).
- No audio generated.

| Scenario | Keepers per month | Generations | Kling 4.0 720p | Veo 3.1 Fast (6s) | Wan 3.0 720p | + images | Approx. monthly total |
|---|---|---|---|---|---|---|---|
| **Lean: reusable insert library** (about 20 new inserts a month, rotated across videos) | 20 | 50 | $39 | $30 | $18 | $6 | **$24 to $45** |
| **Standard: 4 fresh inserts per video** | 35 | 88 | $69 | $53 | $31 | $10 | **$41 to $79** |
| **Heavy: 6 fresh inserts per video** | 52 | 130 | $102 | $78 | $46 | $15 | **$61 to $117** |

Comparison with Higgsfield:
- Higgsfield Plus ($49/mo, 1,000 credits) covers about 28 Seedance 2.5 720p 5s clips, or about 33 Kling/Seedance 2.0 720p clips, with no rollover. That is roughly the Lean or Standard scenario at a similar price.
- Its Nano Banana Pro "Unlimited" needs Ultra ($129) or an annual plan and is capped at 2K.
- Higgsfield only wins if Ann wants its UI or presets. For an existing Replicate pipeline, pay-per-clip on Replicate is cheaper at this volume and has no lock-in.
- Higgsfield may also train on uploads, Ace's photos included.

**Suggested starting budget:** about $40/month (the Lean to Standard range), set as a spending limit in Replicate. Use Kling 4.0 or Veo 3.1 Fast, whichever wins the test, for hero inserts and Wan 3.0 for filler. Reuse and rotate a growing library of inserts rather than generating new ones for every video.

---

## Source list (all fetched 7 Nov 2026 unless noted)

- Higgsfield pricing explainer (24 Oct 2026): https://higgsfield.ai/blog/higgsfield-pricing-explained
- Higgsfield 7-Day Unlimited Bonus (30 Oct 2026): https://higgsfield.ai/blog/higgsfield-7-day-unlimited-bonus
- Higgsfield Unlimited help (3 Aug 2026): https://higgsfield.ai/creator-hub/help-center/credits/what-are-unlimited-models-and-which-plans-include-them
- Higgsfield ownership and commercial use (2 Aug 2026): https://higgsfield.ai/creator-hub/help-center/account/who-owns-my-generations-and-can-i-use-them-commercially
- Higgsfield pricing page (JS-rendered; navigation only): https://higgsfield.ai/pricing
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google image generation docs (14 references): https://ai.google.dev/gemini-api/docs/image-generation
- Gemini API terms: https://ai.google.dev/gemini-api/terms
- Replicate model pages: https://replicate.com/google/nano-banana-pro, /google/nano-banana-2, /kwaivgi/kling-v4.0, /kwaivgi/kling-v3-video, /kwaivgi/kling-v2.6, /google/veo-3.1, /google/veo-3.1-fast, /google/veo-3.1-lite, /google/gemini-omni-1.2-flash, /bytedance/seedance-2.0, /bytedance/seedance-2.0-fast, /bytedance/seedance-1.5-pro, /minimax/hailuo-2.3, /minimax/h3-lite, /alibaba/wan-3, /wan-video/wan-2.7-i2v, /wan-video/wan-2.2-i2v-fast, /runwayml/gen-4.5, /luma/ray-3.2
- Replicate terms: https://replicate.com/terms
- fal.ai: https://fal.ai/models/fal-ai/nano-banana-pro, https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video, https://fal.ai/models/fal-ai/veo3.1/fast/image-to-video
- BudgetPixel price index (checked 24 Sep 2026, third party): https://budgetpixel.com/data/ai-generation-price-index/nano-banana-pro
- YouTube AI disclosure: https://support.google.com/youtube/answer/14328491
- YouTube monetization policies (inauthentic content): https://support.google.com/youtube/answer/1311392
- Secondary or unverified: https://minimatters.com/youtube-ai-content-labeling-update-in-may-2026/ , https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs , https://endless.app/blog/higgsfield-pricing , https://www.teamday.ai/blog/best-ai-video-models-2026 , https://techcrunch.com/2025/11/20/google-releases-nano-banana-pro-its-latest-image-generation-model/
