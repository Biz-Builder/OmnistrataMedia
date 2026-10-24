# Tideglyph social studio

The self-contained engine for Tideglyph's organic posts. A fresh cloud session uses this to generate, build and schedule a week of content. Everything here runs offline except the final Metricool scheduling.

## Fixed facts
- Metricool brand id (Tideglyph): 7442919. NEVER post to any other brand. BBD is separate.
- Media host: this repo, Biz-Builder/OmnistrataMedia (public). Raw URL pattern: https://raw.githubusercontent.com/Biz-Builder/OmnistrataMedia/main/<path>
  - Today's sky cards: tideglyph/todays-sky/YYYY-MM-DD.png. Today's sky Reels: tideglyph/reels/YYYY-MM-DD.mp4. Pillar cards: tideglyph/pillars/YYYY-MM-DD.png.
- Timezone: Africa/Johannesburg (UTC+02:00). Daily slots: 07:00 (today's sky, as a Reel) and 18:00 (a pillar, static card, US-facing).
- Networks: Facebook and Instagram, as SEPARATE posts (from 26 Oct 2026). Add TikTok once its account is connected in Metricool.

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

## Weekly batch (the Monday task)
For each of the next 7 days:
1. If `tideglyph/todays-sky/YYYY-MM-DD.json` exists in the repo (written daily by Alex's job from the product's own endpoint), use its `transit_label`/`headline_transit.label`, `reading` and `journal_question` as the today's sky words. Otherwise run `python3 todays_sky.py YYYY-MM-DD` and write the words yourself from its transit_label, under the voice rules.
2. Write that day's 18:00 pillar post. This week's rotation, one per day, no repeats (see "Pillars" below).
3. Build the media:
   - Today's sky: write spec.json `{eyebrow, tag, headline, journal, cta}` (eyebrow "Today's sky · 26 October", tag = the transit in plain words, cta "Your free chart: tideglyph.com/chart"). Run `python3 make_card.py spec.json ../todays-sky/YYYY-MM-DD.png` AND `python3 make_reel.py spec.json ../reels/YYYY-MM-DD.mp4` (about 40 seconds each Reel).
   - Pillar: spec.json with headline + a short sub as journal and the cta, then `python3 make_card.py spec.json ../pillars/YYYY-MM-DD.png`.
4. Commit and push (fetch and rebase first, the repo is shared with other brands). Confirm one raw PNG URL and one raw MP4 URL load.

## Pillars (18:00)
Rotate through these, one per day. Each supports the ads.
1. **One in twelve.** The whole-chart differentiator in the words of the winning ad: a Sun sign is shared with one in twelve people; the whole chart is close to one of a kind. Vary the angle each week. Best performer so far: "Two people born weeks apart can share a star sign and still have almost nothing else in common on the chart."
2. **What the free chart shows.** Show the product: the seven signs (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn), each with its one line. Use a clearly labelled example, never a real person's data.
3. **Don't know your birth time?** Point to the Moon sign calculator (every Moon sign of your birth date) and the big three calculator (result on the page, no email). Facebook link for this one goes to /moon-sign-calculator, tagged.
4. **Privacy.** Tideglyph does not sell personal information, and the journal is private. Facts only from the privacy notice. Never say "no tracking" or "no analytics": the site now runs cookieless Umami analytics.
5. **The journal.** The daily reading plus a private journal that remembers.
6. **A plain explainer.** Rising, Moon, big three or Saturn return. Do not repeat the last week's topic.
7. **Sign spotlight.** The current season's sign, through the whole-chart lens, never as a horoscope. Avoid generic Sun-sign openers; the weakest post of week 2 was "As the Sun finishes its trip through Libra".

## Schedule (veto model)
Each slot is TWO Metricool posts in brand 7442919, autoPublish true, same time, same media:

| Slot | Instagram post | Facebook post |
| --- | --- | --- |
| 07:00 today's sky | `instagramData: {type: "REEL", showReelOnFeed: true}`, media = the Reel's raw MP4 URL, `videoCoverMilliseconds: 7500` | `facebookData: {type: "REEL"}`, same MP4, `videoCoverMilliseconds: 7500` |
| 18:00 pillar | `instagramData: {type: "POST"}`, media = the pillar PNG | `facebookData: {type: "POST"}`, same PNG |

Captions:
- Instagram caption ends with: "Your free chart: link in bio."
- Facebook caption ends with the tagged link (no shortener):
  `https://tideglyph.com/chart?utm_source=facebook&utm_medium=organic_social&utm_campaign=tideglyph_organic&utm_content=YYYY-MM-DD_sky` (07:00) or `..._pillar` (18:00). The "Don't know your birth time?" pillar links `/moon-sign-calculator` with the same tags.
- Leave `isAiGenerated` false: the cards and Reels are typographic designs, not AI imagery.

After scheduling, send Daniel the Metricool planner link and a one-line summary per day so he can edit or pull anything before it fires. Flag any line that could read as a prediction so his eye goes straight to it.

If the Metricool connector is NOT available in this session: still generate, build and push the media and get the raw URLs, then publish a review page listing every post with its media, caption, time and URL, and notify Daniel that the only remaining step is loading them into Metricool.

## Guardrails
- Never schedule to any brand but 7442919. Never touch BBD.
- Keep posting paced: two slots a day per network, never a burst.
- Instagram's bio link is set by Daniel by hand. It should be `https://tideglyph.com/chart?utm_source=instagram&utm_medium=organic_social&utm_campaign=tideglyph_organic&utm_content=bio`.
- Pinning is manual in the apps. Daniel pins three explainer posts (one in twelve, what the free chart shows, privacy) once they exist.
