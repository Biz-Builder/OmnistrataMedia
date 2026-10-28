#!/usr/bin/env python3
"""Render a Tideglyph photo-backed 'today's sky' Reel: 1080x1920 vertical MP4, ~8s, silent.
Usage: python3 make_reel_photo.py spec.json photo.jpg out.mp4
spec.json: {eyebrow, tag, headline, journal, cta}  (same fields as make_card).
Photo fills the frame under a dark scrim; brand mark, fonts and tokens come from
make_card, and the frame/encode pipeline (render_reel.mjs + ffmpeg) from make_reel."""
import sys, json, base64, pathlib, subprocess, tempfile, shutil
from make_card import faces, mark, esc, HERE
from make_reel import FPS, SECONDS, ffmpeg_bin

SAND = "#E7C9A6"
LIGHT = "#F3ECDD"
TIDE = "#2E5B57"

def photo_b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def html(spec, photo):
    hl = spec["headline"]; n = len(hl)
    hs = 92 if n <= 26 else 82 if n <= 34 else 74 if n <= 46 else 66
    pb = photo_b64(photo)
    tag = f'<div class="tag a" style="--d:.5s">{esc(spec.get("tag",""))}</div>' if spec.get("tag") else ""
    journal = f'<div class="journal a" style="--d:2.4s">{esc(spec.get("journal",""))}</div>' if spec.get("journal") else ""
    cta = esc(spec.get("cta", "Your free chart: tideglyph.com/chart"))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
.c{{width:1080px;height:1920px;position:relative;overflow:hidden;background:#000}}
.photo{{position:absolute;inset:0;background-image:url(data:image/jpeg;base64,{pb});background-size:cover;background-position:center;animation:zoom {SECONDS}s ease-out both}}
@keyframes zoom{{from{{transform:scale(1.0)}}to{{transform:scale(1.07)}}}}
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom, rgba(26,22,19,0.62) 0%, rgba(26,22,19,0.32) 34%, rgba(26,22,19,0.5) 66%, rgba(26,22,19,0.82) 100%)}}
.safe{{position:absolute;left:96px;right:150px;top:250px;bottom:360px;display:flex;flex-direction:column;z-index:2}}
.a{{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) var(--d) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(34px)}}to{{opacity:1;transform:translateY(0)}}}}
.top{{display:flex;align-items:center;gap:16px}}
.top .wm{{font-family:'Fraunces';font-weight:600;font-size:44px;color:{LIGHT};letter-spacing:-1px;text-shadow:0 2px 16px rgba(0,0,0,0.55)}}
.top .wm .d{{color:{SAND}}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:30px;letter-spacing:3px;text-transform:uppercase;color:{SAND};text-shadow:0 2px 16px rgba(0,0,0,0.6)}}
.tag{{font-family:'Newsreader';font-weight:500;font-size:30px;color:{LIGHT};opacity:0.9;margin-top:16px;letter-spacing:1px;text-shadow:0 2px 16px rgba(0,0,0,0.6)}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.08;color:{LIGHT};margin-top:40px;letter-spacing:-1px;text-shadow:0 3px 28px rgba(0,0,0,0.6)}}
.journal{{font-family:'Newsreader';font-weight:400;font-size:44px;line-height:1.38;color:{LIGHT};opacity:0.95;margin-top:48px;text-shadow:0 2px 20px rgba(0,0,0,0.6)}}
.sp{{flex:1}}
.foot{{display:flex;align-items:center;gap:18px}}
.foot .cta{{font-family:'Fraunces';font-weight:600;font-size:34px;color:{SAND};text-shadow:0 2px 18px rgba(0,0,0,0.6)}}
.wave path{{stroke-dasharray:80;stroke-dashoffset:80;animation:draw 1.2s ease-out 3.6s both}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
</style></head><body>
<div class="c">
  <div class="photo"></div>
  <div class="scrim"></div>
  <div class="safe">
    <div class="top a" style="--d:0s">{mark(58)}<div class="wm">Tideglyph<span class="d">.</span></div></div>
    <div class="sp" style="flex:.8"></div>
    <div class="eb a" style="--d:.25s">{esc(spec.get("eyebrow","Today's sky"))}</div>
    {tag}
    <div class="h a" style="--d:1s">{esc(hl)}</div>
    {journal}
    <div class="sp"></div>
    <div class="foot a" style="--d:3.6s"><svg class="wave" width="66" height="22" viewBox="0 0 60 20" fill="none"><path d="M3 10 q6 -7 12 0 t12 0 t12 0 t12 0" stroke="{TIDE}" stroke-width="4" fill="none" stroke-linecap="round"/></svg><div class="cta">{cta}</div></div>
  </div>
</div></body></html>"""

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text()); photo = sys.argv[2]
    out = pathlib.Path(sys.argv[3]).resolve()
    hp = HERE / "_reel.html"; hp.write_text(html(spec, photo))
    frames = pathlib.Path(tempfile.mkdtemp(prefix="reel_"))
    subprocess.run(["node", str(HERE / "render_reel.mjs"), str(hp), str(frames), str(FPS), str(SECONDS)], check=True)
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(frames, ignore_errors=True)
    print("wrote", out)
