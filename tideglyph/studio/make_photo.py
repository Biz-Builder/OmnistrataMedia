#!/usr/bin/env python3
"""Tideglyph photo-led visuals (from 12 Nov 2026). One look for ads, pillar posts
and today's sky Reels: a real photo up top, the words over it, and the product
(the big three result card or the one promise) on paper underneath, so every
post looks like tideglyph.com/chart and says the same thing.

Usage:
  python3 make_photo.py spec.json out.png            # static (feed 1080x1350 or story 1080x1920)
  python3 make_photo.py spec.json out.mp4 --reel     # animated 1080x1920 Reel with the music bed

spec.json:
{
  "layout": "ad" | "pillar" | "sky",
  "size": "feed" | "story",                 # sky is always story
  "photo": "sky-moon-water.jpg",            # file in tideglyph/photos
  "eyebrow": "Today's sky . 12 November",   # optional
  "tag": "Moon in Sagittarius",             # optional, sky only
  "hook": "1 in 12 people share your Sun sign.",
  "sub": "Far fewer share your big three.", # optional (sky: the journal question)
  "signs": ["Taurus", "Cancer", "Gemini"],  # ad: example card (Sun, Moon, rising)
  "cta": "Find your big three, free",
  "focus": "50% 40%"                        # optional photo position
}
Photos are base64 embedded so they load under file://."""
import sys, json, base64, pathlib, subprocess, tempfile, shutil
from make_card import faces, mark, esc, PAPER, INK, RUST, TIDE, MUTED, HERE
from make_chart_card import glyph_face, VS

PHOTOS = HERE.parent / "photos"
LIGHT = "#F6EFE2"
SAND = "#E9C9A0"
LINES = {"Sun": "how you meet the day and what lights you up",
         "Moon": "what you need to feel safe and at home",
         "Rising": "the first impression you give"}
FPS, REEL_SECONDS = 30, 9


def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def card_rows(signs, big):
    sun, moon, rising = signs
    return "".join(
        f'<section class="row"><div class="g">{g}{VS if g != "AC" else ""}</div><div>'
        f'<div class="lab">{lab}</div><div class="sg">{esc(sg)}</div><div class="ln">{LINES[k]}</div></div></section>'
        for g, lab, k, sg in (("☉", "Sun", "Sun", sun), ("☽", "Moon", "Moon", moon), ("AC", "Rising sign", "Rising", rising)))


def promise_strip():
    # the three things /chart shows, as a quiet row of glyphs: the product in one glance
    return ('<div class="strip">'
            f'<span><b class="gl">☉{VS}</b>Sun</span><span><b class="gl">☽{VS}</b>Moon</span>'
            '<span><b class="gl ac">AC</b>Rising</span><span class="plus">+ five planets</span></div>')


def html(spec, reel=False):
    layout = spec.get("layout", "ad")
    story = reel or layout == "sky" or spec.get("size") == "story"
    W, H = 1080, (1920 if story else 1350)
    photo = PHOTOS / spec["photo"]
    focus = spec.get("focus", "50% 40%")
    hook = spec["hook"]; n = len(hook)
    cta = esc(spec.get("cta", "Find your big three, free"))
    eyebrow = f'<div class="eb a" style="--d:.2s">{esc(spec["eyebrow"])}</div>' if spec.get("eyebrow") else ""
    tag = f'<div class="tag a" style="--d:.5s">{esc(spec["tag"])}</div>' if spec.get("tag") else ""
    sub = f'<div class="sub a" style="--d:1.6s">{esc(spec["sub"])}</div>' if spec.get("sub") else ""
    anim = reel

    if layout == "sky":
        # full-bleed sky, words low in the frame, the promise as a pill at the end
        hs = 96 if n <= 34 else 86 if n <= 50 else 76 if n <= 70 else 68
        body = f"""
<div class="photo full"></div><div class="scrim full"></div>
<div class="safe">
  <div class="top a" style="--d:0s">{mark(56)}<div class="wm light">Tideglyph<span class="d">.</span></div></div>
  <div class="spx"></div>
  {eyebrow}{tag}
  <div class="h light a" style="--d:.9s;font-size:{hs}px">{esc(hook)}</div>
  {sub.replace('class="sub', 'class="sub light')}
  <div class="pillrow a" style="--d:3.6s"><div class="pill">{cta}</div><div class="url light">tideglyph.com/chart</div></div>
</div>"""
        photo_h = H
    else:
        # split: photo on top with the hook over it, paper below with the product
        photo_h = (820 if story else 700) if layout == "ad" else (1040 if story else 760)
        hs = (92 if n <= 34 else 82 if n <= 50 else 72) if story else (80 if n <= 34 else 70 if n <= 50 else 62)
        if layout == "ad":
            product = f'<div class="card a" style="--d:2.0s"><div class="ex">Example</div>{card_rows(spec["signs"], story)}</div>'
        else:
            product = (f'<div class="psub a" style="--d:1.6s">{esc(spec.get("sub", ""))}</div>' if spec.get("sub") else "") + \
                      f'<div class="a" style="--d:2.2s">{promise_strip()}</div>'
        sub_on_photo = sub if layout == "ad" else ""
        pad_top = 250 if story else 76
        body = f"""
<div class="photo split"></div><div class="scrim split"></div>
<div class="over" style="height:{photo_h}px;padding:{pad_top}px {170 if story else 84}px 0 {84}px">
  <div class="top a" style="--d:0s">{mark(52)}<div class="wm light">Tideglyph<span class="d">.</span></div></div>
  <div class="spx"></div>
  {eyebrow}
  <div class="h light a" style="--d:.6s;font-size:{hs}px">{esc(hook)}</div>
  {sub_on_photo.replace('class="sub', 'class="sub light')}
</div>
<div class="paper" style="top:{photo_h - 4}px;padding:{0 if layout == 'ad' else 46}px {170 if story else 84}px {420 if story else 76}px 84px">
  {product}
  <div class="spx"></div>
  <div class="foot a" style="--d:{4.0 if layout == 'ad' else 3.0}s"><div class="pill">{cta}</div><div class="url">tideglyph.com/chart</div></div>
</div>"""

    kb = "animation:kb 9s linear both;" if anim else ""
    hide = "opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) var(--d) both;" if anim else ""
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
{glyph_face()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER}}}
.c{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:{PAPER}}}
.photo{{position:absolute;left:0;right:0;top:0;background:url(data:image/jpeg;base64,{b64(photo)}) center/cover;background-position:{focus};{kb}}}
.photo.full{{height:{H}px}} .photo.split{{height:{photo_h}px}}
@keyframes kb{{from{{transform:scale(1.04)}}to{{transform:scale(1.14) translateY(-18px)}}}}
.scrim{{position:absolute;left:0;right:0;top:0}}
.scrim.full{{height:{H}px;background:linear-gradient(180deg,rgba(14,12,20,.45) 0%,rgba(14,12,20,0) 26%,rgba(14,12,20,.15) 45%,rgba(14,12,20,.78) 72%,rgba(14,12,20,.9) 100%)}}
.scrim.split{{height:{photo_h}px;background:linear-gradient(180deg,rgba(14,12,20,.55) 0%,rgba(14,12,20,.05) 30%,rgba(14,12,20,.35) 62%,rgba(14,12,20,.82) 100%)}}
.safe{{position:absolute;left:96px;right:170px;top:250px;bottom:420px;display:flex;flex-direction:column}}
.over{{position:absolute;left:0;right:0;top:0;display:flex;flex-direction:column;padding-bottom:44px!important}}
.paper{{position:absolute;left:0;right:0;bottom:0;background:{PAPER};display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:14px}}
.wm{{font-family:'Fraunces';font-weight:600;font-size:40px;letter-spacing:-1px;color:{INK}}}
.wm.light{{color:{LIGHT}}} .wm .d{{color:{RUST}}}
.top svg circle:first-of-type{{fill:{LIGHT}}} .top svg circle[clip-path]{{fill:#2a2430}}
.spx{{flex:1}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:28px;letter-spacing:4px;text-transform:uppercase;color:{SAND}}}
.tag{{font-family:'Newsreader';font-weight:500;font-size:32px;color:{LIGHT};opacity:.85;margin-top:12px}}
.h{{font-family:'Fraunces';font-weight:600;line-height:1.04;letter-spacing:-1.5px;margin-top:16px;text-wrap:balance}}
.h.light{{color:{LIGHT};text-shadow:0 2px 24px rgba(0,0,0,.35)}}
.sub{{font-family:'Newsreader';font-style:italic;font-size:{44 if story else 38}px;line-height:1.3;margin-top:22px}}
.sub.light{{color:{LIGHT};opacity:.9}}
.psub{{font-family:'Newsreader';font-size:{40 if story else 34}px;line-height:1.38;color:{INK};max-width:36ch}}
.card{{margin-top:-46px;background:#FBF7EE;border:2px solid #D9CDB6;border-radius:28px;padding:{30 if story else 24}px 38px {22 if story else 16}px;box-shadow:0 22px 50px rgba(36,30,26,.18);position:relative;z-index:3}}
.ex{{font-family:'Newsreader';font-weight:500;font-size:21px;letter-spacing:4px;text-transform:uppercase;color:{MUTED};margin-bottom:6px}}
.row{{display:flex;gap:24px;align-items:flex-start;padding:{16 if story else 12}px 0;border-top:1px solid #E4D8C2}}
.card .row:first-of-type{{border-top:none}}
.g{{font-family:'Glyphs','Newsreader';font-size:{40 if story else 34}px;color:{RUST};width:54px;text-align:center;padding-top:4px}}
.lab{{font-family:'Newsreader';font-weight:500;font-size:20px;letter-spacing:3px;text-transform:uppercase;color:{MUTED}}}
.sg{{font-family:'Fraunces';font-weight:600;font-size:{58 if story else 48}px;line-height:1.02;color:{RUST}}}
.ln{{font-family:'Newsreader';font-size:{26 if story else 23}px;color:{INK};opacity:.8}}
.strip{{display:flex;flex-wrap:wrap;align-items:center;gap:14px 30px;margin-top:30px;font-family:'Newsreader';font-weight:500;font-size:{34 if story else 30}px;color:{INK}}}
.strip .gl{{font-family:'Glyphs','Newsreader';font-weight:400;color:{RUST};margin-right:10px}}
.strip .gl.ac{{font-family:'Newsreader';font-weight:500}}
.strip .plus{{color:{MUTED};font-style:italic}}
.foot,.pillrow{{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}}
.pillrow{{margin-top:44px;justify-content:flex-start;gap:26px}}
.pill{{background:{RUST};color:#F7EFE6;font-family:'Fraunces';font-weight:600;font-size:{42 if story else 36}px;padding:22px 38px;border-radius:16px;box-shadow:0 10px 26px rgba(120,40,20,.25)}}
.url{{font-family:'Newsreader';font-weight:500;font-size:{32 if story else 28}px;color:{TIDE}}}
.url.light{{color:{LIGHT}}}
.a{{{hide}}}
@keyframes rise{{from{{opacity:0;transform:translateY(30px)}}to{{opacity:1;transform:none}}}}
</style></head><body><div class="c">{body}</div></body></html>""", W, H


def render_still(spec, out):
    page, W, H = html(spec)
    hp = HERE / "_photo.html"; hp.write_text(page)
    subprocess.run(["node", str(HERE / "render_size.mjs"), str(hp), str(out), str(W), str(H)], check=True)


def render_reel(spec, out):
    from make_reel import ffmpeg_bin
    page, W, H = html(spec, reel=True)
    hp = HERE / "_photo_reel.html"; hp.write_text(page)
    frames = pathlib.Path(tempfile.mkdtemp(prefix="photo_reel_"))
    subprocess.run(["node", str(HERE / "render_reel.mjs"), str(hp), str(frames), str(FPS), str(REEL_SECONDS)], check=True)
    bed = HERE / "audio" / "tideglyph-bed.m4a"
    start = sum(map(ord, spec["hook"])) % 48
    S = REEL_SECONDS
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-ss", str(start), "-i", str(bed), "-filter_complex",
                    f"[1:a]atrim=0:{S},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.4,afade=t=out:st={S - 1.2}:d=1.2,volume=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(frames, ignore_errors=True)


if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve()
    if "--reel" in sys.argv:
        render_reel(spec, out)
    else:
        render_still(spec, out)
    print("wrote", out)
