#!/usr/bin/env python3
"""Render a Tideglyph photo-backed card to 1080x1350 PNG.
Usage: python3 make_card_photo.py spec.json photo.jpg out.png
spec.json: {eyebrow, tag, headline, journal, cta}  (tag/journal optional)
Photo fills the frame under a dark scrim; brand mark, fonts and tokens come
from make_card so it matches the typographic cards. Photo and fonts are
base64 embedded so they load under file:// set_content."""
import sys, json, base64, pathlib, subprocess
from make_card import faces, mark, PAPER, INK, RUST, TIDE, esc, HERE

SAND = "#E7C9A6"    # warm light eyebrow/cta over dark scrim
LIGHT = "#F3ECDD"   # paper, for headline and sub over photo

def photo_b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def html(spec, photo):
    hl = spec["headline"]; n = len(hl)
    hs = 84 if n <= 26 else 74 if n <= 34 else 66 if n <= 46 else 58
    pb = photo_b64(photo)
    eyebrow = esc(spec.get("eyebrow", ""))
    tag = f'<div class="tag">{esc(spec.get("tag",""))}</div>' if spec.get("tag") else ""
    sub = f'<div class="sub">{esc(spec.get("journal",""))}</div>' if spec.get("journal") else ""
    cta = esc(spec.get("cta", "Your free chart: tideglyph.com/chart"))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
.c{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#000}}
.photo{{position:absolute;inset:0;background-image:url(data:image/jpeg;base64,{pb});background-size:cover;background-position:center}}
.topscrim{{position:absolute;left:0;right:0;top:0;height:320px;background:linear-gradient(to bottom, rgba(26,22,19,0.6), rgba(26,22,19,0))}}
.botscrim{{position:absolute;left:0;right:0;bottom:0;height:900px;background:linear-gradient(to top, rgba(26,22,19,0.95) 10%, rgba(26,22,19,0.8) 42%, rgba(26,22,19,0))}}
.wm{{position:absolute;top:62px;left:76px;display:flex;align-items:center;gap:14px;z-index:3}}
.wm .t{{font-family:'Fraunces';font-weight:600;font-size:40px;color:{LIGHT};letter-spacing:-1px;text-shadow:0 2px 14px rgba(0,0,0,0.5)}}
.wm .t .d{{color:{SAND}}}
.block{{position:absolute;left:76px;right:88px;bottom:92px;z-index:3}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:26px;letter-spacing:3px;text-transform:uppercase;color:{SAND};text-shadow:0 2px 14px rgba(0,0,0,0.6)}}
.tag{{font-family:'Newsreader';font-weight:500;font-size:25px;color:{LIGHT};opacity:0.88;margin-top:10px;letter-spacing:1px;text-shadow:0 2px 14px rgba(0,0,0,0.6)}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.08;color:{LIGHT};margin-top:18px;letter-spacing:-0.5px;max-width:19ch;text-shadow:0 2px 24px rgba(0,0,0,0.55)}}
.sub{{font-family:'Newsreader';font-weight:400;font-size:33px;line-height:1.38;color:{LIGHT};opacity:0.94;margin-top:22px;max-width:28ch;text-shadow:0 2px 18px rgba(0,0,0,0.6)}}
.foot{{display:flex;align-items:center;gap:16px;margin-top:34px}}
.foot .cta{{font-family:'Fraunces';font-weight:600;font-size:28px;color:{SAND};text-shadow:0 2px 16px rgba(0,0,0,0.6)}}
</style></head><body>
<div class="c">
  <div class="photo"></div>
  <div class="topscrim"></div>
  <div class="botscrim"></div>
  <div class="wm">{mark(46)}<div class="t">Tideglyph<span class="d">.</span></div></div>
  <div class="block">
    <div class="eb">{eyebrow}</div>
    {tag}
    <div class="h">{esc(hl)}</div>
    {sub}
    <div class="foot">
      <svg width="56" height="18" viewBox="0 0 60 20" fill="none"><path d="M3 10 q6 -7 12 0 t12 0 t12 0 t12 0" stroke="{TIDE}" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
      <div class="cta">{cta}</div>
    </div>
  </div>
</div></body></html>"""

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); photo = sys.argv[2]; out = sys.argv[3]
    hp = HERE / "_card.html"; hp.write_text(html(spec, photo))
    subprocess.run(["node", str(HERE / "render.mjs"), str(hp), out], check=True)
    print("wrote", out)
