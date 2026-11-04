# AI video options for Annie ASMR (research notes, 4 Nov 2026)

Use case: one consistent anonymous character (photoreal close-ups: lips, long-nail hands, gum, lip gloss, crafts). 8-10 unique clips of 5-10 s per 60-minute video (about 60 s of unique footage), 1-2 videos a week (about 4-9 videos a month). Budget $0 ideally, hard ceiling about $20 a month extra. Must be scriptable (API). Starting stills already exist (Canva).

Labels used: **[official]** = vendor's own page/doc; **[3rd]** = third-party article/aggregator listing; **[judgement]** = my estimate. Research method: web search only. Direct page fetches were blocked in this session (kreatorflow.ai, eggstriker.com, kie.ai failed to resolve), so most prices come from search-result extracts of the pages named. Check the live price page before you rely on any figure.

## 1. How short-drama makers do it

- **They route each shot to a different model** rather than using one tool for everything. Typical routing: Seedance 2.0 for the recurring lead and dialogue/lip-sync, Kling 3.0 for action and motion, Veo 3.1 for cinematic close-ups. [3rd, vendor blogs] Sources: [invideo model routing](https://invideo.io/blog/ai-micro-drama-model-routing/), [Minionarts Seedance 2 vs Kling 3 benchmark](https://www.minionarts.com/blogs/seedance-2-vs-kling-3-microdrama-production-benchmark), [invideo script-to-episode](https://invideo.io/blog/ai-micro-drama-script-to-episode/)
- **How they keep a character consistent:**
  - Reference images: Kling 3.0 "Elements" takes 1-4 reference images per generation, each tagged as character, object or scene.
  - Seedance 2.0 lets you tag a character with @Character. Its 95% identity figure is self-reported.
  - Image-to-video from a fixed start frame: they make a locked "character sheet" still, generate every shot from it, and feed a clean frame from one shot into the next (first/last frame chaining).
  - Character LoRAs on open models (Wan) are the self-host version of the same idea. [3rd] Sources: [codedesigns character consistency](https://codedesigns.eu/ai-video-production-in-2026-character-consistency-finally-makes-it-usable/), [invideo how-to](https://invideo.io/blog/how-to-make-ai-micro-drama/)
- **Pipelines:** script, then storyboard stills (image model), then image-to-video, then edit. Usually multi-agent scripts call Seedance/Kling/Veo/Sora APIs. Open-source examples are under the [GitHub ai-short-drama topic](https://github.com/topics/ai-short-drama). [3rd]
- **Why it's cheap:** they work at industrial scale and on falling Chinese compute prices.
  - Caixin: contract producers cut prices from 800-1,000 yuan to about 200 yuan per finished minute, "close to computing power costs".
  - C21/NYT: as little as about US$30 per minute.
  - A Hangzhou producer: a 100-minute drama every 3-7 days for under 20,000 yuan.
  - Only 1.3% of 430,000 titles break even.

  [article] Sources: [Caixin](https://www.caixinglobal.com/2026-06-01/cover-story-how-ai-took-over-chinas-micro-drama-industry-in-90-days-102449814.html), [C21Media](https://www.c21media.net/news/ai-slashing-cost-of-microdrama-production-in-china-to-30-per-minute/), [CNN](https://www.cnn.com/2026/08/22/style/short-drama-ai-china-intl-hnk), [Hello China Tech](https://hellochinatech.com/p/china-470-ai-dramas-a-day), [BigGo](https://finance.biggo.com/news/ad721dc7-6c9c-4cd0-b49f-4de6daee49c3)
- **Lesson for Annie [judgement]:** the consistency trick is almost free. Always start image-to-video from the same Canva still, or from a small set of stills of the same hands and lips. Her character is anonymous (no face), which makes consistency much easier than in drama. The clips get slowed and looped, so 480p-720p and 5 s clips are enough. Upscale afterwards if needed.

## 2. Per-second / per-clip API prices

| Model / tier | Provider | Price | Label, date | 60 s of footage* |
|---|---|---|---|---|
| Wan 2.2 I2V fast (Pruna-optimised) 480p | Replicate | $0.05 per video (blog, Jul 2025); $0.0125 per 480p / $0.025 per 720p video (Replicate tweet, Aug 2025) | [official, but the two disagree] | about $0.15-0.60 |
| Wan 2.2 I2V 480p ultra-fast | WaveSpeed | $0.10 per 5 s run, or $0.01/s (conflicting) | [official pages, unclear] | about $0.60-1.20 |
| Wan 2.2 A14B I2V | fal.ai | $0.04/s 480p, $0.06/s 580p, $0.08/s 720p; Turbo $0.05 / $0.10 per video | [official page, about 460 days old; 3rd confirms] | $2.40-4.80 (Turbo $0.60-1.20) |
| Wan 2.5 i2v preview | Alibaba Model Studio (Singapore) | $0.05/$0.10/$0.15 per s for 480p/720p/1080p; no free quota | [official] | $3-6 |
| Hailuo 2.3 Fast 768p 6 s | MiniMax official API | $0.19 per clip ($0.32 for 10 s); now listed as "legacy V1" | [official, search snippet] | about $1.90 |
| Hailuo 02 Standard 768p | fal.ai | $0.045/s | [3rd] | about $2.70 |
| Kling 2.5 Turbo 5 s | Kie.ai | $0.21 per clip (42 credits); about $0.19 with top-up bonus | [official Kie page via search] | about $2.10-2.50 |
| Kling 2.5 Turbo Pro | fal.ai | $0.07/s (std $0.042/s reported) | [3rd] | $2.50-4.20 |
| Kling 3.0 Std 720p silent | Kling official developer API | $0.084/s; prepaid packs start at $700 | [3rd citing official] | about $5 |
| Veo 3.1 Lite 720p (with audio) | Gemini API | $0.05/s; Vertex video-only reportedly $0.03/s; no free tier. One source claims the Fast/Lite listings shut down on 22 Oct 2026 (unverified) | [3rd quoting Google] | $1.80-3.00 |
| Veo 3.1 Fast 720p | Gemini API | $0.10/s | [3rd quoting Google] | $6 |
| LTX-2.5 Fast 720p | LTX API | $0.09/s | [3rd] | $5.40 |
| Seedance 2.0 Fast 720p | fal.ai | about $0.24/s | [3rd] | about $14 |
| Seedance 2.0 480p | some resellers | about $0.025/s claimed | [3rd vendor] | about $1.50 |

*60 s of footage is assumed to be about 10-12 clips; per-clip prices are scaled accordingly. [judgement]

Sources:
- [Replicate Wan 2.2 blog](https://replicate.com/blog/wan-22), [Replicate tweet](https://x.com/replicate/status/1953057468046819448)
- [WaveSpeed ultra-fast](https://wavespeed.ai/models/wavespeed-ai/wan-2.2/i2v-480p-ultra-fast)
- [fal Wan 2.2](https://fal.ai/models/fal-ai/wan/v2.2-a14b/image-to-video), [aiidelist Wan 2.2 comparison](https://aiidelist.com/blog/cheapest-wan-2-2-api-pricing-2026), [costgoat Wan](https://costgoat.com/pricing/wan-video)
- [Alibaba pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing), [Alibaba free quota](https://www.alibabacloud.com/help/en/model-studio/new-free-quota)
- [MiniMax pricing](https://platform.minimax.io/docs/guides/pricing-video), [Magic Hour Hailuo](https://magichour.ai/blog/hailuo-23-pricing)
- [Kie Kling 2.5](https://kie.ai/kling-2-5), [aireiter Kling API](https://aireiter.com/blog/kling-api-pricing), [costgoat Kling](https://costgoat.com/pricing/kling)
- [inferencehub fal](https://inferencehub.org/providers/fal-ai), [ofox](https://ofox.ai/blog/fal-ai-alternatives-video-generation-api-2026/)
- [8frame Veo tiers](https://www.8frame.co/blog/veo-3-1-standard-vs-fast-vs-lite), [benchlm](https://benchlm.ai/blog/posts/ai-video-generation-models)
- [therundown LTX-2.5](https://www.therundown.ai/tools/ltx-2-5), [atlascloud cheapest](https://www.atlascloud.ai/blog/tips/cheapest-ai-video-generation-api-2026), [seeddance comparison](https://www.seeddance.io/blog/ai-video-api-pricing-comparison)

## 3. "Unlimited" / flat-rate plans

None that I found is usable through an API.

- **Higgsfield:** "unlimited" means time-boxed per-model windows, standard queue, web only. Its MCP, CLI and API spend credits. Plans start at $19.
- **Hailuo:** unlimited video is on the Max plan, about $184/month billed annually, queue-based.
- **Kling:** no unlimited mode.
- **Runway:** Unlimited closed to new subscribers in June 2026.
- **Midjourney:** Relax mode needs the $30 Standard plan; no official API.

All of these are out of budget, manual only, or both. [3rd/vendor] Sources: [Higgsfield unlimited explainer](https://higgsfield.ai/blog/higgsfield-all-unlimited-explained), [Krea on Higgsfield pricing](https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs), [aifunnelinsider](https://aifunnelinsider.com/higgsfield-ai-review-2026/)

## 4. Open-source on rented GPUs

- **Wan 2.2 14B at 720p:**
  - Needs about 65-80 GB of VRAM (an H100).
  - Takes about 10-20 minutes per 5 s clip with reference settings.
  - Costs about $0.35-1.30 per clip at $2-4 an hour.

  [3rd, vendor guides] Sources: [Spheron Wan guide](https://www.spheron.network/blog/deploy-wan-2-1-ai-video-generation-gpu-setup/), [RunPod ComfyUI Wan 2.2](https://www.runpod.io/articles/guides/comfyui-wan-2-2), [Spheron GPU guide](https://www.spheron.network/blog/ai-video-generation-gpu-guide/)
- **Faster options:** the 480p route and the distilled/"Lightning" 4-8 step versions are far faster, but they need ComfyUI setup, model downloads (tens of GB), and a serverless endpoint or a pod you remember to shut down.
- **Verdict [judgement]:** for about 10 clips a week, self-hosting costs more than Replicate/WaveSpeed's optimised Wan endpoints and takes hours to set up. Only worth it if she later wants a custom character LoRA.
- **Licences:**
  - Wan 2.2: Apache 2.0, commercial use allowed. [my knowledge of the model card, not re-verified today]
  - LTX-2.x: free for commercial use under $10M annual revenue. [3rd]

## 5. Free tiers usable via API

All of these are one-time unless stated, and amounts are unverified unless marked.

- **Hugging Face ZeroGPU Spaces** (community Wan 2.2 I2V / "Wan2.2 14B Fast" Spaces), called through `gradio_client`:
  - Daily renewing quota, reportedly about 5 min/day free and about 40 min/day on PRO. PRO gives 8x the free quota [official]; the minute figures are [3rd].
  - API calls may be metered more tightly than browser use [old forum post].
  - Community Spaces can disappear or change.
  - This is the only renewing free source found that a script can call.

  Sources: [HF ZeroGPU AoTI blog](https://huggingface.co/blog/zerogpu-aoti), [HF PRO](https://huggingface.co/pro), [quota forum](https://discuss.huggingface.co/t/what-is-the-quota-on-zerogpu-for-pro-users/94203), [example Space](https://huggingface.co/spaces/duongsd/Wan2.2-I2V-A14B)
- **WaveSpeed:** $1 trial credit for eligible new accounts, no card needed. [3rd, WaveSpeed's own blog]
- **Kie.ai:** 80 free credits for new users (about 2 Kling Turbo clips). [Kie page via search]
- **fal.ai:** $10 or $20 signup credit claimed by blogs. Unverified; treat it as maybe.
- **Replicate:** "small free credits", amount not stated. [3rd]
- **BytePlus ModelArk (Seedance):** free trial quota per model for new users, amount not found. Reportedly not available in the US. [official doc mention]
- **Alibaba Model Studio:** new-user free quota only in the Beijing region, needs identity verification, and none for wan2.5-i2v. [official]
- **Google Veo API:** no free tier. [3rd quoting Google]
- **Web-only daily credits (not API):** Kling 66 credits/day, Google Flow 50/day, Hailuo 200 welcome credits that expire in 3 days. Sources: [apiframe free video API](https://apiframe.ai/blog/free-ai-video-generation-api-2026), [getaiperks](https://www.getaiperks.com/en/blogs/70-free-ai-video-credits-2026), [WaveSpeed free list](https://wavespeed.ai/blog/posts/best-free-ai-video-generators-2026/)

## 6. Commercial / monetisation terms

- **Kling free plan:** watermark, and commercial use excluded or needing permission. Paid plans grant commercial use. [3rd] Sources: [dev.to free-tier comparison](https://dev.to/just_a_side_project/i-compared-the-free-tiers-of-google-flow-kling-ai-and-hailuo-so-you-dont-have-to-2737), [adtestbench](https://adtestbench.com/tools/kling/), [glbgpt](https://www.glbgpt.com/hub/can-i-use-kling-ai-for-commercial-use/)
- **Hailuo web terms:** "personal, non-commercial use only" on free, with watermark. Paid plans get commercial rights and no watermark. [official ToS / 3rd] Source: [Hailuo ToS](https://hailuoai.video/doc/terms-of-service.html)
- **Paid API output (fal, Replicate, WaveSpeed, Kie, MiniMax API):** no watermark. fal says API videos "can be used in commercial projects" but passes through each model owner's terms [official fal page]. Check the ToS of whichever reseller you use.
- **Wan (Apache 2.0) and LTX (under $10M revenue):** the cleanest terms.
- **YouTube:** AI is allowed, but the "inauthentic content" policy (July 2025) demonetises templated, mass-produced videos without real human input. Realistic synthetic media may need the altered-content disclosure. For Annie: keep real human audio and editing, and vary the videos. [3rd] Sources: [eWeek](https://www.eweek.com/news/youtube-responds-to-ai-concerns/), [AIR timeline](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline)

## 7. Free-first router: what to plug in, in what order

What exists already:
- **One-key multi-model aggregators:**
  - fal, Replicate, WaveSpeed, Kie.ai, PiAPI, AIMLAPI.
  - OpenRouter added video in April 2026, with one endpoint, standard parameters (resolution, duration, start/end frame) and async jobs. Models: Seedance 2.0/1.5, Veo 3.1, Wan 2.7/2.6, Sora 2 Pro, Kling O1. A third-party article claims no markup.

  Sources: [OpenRouter announcement](https://openrouter.ai/blog/announcements/video-generation/), [note.com](https://note.com/lucky_allium8251/n/n87f100b52a20?hl=en)
- **n8n:** templates exist for video pipelines, such as PiAPI Kling image-to-video ([n8n 3442](https://n8n.io/workflows/3442-fully-automated-ai-video-generation-and-multi-platform-publishing/)), and n8n has LLM fallback-router patterns. I found no ready-made "free credits first" video router. Sources: [dev.to failover router](https://dev.to/housharenet/zero-downtime-ai-how-to-build-a-multi-model-failover-router-n8n-python-2o9c)
- **Easiest build [judgement]:** a short Python script with an ordered provider list. For each clip it tries the next provider and moves on when it hits a quota, a 402 or 429 error, or a failure. Run providers in sequence, not in parallel, or you pay twice.

Order to plug in [judgement]:
1. **HF ZeroGPU Wan 2.2 I2V Space** via `gradio_client`. Free and renews daily, but slow, quota-limited and liable to break. Worth the $9/month HF PRO only if it proves reliable. The $9 price is unverified.
2. **One-time signup credits, one account each:** WaveSpeed $1, Kie.ai 80 credits, fal (if any), Replicate (if any). These are a few dollars total and do not renew.
3. **Cheapest paid default:** Wan 2.2 fast I2V on Replicate or WaveSpeed (about $0.01-0.10 per clip).
4. **Quality tier for hand/nail hero shots:** Hailuo 2.3 Fast on the MiniMax API ($0.19 per 6 s), or Kling 2.5 Turbo on Kie.ai ($0.21 per 5 s).
5. **Hard stop:** a spending cap in the script (for example $20 a month), plus a prepaid balance only (no auto-top-up).

**Multi-account rule:** do not farm free credits with several accounts.
- Hailuo's terms limit the welcome grant to one per user. [3rd citing official]
- Kling-style terms allow termination for "fraud, abuse". [unofficial-site ToS]
- HF and most providers ban quota evasion. [judgement: standard]
- The risk is losing the account, and with it the commercial rights to the footage.

Sources: [aliteq Hailuo](https://aliteq.com/is-hailuo-ai-free), [Hailuo payment policy](https://hailuoai.video/doc/payment-policy.html)

## 8. Ranked options (cost per 60-min video = about 60 s of unique footage, 10-12 clips)

1. **Replicate (or WaveSpeed) Wan 2.2 fast I2V, 480p/720p, from Canva stills.**
   - Cost: about $0.15-1.20 per video, so about $1-11 a month at 4-9 videos.
   - Automation: yes (official Python client).
   - Quality: good motion, softer detail. Fine fingers and nails can warp. [judgement]
   - Terms: no watermark; Wan is Apache 2.0.
   - Setup: low (API key plus about 40 lines of Python).
2. **MiniMax Hailuo 2.3 Fast official API, 768p 6 s.**
   - Cost: about $1.90 per video, about $8-17 a month.
   - Automation: yes.
   - Quality: better realism and hands. [judgement]
   - Terms: paid API, no watermark; check MiniMax API terms. Listed as "legacy", so it may be retired.
   - Setup: low.
3. **Kling 2.5 Turbo via Kie.ai.**
   - Cost: about $2.10-2.50 per video, about $9-23 a month.
   - Automation: yes.
   - Quality: strongest photoreal close-ups of the three. [judgement]
   - Terms: reseller, so check Kie's ToS.
   - Setup: low.
4. **HF ZeroGPU Wan Space via gradio_client.**
   - Cost: $0, or $9 a month PRO (unverified).
   - Automation: yes, but fragile.
   - Quality: same as option 1.
   - Setup: medium.
5. **Self-hosted Wan 2.2 on RunPod or Vast.**
   - Cost: about $3.50-13 per video at 14B/720p; less with distilled 480p.
   - Automation: yes.
   - Setup: high.
   - Only worth it for a custom LoRA.

**Recommendation within $20:** use option 1 as the default and option 2 for 2-3 hero clips per video. That works out to about $0.60-1.50 per video, comfortably under $20 a month [judgement]. Free HF ZeroGPU can go first in the script. Run one test batch to check that the nails and fingers hold up.
