#!/usr/bin/env python3
"""TikTok format test (from 12 Nov 2026): one idea, two formats.
Renders a set of 9:16 slides for one idea, then:
  - a carousel: the slides as JPEGs (TikTok photo posts reject PNG)
  - a Reel: the same slides as a video, about 2.6 s each with a short fade,
    over Tideglyph's own music bed
so the only thing that differs between the two posts is the format.
Usage: python3 make_slides.py spec.json outdir
spec.json: {"id": "2026-11-12-one-of-three",
            "slides": [{"kind": "hook", "text": "...", "sub": "..."},
                       {"kind": "body", "label": "Sun", "text": "..."},
                       {"kind": "cta", "text": "Find your big three, free", "sub": "Comment yours below."}]}
Writes outdir/<id>-01.jpg ... and outdir/<id>.mp4"""
import sys, json, pathlib, subprocess, tempfile, shutil
from make_card import faces, mark, esc, PAPER, INK, RUST, TIDE, MUTED, HERE
from make_reel import ffmpeg_bin

W, H = 1080, 1920
PER, FADE = 2.6, 0.4

def slide_html(s, i, n):
    k = s["kind"]
    if k == "hook":
        t = s["text"]; L = len(t)
        fs = 104 if L <= 32 else 92 if L <= 48 else 80 if L <= 70 else 70
        body = f'<div class="hook" style="font-size:{fs}px">{esc(t)}</div>' + (f'<div class="sub">{esc(s["sub"])}</div>' if s.get("sub") else "")
    elif k == "body":
        t = s["text"]; L = len(t)
        fs = 72 if L <= 60 else 64 if L <= 90 else 56
        body = (f'<div class="lab">{esc(s["label"])}</div>' if s.get("label") else "") + f'<div class="txt" style="font-size:{fs}px">{esc(t)}</div>'
    else:
        body = (f'<div class="btn">{esc(s.get("text","Find your big three, free"))}</div>'
                f'<div class="url">tideglyph.com/chart</div>' + (f'<div class="sub">{esc(s["sub"])}</div>' if s.get("sub") else ""))
    dots = "".join(f'<span class="{"on" if j == i else ""}"></span>' for j in range(n))
    return f"""<!doctype html><html><head><meta charset=utf-8><style>
{faces()}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER}}}
.c{{width:{W}px;height:{H}px;background:{PAPER};padding:240px 170px 420px 84px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:14px}}
.wm{{font-family:'Fraunces';font-weight:600;font-size:38px;color:{INK};letter-spacing:-1px}} .wm .d{{color:{RUST}}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center}}
.hook{{font-family:'Fraunces';font-weight:600;line-height:1.04;color:{INK};letter-spacing:-1.5px}}
.sub{{font-family:'Newsreader';font-style:italic;font-size:46px;color:{MUTED};margin-top:28px;line-height:1.3}}
.lab{{font-family:'Newsreader';font-weight:500;font-size:30px;letter-spacing:5px;text-transform:uppercase;color:{RUST};margin-bottom:22px}}
.txt{{font-family:'Fraunces';font-weight:600;line-height:1.14;color:{INK};letter-spacing:-.5px}}
.btn{{align-self:flex-start;background:{RUST};color:#F7EFE6;font-family:'Fraunces';font-weight:600;font-size:52px;padding:28px 44px;border-radius:18px}}
.url{{font-family:'Newsreader';font-weight:500;font-size:40px;color:{TIDE};margin-top:26px}}
.dots{{display:flex;gap:12px}} .dots span{{width:14px;height:14px;border-radius:7px;background:#D9CDB6}} .dots span.on{{background:{RUST}}}
</style></head><body><div class="c">
<div class="top">{mark(48)}<div class="wm">Tideglyph<span class="d">.</span></div></div>
<div class="mid">{body}</div>
<div class="dots">{dots}</div>
</div></body></html>"""

def main(spec, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    sid, slides = spec["id"], spec["slides"]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="slides_"))
    pngs = []
    for i, s in enumerate(slides):
        hp = HERE / "_slide.html"; hp.write_text(slide_html(s, i, len(slides)))
        png = tmp / f"s{i+1:02d}.png"
        subprocess.run(["node", str(HERE / "render_size.mjs"), str(hp), str(png), str(W), str(H)], check=True)
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(png), "-q:v", "2", str(outdir / f"{sid}-{i+1:02d}.jpg")], check=True)
        pngs.append(png)
    # video: each slide PER seconds, crossfade FADE, music bed
    n = len(pngs); total = n * PER - (n - 1) * FADE
    inputs = []
    for p in pngs:
        inputs += ["-loop", "1", "-t", str(PER), "-framerate", "30", "-i", str(p)]
    fc, last, off = [], "[0:v]", PER - FADE
    for i in range(1, n):
        lab = f"[v{i}]"
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={off:.2f}{lab}")
        last, off = lab, off + PER - FADE
    bed = HERE / "audio" / "tideglyph-bed.m4a"
    start = sum(map(ord, slides[0]["text"])) % 48
    fc.append(f"[{n}:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.4,afade=t=out:st={total-1.2:.2f}:d=1.2,volume=0.9[a]")
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", *inputs, "-ss", str(start), "-i", str(bed),
                    "-filter_complex", ";".join(fc), "-map", last, "-map", "[a]", "-t", f"{total:.2f}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(outdir / f"{sid}.mp4")], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", outdir, sid, n, "slides")

if __name__ == "__main__":
    main(json.loads(pathlib.Path(sys.argv[1]).read_text()), pathlib.Path(sys.argv[2]))
