#!/usr/bin/env python3
"""Render a Tideglyph birth chart card: a chart wheel, the Sun and Moon large,
the five other planets small. Used for the pinned explainer post (labelled as
an example) and as the mock for the shareable result card.
Usage: python3 make_chart_card.py spec.json out.png
spec.json: {
  "size": "post" | "story",          # 1080x1350 or 1080x1920
  "eyebrow": "An example chart",     # optional
  "headline": "The sky at my first breath",
  "birth": [1994, 3, 14, 10.0],      # UT year, month, day, hour: computes the signs
  "rarity": "1 in 12 share my Sun sign ...",  # optional line under the big two
  "cta": "tideglyph.com/chart"
}
Positions come from the Swiss Ephemeris (pyswisseph), tropical zodiac, so the
example is a real sky, never made up."""
import sys, json, math, base64, pathlib, subprocess
import swisseph as swe
from make_card import faces, mark, PAPER, INK, RUST, TIDE, MUTED, esc, HERE

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_GLYPH = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
BODIES = [("Sun","☉",swe.SUN),("Moon","☽",swe.MOON),("Mercury","☿",swe.MERCURY),
          ("Venus","♀",swe.VENUS),("Mars","♂",swe.MARS),("Jupiter","♃",swe.JUPITER),("Saturn","♄",swe.SATURN)]
VS = "︎"  # text presentation, never emoji
GLYPH_FONT = pathlib.Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

def positions(y, m, d, h):
    jd = swe.julday(y, m, d, h)
    return [(n, g, swe.calc_ut(jd, p)[0][0]) for n, g, p in BODIES]

def glyph_face():
    if not GLYPH_FONT.exists():
        return ""
    b = base64.b64encode(GLYPH_FONT.read_bytes()).decode()
    return f"@font-face{{font-family:'Glyphs';src:url(data:font/ttf;base64,{b}) format('truetype')}}"

def wheel(pos, R):
    """SVG wheel. Aries starts at 9 o'clock and signs run anticlockwise, as on a chart."""
    c = R + 10; size = 2 * c
    def pt(lon, r):
        a = math.radians(180 - lon)  # 0 deg Aries at the left, anticlockwise
        return c + r * math.cos(a), c - r * math.sin(a)
    out = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    out.append(f'<circle cx="{c}" cy="{c}" r="{R}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<circle cx="{c}" cy="{c}" r="{R*0.78}" fill="none" stroke="{INK}" stroke-opacity="0.35" stroke-width="1.5"/>')
    out.append(f'<circle cx="{c}" cy="{c}" r="{R*0.30}" fill="none" stroke="{TIDE}" stroke-opacity="0.5" stroke-width="1.5"/>')
    for i in range(12):
        x1, y1 = pt(i * 30, R * 0.78); x2, y2 = pt(i * 30, R)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-opacity="0.35" stroke-width="1.5"/>')
        gx, gy = pt(i * 30 + 15, R * 0.89)
        out.append(f'<text x="{gx:.1f}" y="{gy:.1f}" font-family="Glyphs" font-size="{R*0.12:.0f}" fill="{MUTED}" text-anchor="middle" dominant-baseline="central">{SIGN_GLYPH[i]}{VS}</text>')
    # planets: nudge apart when they sit close together so glyphs never overlap
    placed = []
    for n, g, lon in sorted(pos, key=lambda p: p[2]):
        r = R * 0.62
        for plon, pr in placed:
            if abs((lon - plon + 180) % 360 - 180) < 14 and abs(pr - r) < 1:
                r -= R * 0.17
        placed.append((lon, r))
        big = n in ("Sun", "Moon")
        col = RUST if big else INK
        tx, ty = pt(lon, R * 0.78)
        px, py = pt(lon, r)
        out.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{col}" stroke-opacity="0.4" stroke-width="1.5"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{R*(0.085 if big else 0.07):.1f}" fill="{PAPER}" stroke="{col}" stroke-width="{2.5 if big else 1.5}"/>')
        out.append(f'<text x="{px:.1f}" y="{py:.1f}" font-family="Glyphs" font-size="{R*(0.10 if big else 0.08):.0f}" fill="{col}" text-anchor="middle" dominant-baseline="central">{g}{VS}</text>')
    out.append("</svg>")
    return "\n".join(out)

def html(spec):
    story = spec.get("size") == "story"
    W, H = 1080, (1920 if story else 1350)
    pos = positions(*spec["birth"])
    sign = {n: SIGNS[int(l // 30)] for n, _, l in pos}
    glyph = {n: g for n, g, _ in pos}
    R = 330 if story else 270
    others = "".join(
        f'<div class="o"><span class="g">{glyph[n]}{VS}</span>{n} in <b>{sign[n]}</b></div>'
        for n in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"))
    eb = f'<div class="eb">{esc(spec["eyebrow"])}</div>' if spec.get("eyebrow") else ""
    rar = f'<div class="rar">{esc(spec["rarity"])}</div>' if spec.get("rarity") else ""
    pad = "250px 96px 420px" if story else "84px 92px 76px"
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
{glyph_face()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER}}}
.c{{width:{W}px;height:{H}px;background:{PAPER};padding:{pad};display:flex;flex-direction:column;align-items:center;text-align:center}}
.top{{display:flex;align-items:center;gap:14px;align-self:flex-start}}
.top .wm{{font-family:'Fraunces';font-weight:600;font-size:36px;color:{INK};letter-spacing:-1px}}
.top .wm .d{{color:{RUST}}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{RUST};margin-top:{40 if story else 26}px}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{64 if story else 54}px;line-height:1.05;color:{INK};letter-spacing:-1px;margin-top:14px}}
.wheel{{margin-top:{40 if story else 22}px}}
.big{{font-family:'Fraunces';font-weight:600;font-size:{60 if story else 50}px;color:{INK};margin-top:{36 if story else 18}px;letter-spacing:-0.5px}}
.big b{{color:{RUST};font-weight:600}}
.big .dot{{color:{TIDE};padding:0 14px}}
.rar{{font-family:'Newsreader';font-style:italic;font-size:{34 if story else 30}px;color:{MUTED};margin-top:12px}}
.others{{display:grid;grid-template-columns:1fr 1fr;gap:6px 40px;margin-top:{40 if story else 22}px;text-align:left}}
.o{{font-family:'Newsreader';font-weight:500;font-size:{32 if story else 28}px;color:{INK}}}
.o b{{color:{RUST};font-weight:500}}
.o .g{{font-family:'Glyphs';color:{MUTED};display:inline-block;width:42px}}
.sp{{flex:1}}
.foot{{font-family:'Fraunces';font-weight:600;font-size:{32 if story else 28}px;color:{RUST};display:flex;align-items:center;gap:16px}}
</style></head><body><div class="c">
<div class="top">{mark(44)}<div class="wm">Tideglyph<span class="d">.</span></div></div>
{eb}
<div class="h">{esc(spec.get("headline","The sky at my first breath"))}</div>
<div class="wheel">{wheel(pos, R)}</div>
<div class="big">{sign['Sun']} <b>Sun</b><span class="dot">&middot;</span>{sign['Moon']} <b>Moon</b></div>
{rar}
<div class="others">{others}</div>
<div class="sp"></div>
<div class="foot"><svg width="60" height="20" viewBox="0 0 60 20" fill="none"><path d="M3 10 q6 -7 12 0 t12 0 t12 0 t12 0" stroke="{TIDE}" stroke-width="4" fill="none" stroke-linecap="round"/></svg>{esc(spec.get("cta","tideglyph.com/chart"))}</div>
</div></body></html>""", W, H

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text()); out = sys.argv[2]
    page, W, H = html(spec)
    hp = HERE / "_chart.html"; hp.write_text(page)
    subprocess.run(["node", str(HERE / "render_size.mjs"), str(hp), out, str(W), str(H)], check=True)
    print("wrote", out)
