# Tideglyph social studio

The self-contained engine for Tideglyph's organic posts. A fresh cloud session uses this to generate, build and schedule a week of content. Everything here runs offline except the final Metricool scheduling.

## Fixed facts
- Metricool brand id (Tideglyph): 7442919. NEVER post to any other brand. BBD is separate.
- Media host: this repo, Biz-Builder/OmnistrataMedia (public). Raw URL pattern: https://raw.githubusercontent.com/Biz-Builder/OmnistrataMedia/main/<path>
  - Today's sky cards: tideglyph/todays-sky/YYYY-MM-DD.png. Today's sky Reels: tideglyph/reels/YYYY-MM-DD.mp4. Pillar cards: tideglyph/pillars/YYYY-MM-DD.png.
- Timezone: Africa/Johannesburg (UTC+02:00). Daily slots: 07:00 (today's sky, as a Reel) and 18:00 (a pillar, static card, US-facing).
- Networks: Facebook and Instagram, as SEPARATE posts (from 26 Oct 2026). TikTok @tideglyph (Business account, connected to brand 7442919 on 7 Nov 2026) gets the 07:00 Reel only, as its own third post. EXCEPTION 12 to 25 Nov 2026: the TikTok format test below replaces this.

## Why the format is what it is (decided 24 Oct 2026)
- Organic reach was 34 people across 24 posts in week 2. Static posts on a new account reach almost only followers. Reels are the format Instagram shows to non-followers, so the daily today's sky post is a Reel.
- Facebook gets its own post with a clickable, tagged link, because Umami can now count visits per organic post. Instagram cannot carry links, so it keeps "link in bio".
- The Meta ads bring about 120 visitors a day, and the "One in twelve" angle brings most of them. Organic posts support the ads: they repeat that message, show what the free chart actually is, and make the profile make sense to anyone who checks it after seeing an ad.

## Voice rules (every line)
- Reflection, never prediction. Name what the sky is doing, then invite noticing. No forecasts.
- No health, money or love claims. No medical or financial advice.
- Plain English that travels to the US and UK. No South African only references, no slang.
- No em dashes anywhere.
- Write like a person. No "It's not X, it's Y" lines, no lists of absences ("No ads, no tracking, no noise"; one plain absence such as "No card" is fine), no "The result? ..." or "The best part: ..." reveals, no stock phrases ("Unlock", "Say goodbye to", "Here's the thing"), no one-sentence-per-line posts, no engagement bait ("Thoughts?", "Agree?"), no emoji as bullets. End on the point or on a real question.
- Today's sky: one short headline line plus one journal question. Pillars: a hook plus two or three lines, ending on the call to action.

## Setup (once per run)
1. Clone this repo with push access and cd to tideglyph/studio.
2. `pip install pyswisseph --break-system-packages -q`. In the cloud workspace this often fails to build against the system setuptools with an `install_layout` AttributeError. If it does, build it in a fresh venv: `python3 -m venv /tmp/skyenv && /tmp/skyenv/bin/pip install -U pip setuptools wheel -q && /tmp/skyenv/bin/pip install pyswisseph -q`, then run the sky step with that venv (`/tmp/skyenv/bin/python todays_sky.py YYYY-MM-DD`). Only todays_sky.py needs it; make_card.py, make_reel.py and the renderers use the system python and node.
3. `npm install playwright` in studio (chromium is preinstalled; do not run `playwright install`). make_reel.py uses the system ffmpeg, and installs imageio-ffmpeg itself if ffmpeg is missing.
4. Music: make_reel.py mixes Tideglyph's own ambient bed (`audio/tideglyph-bed.m4a`, made by make_music.py, owned outright) under every Reel automatically, starting at a different point per headline. Never add library or trending music; Daniel decided on 7 Nov 2026 to stay hands-off. Photo posts to TikTok set `autoAddMusic: true` and must use JPEG or WebP images: TikTok rejects PNG (learned 7 Nov 2026). Convert with `ffmpeg -i in.png -q:v 2 out.jpg`.

## Weekly batch (the Monday task)
For each of the next 7 days:
1. If `tideglyph/todays-sky/YYYY-MM-DD.json` exists in the repo (written daily by Alex's job from the product's own endpoint), use its `transit_label`/`headline_transit.label`, `reading` and `journal_question` as the today's sky words. Otherwise run `python3 todays_sky.py YYYY-MM-DD` and write the words yourself from its transit_label, under the voice rules.
2. Write that day's 18:00 pillar post. This week's rotation, one per day, no repeats (see "Pillars" below).
3. Build the media:
   - VISUALS (decided by Daniel 11 Nov 2026, do not revert to the plain typographic cards): every Instagram and Facebook post uses `make_photo.py`, a real photo from `tideglyph/photos` with the words over it and the one promise ("Find your big three, free" button and tideglyph.com/chart) underneath. Rotate photos so no photo repeats on consecutive days: sky-* photos for today's sky, people-* photos for pillars.
   - Today's sky: spec.json `{"layout":"sky", "photo":"sky-dusk.jpg", "eyebrow":"Today's sky \u00b7 26 October", "tag":<the transit in plain words>, "hook":<headline>, "sub":<journal question>}`. Run `python3 make_photo.py spec.json ../reels-photo/YYYY-MM-DD.mp4 --reel` (9 s, own music bed, about 2 minutes). Keep the spec as `../reels-photo/YYYY-MM-DD.json`.
   - Pillar: spec.json `{"layout":"pillar", "size":"feed", "photo":"people-window.jpg", "focus":"50% 35%", "eyebrow":<topic>, "hook":<headline>, "sub":<two plain sentences>}`, then `python3 make_photo.py spec.json ../pillars-photo/YYYY-MM-DD.png`. Every pillar leads back to the big three; the card shows Sun, Moon, Rising and five planets under the sub.
   - Ads use the same renderer with `"layout":"ad"` (example big three card), feed and story sizes, in `../ads-2026-11-photo/`.
   - Look at every render before scheduling: text clear of the face in people photos (adjust `focus`), nothing cut off, the button visible.
4. Commit and push (fetch and rebase first, the repo is shared with other brands). Confirm one raw PNG URL and one raw MP4 URL load.

## Pillars (18:00)
Rotate through these, one per day. Each supports the ads.
1. **One in twelve.** The whole-chart differentiator in the words of the winning ad: a Sun sign is shared with one in twelve people; the whole chart is close to one of a kind. Vary the angle each week. Best performer so far: "Two people born weeks apart can share a star sign and still have almost nothing else in common on the chart."
2. **What the free chart shows.** Show the product: the seven signs (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn), each with its one line. Use a clearly labelled example, never a real person's data.
3. **Don't know your birth time?** The chart works with the birth date alone: Sun, Moon and five planets, and the rising sign can be added later. Facebook link goes to /chart, tagged, like every other post (since 11 Nov 2026 every post points to /chart).
4. **Privacy.** Tideglyph does not sell personal information, and the journal is private. Facts only from the privacy notice. Never say "no tracking" or "no analytics": the site now runs cookieless Umami analytics.
5. **The journal.** The daily reading plus a private journal that remembers.
6. **A plain explainer.** Rising, Moon, big three or Saturn return. Do not repeat the last week's topic.
7. **Sign spotlight.** The current season's sign, through the whole-chart lens, never as a horoscope. Avoid generic Sun-sign openers; the weakest post of week 2 was "As the Sun finishes its trip through Libra".

## Schedule (veto model)
Each slot is separate Metricool posts in brand 7442919, autoPublish true, same time, same media: three at 07:00 (Instagram, Facebook, TikTok), two at 18:00 (Instagram, Facebook):

| Slot | Instagram post | Facebook post | TikTok post |
| --- | --- | --- | --- |
| 07:00 today's sky | `instagramData: {type: "REEL", showReelOnFeed: true}`, media = the Reel's raw MP4 URL, `videoCoverMilliseconds: 7500` | `facebookData: {type: "REEL"}`, same MP4, `videoCoverMilliseconds: 7500` | `tiktokData: {privacyOption: "PUBLIC_TO_EVERYONE", title: <the headline line>, autoAddMusic: false, isAigc: false}`, same MP4, `videoCoverMilliseconds: 7500` |
| 18:00 pillar | `instagramData: {type: "POST"}`, media = the pillar PNG | `facebookData: {type: "POST"}`, same PNG | none |

Captions:
- Instagram caption ends with: "Find your big three, free: link in bio." (one promise from 11 Nov 2026: ads, site and posts all say "Find your big three, free")
- Facebook caption ends with the tagged link (no shortener):
  `https://tideglyph.com/chart?utm_source=facebook&utm_medium=organic_social&utm_campaign=tideglyph_organic&utm_content=YYYY-MM-DD_sky` (07:00) or `..._pillar` (18:00). Every post links /chart; no post links the other calculators.
- TikTok caption: the headline line, the journal question, then "Find your big three: tideglyph.com/chart" as plain text (TikTok captions carry no clickable link). Add three or four plain hashtags at the end: #astrology #birthchart #bigthree plus the day's sign or planet. Once the TikTok bio link is live, end with "Find your big three, free: link in bio." instead.
- `isAiGenerated` (Instagram) and `isAigc` (TikTok) stay false: the photos are AI stills composited into designed cards and Reels, and Meta organic only requires the flag for photorealistic AI video or audio. Raise it with Daniel before switching on.

After scheduling, send Daniel the Metricool planner link and a one-line summary per day so he can edit or pull anything before it fires. Flag any line that could read as a prediction so his eye goes straight to it.

If the Metricool connector is NOT available in this session: still generate, build and push the media and get the raw URLs, then publish a review page listing every post with its media, caption, time and URL, and notify Daniel that the only remaining step is loading them into Metricool.

## Guardrails
- Never schedule to any brand but 7442919. Never touch BBD.
- Keep posting paced: two slots a day on Instagram and Facebook, one on TikTok, never a burst.
- TikTok's bio link needs TikTok's business verification, which Daniel is completing (7 Nov 2026). It should be the clean `https://tideglyph.com/chart`, with no tracking tags (Daniel, 12 Nov 2026: tagged links look dodgy on a profile).
- Instagram's bio link is set by Daniel by hand and stays clean: no tracking tags in any bio link (decided 12 Nov 2026). It is tideglyph.com; tideglyph.com/chart is the optional shorter path. Instagram visits still show in Umami by referrer.
- Pinning is manual in the apps. Daniel pins three explainer posts (one in twelve, what the free chart shows, privacy) once they exist.


## TikTok ads (added 11 Nov 2026)
- Organic TikTok cannot send clicks until the bio link is live (business verification pending). Captions and comments are not clickable. Paid TikTok ads carry their own clickable button, so they work before the bio link.
- Creative: 9:16 videos from `make_big3_video.py` (hook, then Sun, Moon and rising reveal, then "Find your big three, free"), 10 s, with the Tideglyph music bed, inside the TikTok safe zone (170 px clear on the right). Files: `tideglyph/tiktok-ads-2026-11/`.
- Landing page: `https://tideglyph.com/chart?utm_source=tiktok&utm_medium=paid_social&utm_campaign=tideglyph_bigthree_nov26&utm_content=<angle>` (oneintwelve, oneofthree, knowyours). No TikTok pixel, same as Meta.
- Set up in TikTok Ads Manager (self-serve is available in South Africa) by Daniel, or through the TikTok for Business connector once it is connected. Objective Traffic, optimise for clicks, South Africa, ages 18 to 44, TikTok placement only, three ads in one ad group. Same stop rule as Meta: an ad that spends R100 without 5 `form-start` events in Umami (filter utm_source=tiktok) is switched off.

## TikTok format test, carousel vs Reel (12 to 25 Nov 2026)
- Question: on TikTok, does a photo carousel or a video Reel of the SAME idea get more reach and action? BBD's TikTok grows on carousels; Tideglyph has only posted Reels. Comparing the two brands is not a fair test, so this runs inside Tideglyph.
- Two TikTok posts a day, 12 hours apart, at 07:00 and 19:00. Both carry the same idea, the same words and the same caption; only the format differs. The order swaps each day (12 Nov is day 1. Odd days: carousel 07:00, Reel 19:00. Even days: Reel 07:00, carousel 19:00) so time of day does not decide the result.
- No today's sky Reel on TikTok during the test (the old 07:00 TikTok sky posts for 12 to 15 Nov were set to draft). Instagram and Facebook carry on unchanged.
- Build: write a spec (id, then 5 slides: hook, three body slides, cta) and run `python3 make_slides.py spec.json ../tiktok-test-2026-11`. It writes `<id>-01.jpg` to `<id>-05.jpg` (carousel) and `<id>.mp4` (the same slides, 2.6 s each with a fade, own music bed).
- Ideas are evergreen big three teaching, one per day: the Sun is one of three, why horoscopes feel off, no birth time, Moon sign, rising sign, the big three as a set, and similar. Hooks are short and concrete; slide 5 is the button "Find your big three, free" with tideglyph.com/chart.
- Carousel post: the 5 JPEGs, tiktokData autoAddMusic true, photoCoverIndex 0. Reel post: the MP4, videoCoverMilliseconds 500, autoAddMusic false, isAigc false. Both PUBLIC_TO_EVERYONE, title = the hook, autoPublish true.
- Caption: one or two lines of the idea, a comment prompt where it fits, then "Find your big three: tideglyph.com/chart" and four hashtags.
- Scheduled so far: 12 to 15 Nov (log.json event "tiktok-format-test"). The Monday batch builds the rest through 25 Nov.
- Read-out (Friday reviews of 20 and 27 Nov): per format, average views, (shares + saves) per view, profile visits and follows. If carousels beat Reels by 50% or more on views or on shares plus saves per view, carousels become TikTok's main format; if not, keep Reels. Under 8 posts per format is a lean, not a verdict.
