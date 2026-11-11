#!/usr/bin/env python3
"""Render the big three ad as a 9:16 video for TikTok (and Reels): the hook lands,
then the Sun, Moon and rising sign reveal one by one, then the promise.
Same layout and words as make_big3_ad.py, with Tideglyph's own music bed.
Layout stays inside the TikTok safe zone: clear of the top bar, the caption and
buttons at the bottom, and the action column on the right.
Usage: python3 make_big3_video.py spec.json out.mp4   (spec as make_big3_ad.py)"""
import sys, json, pathlib, subprocess, tempfile, shutil
from make_big3_ad import html as ad_html
from make_reel import ffmpeg_bin, HERE

FPS, SECONDS = 30, 10

ANIM = """
.hook,.sub,.card,.row,.foot{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.hook{animation-delay:.2s}.sub{animation-delay:1.2s}.card{animation-delay:2.0s}
.row:nth-of-type(1){animation-delay:2.6s}.row:nth-of-type(2){animation-delay:4.0s}.row:nth-of-type(3){animation-delay:5.4s}
.foot{animation-delay:7.0s}
@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
"""

def html(spec):
    page, W, H = ad_html(dict(spec, size="story"))
    # TikTok: keep 170px clear on the right for the action column
    page = page.replace("padding:250px 90px 380px", "padding:240px 170px 420px 80px")
    page = page.replace(".row:first-of-type", ".card .row:first-of-type")
    # the example label is the card's first child; rows are nth-of-type among divs, so label rows explicitly
    page = page.replace('<div class="row">', '<section class="row">').replace("</div></div></div>", "</div></div></section>")
    page = page.replace("</style>", ANIM.replace(".row:nth-of-type", "section.row:nth-of-type") + "</style>")
    return page

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text()); out = pathlib.Path(sys.argv[2]).resolve()
    hp = HERE / "_big3v.html"; hp.write_text(html(spec))
    frames = pathlib.Path(tempfile.mkdtemp(prefix="b3v_"))
    subprocess.run(["node", str(HERE / "render_reel.mjs"), str(hp), str(frames), str(FPS), str(SECONDS)], check=True)
    bed = HERE / "audio" / "tideglyph-bed.m4a"
    start = sum(map(ord, spec["hook"])) % 48
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"),
                    "-ss", str(start), "-i", str(bed), "-filter_complex",
                    f"[1:a]atrim=0:{SECONDS},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.4,afade=t=out:st={SECONDS-1.2}:d=1.2,volume=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(frames, ignore_errors=True)
    print("wrote", out)
