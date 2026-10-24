#!/usr/bin/env python3
"""Render a TablePics product Reel: 1080x1920 vertical MP4, 14 seconds, silent audio track.

Usage: python3 make_reel.py spec.json out.mp4
spec.json: {"photo": "<path to a 4:5 photo>", "kick": "Weddings",
            "hook": "120 guests.<br>*120 cameras.*",
            "end": "Every guest's photos.<br>*One album.*",
            "price": "From R299, paid once"}
*phrase* turns gold. <br> forces a line break.

Scenes: 1 the problem over a photo (0 to 3.2s), 2 scan the QR card (3.2 to 7.6s),
3 the album fills (7.6 to 10.8s), 4 the offer (10.8 to 14s).
Text stays inside the Reels safe zone: clear of the top 250px, the bottom 420px
(caption area) and the right 170px (buttons).
Frames are captured with Playwright by pausing every CSS animation and setting its
time, then encoded with ffmpeg."""
import sys, os, json, base64, shutil, subprocess, tempfile, pathlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R
from playwright.sync_api import sync_playwright

FPS = 30
SECONDS = 14
NIGHT, LIN, FL = R.NIGHT, R.LIN, R.FL

def tiles(n):
    out = []
    for i in range(n):
        a, b, _ = R.TILES[i % len(R.TILES)]
        out.append(f'<div class="t" style="--d:{7.9 + i*0.16:.2f}s;background:radial-gradient(circle at 30% 25%,rgba(255,240,200,.55),rgba(255,240,200,0) 45%),linear-gradient(160deg,{a},{b})"></div>')
    return "".join(out)

def html(spec, photo_b64):
    wm = '<div class="wm">' + R.GLYPH.format(s=52) + '<span>Table<b>Pics</b></span></div>'
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{R.CSS}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:{NIGHT}}}
.v{{width:1080px;height:1920px;position:relative;overflow:hidden;background:{NIGHT};color:{LIN};font-family:A}}
.sc{{position:absolute;inset:0;opacity:0}}
@keyframes show{{0%{{opacity:0}}6%{{opacity:1}}94%{{opacity:1}}100%{{opacity:0}}}}
@keyframes showlast{{0%{{opacity:0}}8%{{opacity:1}}100%{{opacity:1}}}}
.q1{{animation:show 3.3s linear 0s both}}
.q2{{animation:show 4.5s linear 3.15s both}}
.q3{{animation:show 3.3s linear 7.55s both}}
.q4{{animation:showlast 3.2s linear 10.8s both}}
.a{{opacity:0;animation:rise .7s cubic-bezier(.2,.7,.2,1) var(--d) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(40px)}}to{{opacity:1;transform:none}}}}
/* scene 1 */
.bg{{position:absolute;inset:-40px;background-size:cover;background-position:center 30%;animation:zoom 3.3s linear 0s both}}
@keyframes zoom{{from{{transform:scale(1.04)}}to{{transform:scale(1.14)}}}}
.bg:after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,17,16,.55) 0%,rgba(18,17,16,.1) 25%,rgba(18,17,16,.35) 50%,rgba(18,17,16,.92) 78%,{NIGHT} 100%)}}
.safe{{position:absolute;left:84px;right:170px;top:250px;bottom:420px;display:flex;flex-direction:column}}
.sp{{flex:1}}
.wm{{font-size:46px}}
.kick{{font-size:34px;margin-bottom:22px;text-shadow:0 2px 16px rgba(0,0,0,.6)}}
.hook{{font-family:B;font-weight:800;font-size:128px;line-height:.96;letter-spacing:-.035em;text-wrap:balance;text-shadow:0 4px 30px rgba(0,0,0,.55)}}
/* scenes 2 and 3 */
.step{{font-family:B;font-weight:800;font-size:76px;line-height:1;letter-spacing:-.03em}}
.step i{{font-style:normal;color:{FL}}}
.sub{{font-size:38px;color:rgba(245,243,238,.72);margin-top:18px}}
.stage{{position:absolute;left:0;right:0;top:760px;height:760px}}
.tentw{{position:absolute;left:50px;top:170px;transform:scale(.76);transform-origin:left top}}
.phone{{position:absolute;right:150px;top:0;width:430px;height:760px;border-radius:64px;background:#1d1b18;border:4px solid #3a352d;box-shadow:0 50px 90px -30px rgba(0,0,0,.9);overflow:hidden;animation:pin 1s cubic-bezier(.2,.7,.2,1) 3.5s both}}
@keyframes pin{{from{{transform:translateY(260px) rotate(6deg);opacity:0}}to{{transform:none;opacity:1}}}}
.notch{{position:absolute;top:18px;left:50%;margin-left:-55px;width:110px;height:28px;border-radius:14px;background:{NIGHT}}}
.cam{{position:absolute;inset:60px 22px 22px;border-radius:30px;background:linear-gradient(180deg,#2b2823,#151412);display:flex;align-items:center;justify-content:center;animation:fadeout .4s linear 5.3s both}}
@keyframes fadeout{{to{{opacity:0}}}}
.frame{{width:250px;height:250px;border:6px solid {FL};border-radius:28px;position:relative;overflow:hidden}}
.beam{{position:absolute;left:0;right:0;height:6px;background:{FL};box-shadow:0 0 24px {FL};animation:scan 1.1s ease-in-out 4.1s 2 alternate both}}
@keyframes scan{{from{{top:8px}}to{{top:230px}}}}
.page{{position:absolute;inset:60px 22px 22px;border-radius:30px;background:{LIN};color:{NIGHT};padding:40px 30px;opacity:0;animation:fadein .4s linear 5.3s both}}
@keyframes fadein{{to{{opacity:1}}}}
.page .t1{{font-family:B;font-weight:800;font-size:40px;letter-spacing:-.02em}}
.page .t2{{font-size:26px;color:#4a443b;margin-top:10px}}
.btn{{margin-top:46px;background:{FL};color:{NIGHT};font-family:B;font-weight:800;font-size:34px;text-align:center;padding:26px 0;border-radius:999px;animation:press .5s ease-in-out 6.3s both}}
@keyframes press{{0%{{transform:scale(1)}}40%{{transform:scale(.92)}}100%{{transform:scale(1)}}}}
.fly{{margin:40px auto 0;width:150px;height:150px;border-radius:22px;background:radial-gradient(circle at 30% 25%,rgba(255,240,200,.55),rgba(255,240,200,0) 45%),linear-gradient(160deg,#c98a4b,#6b3e1e);opacity:0;animation:fly 1s cubic-bezier(.2,.7,.2,1) 6.6s both}}
@keyframes fly{{0%{{opacity:0;transform:scale(.6)}}30%{{opacity:1;transform:scale(1)}}100%{{opacity:0;transform:translateY(-220px) scale(.4)}}}}
.tap{{position:absolute;width:90px;height:90px;border-radius:50%;background:rgba(18,17,16,.25);border:4px solid rgba(18,17,16,.5);left:170px;top:340px;opacity:0;animation:tap .6s ease-out 6.2s both}}
@keyframes tap{{0%{{opacity:0;transform:scale(1.6)}}50%{{opacity:1;transform:scale(1)}}100%{{opacity:0;transform:scale(1)}}}}
.album{{position:absolute;left:84px;right:84px;top:640px;background:#1d1b18;border:3px solid #2b2823;border-radius:48px;padding:40px 36px}}
.album .h{{font-family:B;font-weight:800;font-size:46px;margin-bottom:26px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.t{{height:180px;border-radius:20px;opacity:0;animation:pop .35s cubic-bezier(.2,.7,.2,1) var(--d) both}}
@keyframes pop{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
.cnt{{position:relative;height:56px;margin-top:28px;font-family:B;font-weight:800;font-size:46px;color:{FL}}}
.cnt span{{position:absolute;left:0;top:0;opacity:0}}
.c1{{animation:blink .7s linear 8.6s both}} .c2{{animation:blink .7s linear 9.3s both}} .c3{{animation:fadein .3s linear 10s both}}
@keyframes blink{{0%{{opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{opacity:0}}}}
/* scene 4 */
.end{{font-family:B;font-weight:800;font-size:112px;line-height:.98;letter-spacing:-.035em;text-wrap:balance}}
.price{{display:inline-block;margin-top:46px;background:{FL};color:{NIGHT};font-family:B;font-weight:800;font-size:52px;padding:20px 40px;border-radius:999px}}
.note{{font-size:40px;color:rgba(245,243,238,.75);margin-top:30px}}
.url{{font-family:B;font-weight:800;font-size:64px;margin-top:56px}}
</style></head><body><div class="v">

<div class="sc q1">
  <div class="bg" style="background-image:url(data:image/jpeg;base64,{photo_b64})"></div>
  <div class="safe">
    <div class="a" style="--d:0s">{wm}</div>
    <div class="sp"></div>
    <div class="kick a" style="--d:.15s">{spec.get("kick","")}</div>
    <div class="hook a" style="--d:.3s">{R.hl(spec["hook"])}</div>
  </div>
</div>

<div class="sc q2">
  <div class="safe">
    <div class="step a" style="--d:3.3s"><i>1.</i> Scan the QR card</div>
    <div class="sub a" style="--d:3.45s">With the phone camera. No app.</div>
  </div>
  <div class="stage">
    <div class="tentw a" style="--d:3.35s">{R.tent("Table 4")}</div>
    <div class="phone"><div class="notch"></div>
      <div class="cam"><div class="frame"><div class="beam"></div></div></div>
      <div class="page"><div class="t1">Table 4</div><div class="t2">Add your photos to the album.</div>
        <div class="btn">Add photos</div><div class="fly"></div><div class="tap"></div></div>
    </div>
  </div>
</div>

<div class="sc q3">
  <div class="safe">
    <div class="step a" style="--d:7.65s"><i>2.</i> Every photo lands<br>in one album</div>
    <div class="sub a" style="--d:7.8s">Full quality, from every guest.</div>
  </div>
  <div class="album a" style="--d:7.7s">
    <div class="h">Our album</div>
    <div class="grid">{tiles(12)}</div>
    <div class="cnt"><span class="c1">+38 more</span><span class="c2">+156 more</span><span class="c3">+412 more</span></div>
  </div>
</div>

<div class="sc q4">
  <div class="safe">
    <div class="a" style="--d:10.9s">{wm}</div>
    <div class="sp"></div>
    <div class="end a" style="--d:11.05s">{R.hl(spec.get("end","Every guest's photos.<br>*One album.*"))}</div>
    <div><div class="price a" style="--d:11.4s">{spec.get("price","From R299, paid once")}</div></div>
    <div class="note a" style="--d:11.6s">No fee for each guest. No app.</div>
    <div class="url a" style="--d:11.8s">tablepics.com</div>
  </div>
</div>

</div></body></html>"""

def main(spec_path, out):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    photo = base64.b64encode(open(spec["photo"], "rb").read()).decode()
    frames = pathlib.Path(tempfile.mkdtemp(prefix="tpreel_"))
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(html(spec, photo))
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(FPS * SECONDS):
            t = i * 1000 / FPS
            pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={t})")
            pg.screenshot(path=str(frames / f"f{i:04d}.png"))
        b.close()
    ff = shutil.which("ffmpeg") or "ffmpeg"
    subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(frames, ignore_errors=True)
    print("wrote", out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
