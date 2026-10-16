#!/usr/bin/env python3
"""Render a Tideglyph social card to 1080x1350 PNG.
Usage: python3 make_card.py spec.json out.png
spec.json: {kind, eyebrow, tag, headline, journal, cta}  (tag/journal optional)
Fonts live in studio/fonts. Renders via node+playwright (render.mjs)."""
import sys, json, base64, pathlib, subprocess, os
HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "fonts"
def b64(p): return base64.b64encode((FONTS/p).read_bytes()).decode()
def faces():
    f = {"fr600":"fraunces-latin-600-normal.woff2","fr700":"fraunces-latin-700-normal.woff2",
         "nr400":"newsreader-latin-400-normal.woff2","nr500":"newsreader-latin-500-normal.woff2"}
    w=["Fraunces:600","Fraunces:700","Newsreader:400","Newsreader:500"]
    out=[]
    for (k,fn),spec in zip(f.items(),w):
        fam,wt=spec.split(":")
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url(data:font/woff2;base64,{b64(fn)}) format('woff2')}}")
    return "\n".join(out)
PAPER="#F3ECDD";INK="#241E1A";RUST="#A8432A";TIDE="#2E5B57";MUTED="#6C5F50";DISC="#F5EFE0"
def mark(sz,op=1.0):
    return (f'<svg width="{sz}" height="{sz}" viewBox="0 0 120 120" fill="none" style="opacity:{op}">'
      f'<defs><clipPath id="m{sz}"><circle cx="54" cy="44" r="23"/></clipPath></defs>'
      f'<circle cx="54" cy="44" r="23" fill="{INK}"/>'
      f'<circle cx="63" cy="40" r="20.5" fill="{DISC}" clip-path="url(#m{sz})"/>'
      f'<line x1="30" y1="80" x2="90" y2="80" stroke="{RUST}" stroke-width="5.4" stroke-linecap="round"/>'
      f'<path d="M33 95 q7 -7 14 0 t14 0 t14 0 t14 0" stroke="{TIDE}" stroke-width="4.6" fill="none" stroke-linecap="round"/></svg>')
def esc(s): 
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def html(spec):
    hl=spec["headline"]; n=len(hl)
    hs = 92 if n<=38 else 82 if n<=54 else 72 if n<=72 else 64
    tag = f'<div class="tag">{esc(spec.get("tag",""))}</div>' if spec.get("tag") else ""
    journal = f'<div class="journal">{esc(spec.get("journal",""))}</div>' if spec.get("journal") else ""
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
.c{{width:1080px;height:1350px;background:{PAPER};padding:100px 92px;display:flex;flex-direction:column;position:relative;overflow:hidden}}
.ghost{{position:absolute;right:-70px;top:-60px;opacity:0.06}}
.top{{display:flex;align-items:center;gap:16px;position:relative;z-index:2}}
.top .wm{{font-family:'Fraunces';font-weight:600;font-size:38px;color:{INK};letter-spacing:-1px}}
.top .wm .d{{color:{RUST}}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:27px;letter-spacing:3px;text-transform:uppercase;color:{RUST};margin-top:78px;position:relative;z-index:2}}
.tag{{font-family:'Newsreader';font-weight:500;font-size:25px;color:{TIDE};margin-top:14px;letter-spacing:1px;position:relative;z-index:2}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.08;color:{INK};margin-top:30px;letter-spacing:-1px;position:relative;z-index:2}}
.journal{{font-family:'Newsreader';font-weight:400;font-style:italic;font-size:38px;line-height:1.4;color:{MUTED};margin-top:40px;max-width:28ch;position:relative;z-index:2}}
.sp{{flex:1}}
.foot{{display:flex;align-items:center;gap:16px;position:relative;z-index:2}}
.foot .cta{{font-family:'Fraunces';font-weight:600;font-size:28px;color:{RUST}}}
</style></head><body>
<div class="c">
  <div class="ghost">{mark(460)}</div>
  <div class="top">{mark(50)}<div class="wm">Tideglyph<span class="d">.</span></div></div>
  <div class="eb">{esc(spec.get("eyebrow","Today's sky"))}</div>
  {tag}
  <div class="h">{esc(spec["headline"])}</div>
  {journal}
  <div class="sp"></div>
  <div class="foot">
    <svg width="60" height="20" viewBox="0 0 60 20" fill="none"><path d="M3 10 q6 -7 12 0 t12 0 t12 0 t12 0" stroke="{TIDE}" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
    <div class="cta">{esc(spec.get("cta","Your reading, from your chart. Free."))}</div>
  </div>
</div></body></html>"""
if __name__=="__main__":
    spec=json.load(open(sys.argv[1])); out=sys.argv[2]
    hp=HERE/"_card.html"; hp.write_text(html(spec))
    subprocess.run(["node", str(HERE/"render.mjs"), str(hp), out], check=True)
    print("wrote", out)
