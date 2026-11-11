"""Email banner for each reservation reminder tip.

Usage: python3 render_tip.py tips.json outdir
tips.json maps a key to {"photo", "n", "of", "head", "pos" (optional), "full" (optional bool)}.
Output: 1200x600 JPEG per key, for a 600px wide email column at 2x.
"""
import sys, os, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from playwright.sync_api import sync_playwright

CSS = R.CSS + '''
.tbn{width:1200px;height:600px;background:#121110;color:#f5f3ee;position:relative;overflow:hidden;font-family:A}
.tbn .ph{position:absolute;top:0;right:0;bottom:0;width:760px;background-size:cover}
.tbn .ph:after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,#121110 0%,rgba(18,17,16,.85) 18%,rgba(18,17,16,0) 55%)}
.tbn .tx{position:absolute;left:64px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center}
.tbn .wm2{position:absolute;left:64px;top:48px;display:flex;align-items:center;gap:12px;font-family:B;font-weight:700;font-size:30px}
.tbn .wm2 b{color:#FFB000}
.tbn .tipk{font-family:A;font-weight:700;font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:#FFB000;margin-bottom:22px}
.tbn .tiph{font-family:B;font-weight:800;font-size:72px;line-height:1.02;letter-spacing:-.02em;text-wrap:balance;margin:0}
.tbn .tiph em{font-style:normal;color:#FFB000}
.tbn .fullb{display:inline-block;margin-top:28px;background:#FFB000;color:#121110;font-weight:700;font-size:22px;padding:8px 18px;border-radius:999px}
'''

def head(s):
    import re
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)

def banner(t, photo):
    full = '<div><span class="fullb">On Full</span></div>' if t.get("full") else ''
    return f'''<div class="tbn"><div class="ph" style="background-image:url(data:image/jpeg;base64,{photo});background-position:{t.get("pos","center 40%")}"></div>
<div class="wm2">{R.GLYPH.format(s=34)}<span>Table<b>Pics</b></span></div>
<div class="tx"><div class="tipk">Tip {t["n"]} of {t["of"]}</div><h1 class="tiph">{head(t["head"])}</h1>{full}</div></div>'''

tips = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 600})
    for k, t in tips.items():
        ph = base64.b64encode(open(t["photo"], "rb").read()).decode()
        pg.set_content(f'<html><head><style>{CSS}</style></head><body style="margin:0">{banner(t, ph)}</body></html>')
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
        pg.screenshot(path=f"{out}/{k}.jpg", type="jpeg", quality=80)
    b.close()
