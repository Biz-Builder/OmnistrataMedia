#!/usr/bin/env python3
"""Render a Tideglyph 'today's sky' Reel: 1080x1920 vertical MP4, about 8 seconds, silent.
Usage: python3 make_reel.py spec.json out.mp4
spec.json: {eyebrow, tag, headline, journal, cta}  (same fields as make_card.py)
Reuses the brand mark, tokens and fonts from make_card so the Reel matches the cards.
Text stays inside the Reels safe zone (clear of the top bar, the caption area at the
bottom and the buttons on the right). Frames are captured with Playwright by stepping
the CSS animations, then encoded with ffmpeg (system ffmpeg, else imageio-ffmpeg)."""
import sys, json, pathlib, subprocess, shutil, tempfile
from make_card import faces, mark, esc, PAPER, INK, RUST, TIDE, MUTED, HERE

FPS = 30
SECONDS = 8

def html(spec):
    hl = spec["headline"]; n = len(hl)
    hs = 96 if n <= 38 else 86 if n <= 54 else 76 if n <= 72 else 68
    tag = f'<div class="tag a" style="--d:.5s">{esc(spec.get("tag",""))}</div>' if spec.get("tag") else ""
    journal = f'<div class="journal a" style="--d:2.4s">{esc(spec.get("journal",""))}</div>' if spec.get("journal") else ""
    cta = esc(spec.get("cta", "Your free chart: tideglyph.com/chart"))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{PAPER}}}
.c{{width:1080px;height:1920px;background:{PAPER};position:relative;overflow:hidden}}
.ghost{{position:absolute;right:-120px;top:120px;opacity:0.07;animation:drift {SECONDS}s linear both}}
@keyframes drift{{from{{transform:translateY(0) rotate(0deg)}}to{{transform:translateY(60px) rotate(8deg)}}}}
.safe{{position:absolute;left:96px;right:170px;top:250px;bottom:420px;display:flex;flex-direction:column}}
.a{{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) var(--d) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(34px)}}to{{opacity:1;transform:translateY(0)}}}}
.top{{display:flex;align-items:center;gap:16px}}
.top .wm{{font-family:'Fraunces';font-weight:600;font-size:44px;color:{INK};letter-spacing:-1px}}
.top .wm .d{{color:{RUST}}}
.eb{{font-family:'Newsreader';font-weight:500;font-size:30px;letter-spacing:3px;text-transform:uppercase;color:{RUST}}}
.tag{{font-family:'Newsreader';font-weight:500;font-size:30px;color:{TIDE};margin-top:16px;letter-spacing:1px}}
.h{{font-family:'Fraunces';font-weight:600;font-size:{hs}px;line-height:1.08;color:{INK};margin-top:40px;letter-spacing:-1px}}
.journal{{font-family:'Newsreader';font-weight:400;font-style:italic;font-size:44px;line-height:1.38;color:{MUTED};margin-top:56px}}
.sp{{flex:1}}
.foot{{display:flex;align-items:center;gap:18px}}
.foot .cta{{font-family:'Fraunces';font-weight:600;font-size:34px;color:{RUST}}}
.wave path{{stroke-dasharray:80;stroke-dashoffset:80;animation:draw 1.2s ease-out 3.6s both}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
</style></head><body>
<div class="c">
  <div class="ghost">{mark(560)}</div>
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

def ffmpeg_bin():
    p = shutil.which("ffmpeg")
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "imageio-ffmpeg", "--break-system-packages", "-q"], check=True)
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text()); out = pathlib.Path(sys.argv[2]).resolve()
    hp = HERE / "_reel.html"; hp.write_text(html(spec))
    frames = pathlib.Path(tempfile.mkdtemp(prefix="reel_"))
    subprocess.run(["node", str(HERE / "render_reel.mjs"), str(hp), str(frames), str(FPS), str(SECONDS)], check=True)
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(frames, ignore_errors=True)
    print("wrote", out)
