# Tideglyph social studio

The self-contained engine for Tideglyph's organic posts. A fresh cloud session uses this to generate, build and schedule a week of content. Everything here runs offline except the final Metricool scheduling.

## Fixed facts
- Metricool brand id (Tideglyph): 7442919. NEVER post to any other brand. BBD is separate.
- Media host: this repo, Biz-Builder/OmnistrataMedia (public). Cards go in tideglyph/todays-sky/ and tideglyph/pillars/. Raw URL pattern: https://raw.githubusercontent.com/Biz-Builder/OmnistrataMedia/main/<path>
- Timezone: Africa/Johannesburg (UTC+02:00). Daily slots: 07:00 (today's sky) and 18:00 (a pillar, US-facing).
- Networks: Facebook and Instagram now. Add TikTok once its account is connected in Metricool.

## Voice rules (every line)
- Reflection, never prediction. Name what the sky is doing, then invite noticing. No forecasts.
- No health, money or love claims. No medical or financial advice.
- Plain English that travels to the US and UK. No South African only references, no slang.
- No em dashes anywhere.
- Today's sky: one short headline line plus one journal question. Pillars: a hook plus two or three lines, ending on the free chart.

## Setup (once per run)
1. Clone this repo with push access and cd to tideglyph/studio.
2. `pip install pyswisseph --break-system-packages -q`. In the cloud workspace this often fails to build against the system setuptools with an `install_layout` AttributeError. If it does, build it in a fresh venv: `python3 -m venv /tmp/skyenv && /tmp/skyenv/bin/pip install -U pip setuptools wheel -q && /tmp/skyenv/bin/pip install pyswisseph -q`, then run the sky step with that venv (`/tmp/skyenv/bin/python todays_sky.py YYYY-MM-DD`). Only todays_sky.py needs it; make_card.py and render.mjs use the system python and node.
3. `npm install playwright` in studio (chromium is preinstalled; do not run `playwright install`).

## Weekly batch (the Monday task)
For each of the next 7 days:
1. `python3 todays_sky.py YYYY-MM-DD` -> JSON with the day's headline transit.
2. Write the today's sky copy from that transit, under the voice rules. Fact is the transit_label; the words are yours.
3. Write that day's 18:00 pillar post, rotating through: whole chart differentiator, privacy, the journal/record, a plain explainer (rising, moon, big three, Saturn return), sign spotlight. One pillar per day, do not repeat within the week.
4. Build the card for each: write a spec.json {eyebrow,tag,headline,journal,cta} and run `python3 make_card.py spec.json out.png`. Today's sky uses the tag (transit_label) and a journal line. Pillars omit the tag, use headline + a short sub as journal, cta to the free chart.
5. Save cards to tideglyph/todays-sky/YYYY-MM-DD.png and tideglyph/pillars/YYYY-MM-DD.png. Commit and push. Confirm one raw URL loads.

## Schedule (veto model)
- Schedule each post to Metricool brand 7442919, providers facebook and instagram, autoPublish true, at 07:00 (today's sky) and 18:00 (pillar) SAST, using the card's raw URL as media and the caption you wrote.
- This is the veto model: posts publish automatically. After scheduling, send Daniel the Metricool planner link and a one-line summary per day so he can edit or pull anything before it fires. Flag any line that could read as a prediction so his eye goes straight to it.
- If the Metricool connector is NOT available in this session: still generate, build, push the cards and get the raw URLs, then publish a review page listing every post with its card, caption, time and raw URL, and notify Daniel that the only remaining step is loading them into Metricool.

## Guardrails
- Never schedule to any brand but 7442919. Never touch BBD.
- Instagram and the accounts are freshly out of a Meta review; keep posting paced (the two fixed daily slots are fine) and never burst many posts close together.
- When Alex's general-sky endpoint is live (see the endpoint spec in the OmniStrata project), call it for the today's sky reading instead of writing the line here, so the social voice matches the product exactly. The card and schedule steps are unchanged.
