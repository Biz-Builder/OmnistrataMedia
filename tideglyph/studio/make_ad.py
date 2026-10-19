#!/usr/bin/env python3
"""Render a Tideglyph static ad to 1080x1350 PNG from a photo plus a headline.
Usage: python3 make_ad.py photo.jpg "Headline, seven words or fewer" out.png [subline]
Reuses the brand mark, tokens and fonts from make_card so the CI matches the posts.
Photo is base64 embedded so it loads under file:// set_content, same as the fonts."""
import sys, base64, pathlib, subprocess
from make_card import faces, mark, PAPER, INK, RUST, TIDE, esc, HERE

def photo_b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def html(photo, headline, subline):
    n = len(headline)
    hs = 80 if n <= 30 else 72 if n <= 40 else 64 if n <= 50 else 58
    pb = photo_b64(photo)
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
.c{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#000}}
.photo{{position:absolute;inset:0;background-image:url(data:image/jpeg;base64,{pb});background-size:cover;background-position:center}}
.topscrim{{position:absolute;left:0;right:0;top:0;height:300px;background:linear-gradient(to bottom, rgba(36,30,26,0.55), rgba(36,30,26,0))}}
.botscrim{{position:absolute;left:0;right:0;bottom:0;height:760px;background:linear-gradient(to top, rgba(36,30,26,0.93) 8%, rgba(36,30,26,0.76) 36%, rgba(36,30,26,0))}}
.wm{{position:absolute;top:60px;left:72px;display:flex;align-items:center;gap:14px;z-index:3}}
.wm .t{{font-family:'Fraunces';font-weight:600;font-size:40px;color:{PAPER};letter-spacing:-1px;text-shadow:0 2px 12px rgba(0,0,0,0.45)}}
.wm .t .d{{color:{RUST}}}
.block{{position:absolute;left:72px;right:92px;bottom:96px;z-index:3}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.1;color:{PAPER};letter-spacing:-0.5px;text-shadow:0 2px 24px rgba(0,0,0,0.5);max-width:17ch}}
.sub{{font-family:'Newsreader';font-weight:500;font-size:34px;color:{PAPER};opacity:0.92;margin-top:24px;letter-spacing:0.3px;display:flex;align-items:center;gap:16px;text-shadow:0 2px 16px rgba(0,0,0,0.5)}}
.sub .wave{{flex:none}}
</style></head><body>
<div class="c">
  <div class="photo"></div>
  <div class="topscrim"></div>
  <div class="botscrim"></div>
  <div class="wm">{mark(46)}<div class="t">Tideglyph<span class="d">.</span></div></div>
  <div class="block">
    <div class="h">{esc(headline)}</div>
    <div class="sub"><svg class="wave" width="54" height="18" viewBox="0 0 60 20" fill="none"><path d="M3 10 q6 -7 12 0 t12 0 t12 0 t12 0" stroke="{TIDE}" stroke-width="4" fill="none" stroke-linecap="round"/></svg>{esc(subline)}</div>
  </div>
</div></body></html>"""

if __name__ == "__main__":
    photo = sys.argv[1]; headline = sys.argv[2]; out = sys.argv[3]
    subline = sys.argv[4] if len(sys.argv) > 4 else "Your free birth chart. No card."
    hp = HERE / "_ad.html"; hp.write_text(html(photo, headline, subline))
    subprocess.run(["node", str(HERE / "render.mjs"), str(hp), out], check=True)
    print("wrote", out)
