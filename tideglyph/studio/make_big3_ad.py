#!/usr/bin/env python3
"""Render a Tideglyph "big three" ad: paper background, one hook, the result card
from tideglyph.com/chart as an inset (labelled Example), and the one promise.
Matches the live chart page so the ad and the page look the same.
Usage: python3 make_big3_ad.py spec.json out.png
spec.json: {
  "size": "feed" | "story",            # 1080x1350 or 1080x1920
  "hook": "1 in 12 people share your Sun sign.",
  "sub": "Far fewer share your big three.",   # optional
  "signs": ["Taurus", "Cancer", "Gemini"],    # Sun, Moon, rising (example only)
  "cta": "Find your big three, free"
}"""
import sys, json, pathlib, subprocess
from make_card import faces, mark, esc, PAPER, INK, RUST, TIDE, MUTED, HERE
from make_chart_card import glyph_face, VS

LINES = {
    "Sun": "how you meet the day and what lights you up",
    "Moon": "what you need to feel safe and at home",
    "Rising": "the first impression you give",
}

def html(spec):
    story = spec.get("size") == "story"
    W, H = 1080, (1920 if story else 1350)
    sun, moon, rising = spec["signs"]
    hook = spec["hook"]; n = len(hook)
    hs = (96 if n <= 34 else 86 if n <= 48 else 76) if story else (84 if n <= 34 else 76 if n <= 48 else 68)
    sub = f'<div class="sub">{esc(spec["sub"])}</div>' if spec.get("sub") else ""
    # story keeps text inside the safe zone (clear of top bar and bottom caption)
    pad = "250px 90px 380px" if story else "90px 84px 84px"
    rows = "".join(
        f'<div class="row"><div class="g">{g}{VS if g != "AC" else ""}</div><div class="t"><div class="lab">{lab}</div>'
        f'<div class="sg">{esc(sg)}</div><div class="ln">{LINES[key]}</div></div></div>'
        for g, lab, key, sg in (("☉", "Sun", "Sun", sun), ("☽", "Moon", "Moon", moon), ("AC", "Rising sign", "Rising", rising)))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
{glyph_face()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER}}}
.c{{width:{W}px;height:{H}px;background:{PAPER};padding:{pad};display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:14px}}
.wm{{font-family:'Fraunces';font-weight:600;font-size:40px;color:{INK};letter-spacing:-1px}}
.wm .d{{color:{RUST}}}
.hook{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.04;color:{INK};letter-spacing:-1.5px;margin-top:{56 if story else 44}px}}
.sub{{font-family:'Newsreader';font-style:italic;font-size:{44 if story else 40}px;color:{MUTED};margin-top:18px}}
.card{{margin-top:{60 if story else 40}px;background:#FBF7EE;border:2px solid #D9CDB6;border-radius:28px;padding:{40 if story else 32}px 40px 30px;box-shadow:0 18px 40px rgba(36,30,26,.10)}}
.ex{{font-family:'Newsreader';font-weight:500;font-size:22px;letter-spacing:4px;text-transform:uppercase;color:{MUTED};margin-bottom:10px}}
.row{{display:flex;gap:26px;align-items:flex-start;padding:{18 if story else 14}px 0;border-top:1px solid #E4D8C2}}
.row:first-of-type{{border-top:none}}
.g{{font-family:'Glyphs','Newsreader';font-size:40px;color:{RUST};width:56px;text-align:center;padding-top:6px}}
.lab{{font-family:'Newsreader';font-weight:500;font-size:22px;letter-spacing:3px;text-transform:uppercase;color:{MUTED}}}
.sg{{font-family:'Fraunces';font-weight:600;font-size:{62 if story else 54}px;line-height:1.05;color:{RUST}}}
.ln{{font-family:'Newsreader';font-size:26px;color:{INK};opacity:.8;margin-top:2px}}
.sp{{flex:1}}
.foot{{display:flex;align-items:center;justify-content:space-between}}
.btn{{background:{RUST};color:#F7EFE6;font-family:'Fraunces';font-weight:600;font-size:{40 if story else 36}px;padding:22px 38px;border-radius:16px}}
.url{{font-family:'Newsreader';font-weight:500;font-size:28px;color:{TIDE}}}
</style></head><body><div class="c">
<div class="top">{mark(52)}<div class="wm">Tideglyph<span class="d">.</span></div></div>
<div class="hook">{esc(hook)}</div>
{sub}
<div class="card"><div class="ex">Example</div>{rows}</div>
<div class="sp"></div>
<div class="foot"><div class="btn">{esc(spec.get("cta","Find your big three, free"))}</div><div class="url">tideglyph.com/chart</div></div>
</div></body></html>""", W, H

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text()); out = sys.argv[2]
    page, W, H = html(spec)
    hp = HERE / "_big3.html"; hp.write_text(page)
    subprocess.run(["node", str(HERE / "render_size.mjs"), str(hp), out, str(W), str(H)], check=True)
    print("wrote", out)
