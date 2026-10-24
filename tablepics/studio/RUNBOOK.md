# TablePics studio runbook

The single source of truth for TablePics organic content. The Monday batch and the Friday review follow this file. If the brand-marketing skill is available, load it for the method; this file wins for anything TablePics-specific.

## Fixed facts

- Product: TablePics, an OmniStrata brand. QR cards on each table, guests scan with the phone camera and add photos and videos to one private album. No app, no guest account, full quality.
- Tiers: Essentials R299 and Full R499, paid once for one event, no fee for each guest. Full adds the live slideshow, a moderator, voice notes and photo checks. Check every claim against tablepics.co.za (read the live page in the browser or with a direct fetch, never trust a summary) before it goes out.
- Audiences, never blended in one post: year-end function organisers, engaged couples, milestone birthdays. Any other event only as a light extra.
- Handles: @tablepix on Instagram and Facebook. TikTok not yet created.
- Metricool brand id **7462744** (TablePics). Never any other brand id.
- Ad account 1642736234081287, ads named "TP | ...". Umami website 0e8aa57c-48c8-4647-9468-e095d07bdc64 (analytics.omnistrata.co.za).
- Timezone Africa/Johannesburg.

## Rules that never bend

1. Problem first, then the fix. Image headlines are seven words or fewer, with a short kicker above.
2. Photos of people on every cover and Reel opener. No flat colour-block covers.
3. No em dashes anywhere.
4. Product rules that may change (the upload window, refunds, limits) are worded to stay true under the current site and the draft plans in Confluence. Today: say "uploads can open up to 7 days before" and "on the night and in the days after". Never say "30 days after".
5. Instagram `isAiGenerated` stays false. Switch it on only where a platform rule requires it (Meta organic: photorealistic AI video or realistic AI audio). Cover photos are AI stills, the Reels are typographic designs, so false.
6. Veto model: posts are scheduled to publish automatically and Daniel vetoes by deleting in Metricool or replying. Anything unsure goes in as a Metricool draft and is flagged first in the summary.
7. Changing a post that is already scheduled needs Daniel's explicit yes for that batch. (On 20 Oct he approved swapping slide 1 on every queued post for a photo cover, and the upload-window rewording. Anything beyond that, ask.)

## Why the plan is what it is (decided 24 Oct 2026)

- Organic reach on the new account is tiny (Instagram 4 to 16 people per post, Facebook 1 to 38, in the first 8 days). Tideglyph saw the same: static posts reach almost only followers. Reels are the format shown to non-followers.
- The ads bring nearly all site visitors (about R1.79 per landing page view). Organic supports the ads: repeat the best ad angles, show the product working, and make the profile make sense to someone who checks it after an ad.
- Best ad angles so far (by landing page views): Guest book (weddings), January (year-end), On their phones (birthdays).
- The weak point is landing page to order (0 orders from 393 paid visits to 24 Oct). Alex is building the order form onto each event page (Confluence: TablePics build requests).

## The weekly plan

| Slot | What | Networks |
| --- | --- | --- |
| Tue 12:30 | Carousel or single photo post | Instagram + Facebook, separate posts |
| Tue 18:30 | Product Reel | Instagram REEL + Facebook REEL, separate posts |
| Thu 18:30 | Carousel | Instagram + Facebook, separate posts |
| Fri 18:30 | Product Reel | Instagram REEL + Facebook REEL, separate posts |
| Sun 18:30 | Carousel or single photo post | Instagram + Facebook, separate posts |

- Weighted to year-end functions until the end of November, then weddings for the engagement season from 1 December.
- Keep about two weeks queued. Two slots a day at most, never a burst.
- The posts queued before 24 Oct were scheduled to Instagram and Facebook together. Leave them as they are. New posts follow the split below.

## Instagram and Facebook as separate posts

- Instagram caption ends with "Link in bio." plus 4 to 6 hashtags.
- Facebook gets its own post with the same media and a clickable tagged link to the matching event page, no hashtags needed:
  `https://tablepics.co.za/<page>?utm_source=facebook&utm_medium=organic_social&utm_campaign=tablepics_organic&utm_content=YYYY-MM-DD_<kind>`
  where `<page>` is `weddings`, `birthdays`, `year-end-functions` or nothing for the home page, and `<kind>` is `reel`, `carousel` or `single`.
- Umami then counts the visits per organic Facebook post (utm_content).

## Making posts

Setup: `pip install playwright qrcode --break-system-packages` if missing; Chromium is preinstalled, never run `playwright install`; ffmpeg is on the system.

- **Carousel slides** (1080x1350): `python3 render.py batch.json outdir`. batch.json maps a post key to `{"slides": [...]}`. Slide fields: `h` (headline, `*phrase*` turns gold), `b` (body), `kick`, `size`, `items`, `light`, `t` (`hook`, `step` with `n`, `compare` with `ca`/`cb`, `cta`), `v` (visual: `tent`, `phone`, `scatter`, `none`). See the October batch in the repo history for examples.
- **Photo cover** for slide 1 and single photo posts: `python3 render_cover.py covers.json outdir`, with `{"key": {"photo": "<path>", "kick": "...", "head": "Line one<br>*line two.*", "n": <slide count, 0 for a single>, "pos": "center 30%"}}`. The class names in render.py (`.s1`, `.s2`, `.s3`) are taken; use others in new templates.
- **Product Reel** (1080x1920, 14 s): `python3 make_reel.py spec.json out.mp4` with `{"photo", "kick", "hook", "end", "price"}`. Scenes: the problem over a photo, scan the QR card, the album fills, the offer. Specs in `specs/`. Takes about 2.5 minutes per Reel. Vary the opener photo and hook each week; the middle is the same product demo.
- **Photos**: Canva AI images through the Canva connector (generate-image). For full size, load each media id onto a page of the holder design "TablePics photo export holder" (`DAHYiN1DHhM`), export JPG at quality 95, then start the `Fetch media` workflow in this repo with the export links (REST: `gh api -X POST repos/Biz-Builder/OmnistrataMedia/actions/workflows/fetch-media.yml/dispatches`, ref `main`, input `items` = JSON list of `{"path": "tablepics/photos/<name>.jpg", "url": "<link>"}`). The quota runs out after about 7 images in a burst; plan around it and reuse photos in `tablepics/photos/` and the ad photos before paying. South African settings, racially diverse adults, no children, no text or logos.
- Check every render by eye. Decode any QR code (OpenCV QRCodeDetector): it must read `https://tablepics.com`.

## Media and scheduling

- Media go in this repo: carousels `tablepics/<batch>/<NN-post-name>/NN.jpg`, singles `tablepics/extra-<yyyy-mm>/`, Reels `tablepics/reels/YYYY-MM-DD-<angle>.mp4`. Fetch and rebase before every push (the repo is shared), then confirm one raw URL loads.
- Schedule in Metricool brand 7462744 with autoPublish true. Reels: `instagramData: {type: "REEL", showReelOnFeed: true, isAiGenerated: false}`, `facebookData: {type: "REEL"}`, `videoCoverMilliseconds: 1500`. Posts: type `POST` on both.
- Pinning and highlights are manual in the Instagram app. Daniel pins the How it works post (reposted 24 Oct).

## Open items (as of 24 Oct)

- Three queued posts still have text covers waiting for Canva quota: co-hosts (10 Nov), Function in two weeks (24 Nov), Event date moved (26 Nov). Posts 18 and 19 (24 and 26 Nov) also need the upload-window rewording from rule 4. Daniel approved both changes on 20 Oct.
- Five covers reuse ad photos (birthday, slideshow, signal, photo checks, pricing). Swap for new photos when quota allows, if Daniel agrees.
- Content from 1 December: weddings first.

## Monday batch (every Monday, 07:30)

1. Read this runbook and `log.json` (what is queued, what the last Friday review recommended).
2. In Metricool brand 7462744, list what is scheduled for the next 14 days.
3. Fill any empty slot in the weekly plan for the next 14 days: Reels on Tue and Fri 18:30, carousels or singles in the other slots. Use the best ad angles and the Friday review's one change. Build media, push, confirm URLs, schedule as above.
4. Work the open items when quota allows, within what Daniel has approved.
5. Append a `batch` entry to `log.json` (date, each post with time, network, kind, Metricool id), commit and push.
6. Send Daniel the veto summary: flags first, one line per post, the Metricool planner link.

## Friday review (every Friday, 16:30)

1. Metricool brand 7462744: this week's posts, Instagram reach, saves, shares, likes; Facebook reach, reactions, shares and link clicks. Metricool can report Instagram reach as 0 on a new account for weeks; if so, say so and ask Daniel for the numbers from the Instagram app rather than ranking on zeros.
2. Umami (TablePics website): visitors by channel, by utm_content (ads and organic), and the funnel `choose-tier`, `order-start`, `order-submit`, `payment-cancelled`, paid.
3. Meta ads: spend, landing page views and cost per landing page view per TablePics ad for the week. Report only; propose changes, never make them.
4. Rank the week's organic posts by saves plus shares per reach, name the best and weakest hook and why, and recommend exactly one change for Monday.
5. Send Daniel a summary under 200 words. Append a `review` entry to `log.json`, commit and push. Do not post, schedule or change anything public in this run.
6. End by listing any lesson that applies to every brand and offer to add it to the brand-marketing skill.
