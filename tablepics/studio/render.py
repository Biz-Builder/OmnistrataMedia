import os, json, qrcode, qrcode.image.svg, io, html
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
F=HERE+"/fonts"
BRIC=F+"/bricolage-grotesque-latin-wght-normal.woff2"
AT4=F+"/atkinson-hyperlegible-next-latin-400-normal.woff2"
AT7=F+"/atkinson-hyperlegible-next-latin-700-normal.woff2"
NIGHT="#121110"; N2="#1d1b18"; N3="#2b2823"; LIN="#f5f3ee"; FL="#ffb000"; SOFT="rgba(245,243,238,.68)"
GLYPH='<svg viewBox="7 7 16 16" width="{s}" height="{s}"><rect x="7" y="7" width="7" height="7" rx="1.5" fill="#ffb000"/><rect x="16" y="7" width="7" height="7" rx="1.5" fill="none" stroke="#f5f3ee" stroke-width="1.8"/><rect x="7" y="16" width="7" height="7" rx="1.5" fill="none" stroke="#f5f3ee" stroke-width="1.8"/><rect x="17.5" y="17.5" width="4" height="4" rx="1" fill="#f5f3ee"/></svg>'
def qr_svg(url,size):
    q=qrcode.QRCode(border=0,error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    m=q.get_matrix(); n=len(m); c=size/n
    r="".join(f'<rect x="{x*c:.2f}" y="{y*c:.2f}" width="{c+.3:.2f}" height="{c+.3:.2f}"/>' for y,row in enumerate(m) for x,v in enumerate(row) if v)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" fill="{NIGHT}">{r}</svg>'
def hl(t):  # *phrase* -> gold
    import re; return re.sub(r"\*(.+?)\*",r'<span class="hl">\1</span>',t)
TILES=[("#c98a4b","#6b3e1e","Naledi, 19:42"),("#d9b77a","#7a5a2a","Uncle Johan, 16:05"),("#e7a34a","#5a2f12","Table 4, 21:17"),("#9c6b4a","#3a2416","Thandi, 20:03"),("#cfa06a","#4e3320","Table 9, 22:41"),("#b8743c","#40220f","Sam, 18:12")]
def tile(i,w,h,cap=True):
    a,b,c=TILES[i%len(TILES)]
    return f'<div class="tile" style="width:{w}px;height:{h}px;background:radial-gradient(circle at 30% 25%,rgba(255,240,200,.55),rgba(255,240,200,0) 45%),linear-gradient(160deg,{a},{b})">{"<i>"+c+"</i>" if cap else ""}</div>'
def tent(label="Table 4"):
    return f'''<div class="tent"><div class="tentface"><div class="tl">{label}</div><div class="qr">{qr_svg("https://tablepics.com",210)}</div><div class="tb">Point your camera here.</div><div class="ts">Add your photos. No app.</div></div><div class="tentbase"></div></div>'''
def phone():
    t="".join(tile(i,150,150,False) for i in range(9))
    return f'<div class="phone"><div class="notch"></div><div class="ph">Our album</div><div class="pg">{t}</div><div class="pc">+ 412 more</div></div>'
def scatter():
    return f'<div class="scatter"><div class="s1">{tile(0,300,360)}</div><div class="s2">{tile(1,300,360)}</div><div class="s3">{tile(2,300,360)}</div></div>'
VIS={"tent":tent,"phone":phone,"scatter":scatter,"none":lambda:""}
import base64
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
FB,FA4,FA7=b64(BRIC),b64(AT4),b64(AT7)
CSS=f'''@font-face{{font-family:B;src:url(data:font/woff2;base64,{FB}) format("woff2");font-weight:200 800}}
@font-face{{font-family:A;src:url(data:font/woff2;base64,{FA4}) format("woff2");font-weight:400}}@font-face{{font-family:A;src:url(data:font/woff2;base64,{FA7}) format("woff2");font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
.sl{{width:1080px;height:1350px;background:{NIGHT};color:{LIN};position:relative;overflow:hidden;font-family:A;padding:96px 88px}}
.sl.mid{{display:flex;flex-direction:column;justify-content:center;padding-bottom:200px}}
.sl.lin{{background:{LIN};color:{NIGHT}}}
.glow{{position:absolute;right:-260px;top:-260px;width:820px;height:820px;border-radius:50%;background:radial-gradient(circle,rgba(255,176,0,.14),rgba(255,176,0,0) 65%)}}
.kick{{font-family:A;font-weight:700;font-size:30px;letter-spacing:3px;text-transform:uppercase;color:{FL};margin-bottom:28px}}
h1{{font-family:B;font-weight:800;letter-spacing:-.035em;line-height:.98;margin:0}}
.hl{{color:{FL}}} .lin .hl{{color:#8a5200}}
p.b{{font-size:40px;line-height:1.35;color:{SOFT};margin:34px 0 0;max-width:860px}} .lin p.b{{color:#4a443b}}
p.b b{{color:{LIN}}} .lin p.b b{{color:{NIGHT}}}
.num{{font-family:B;font-weight:800;font-size:200px;line-height:.8;color:{FL};letter-spacing:-.04em}}
.vis{{position:absolute;left:0;right:0;bottom:150px;display:flex;justify-content:center;align-items:flex-end}}
.foot{{position:absolute;left:88px;right:88px;bottom:64px;display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{SOFT}}}
.lin .foot{{color:#6f675c}}
.wm{{display:flex;align-items:center;gap:14px;font-family:B;font-weight:800;font-size:34px;color:{LIN};letter-spacing:-.5px}} .wm b{{color:{FL}}}
.lin .wm{{color:{NIGHT}}}
.tile{{border-radius:22px;position:relative;box-shadow:0 30px 60px -28px rgba(0,0,0,.6)}} .tile i{{position:absolute;left:18px;bottom:16px;font-style:normal;font-family:A;font-weight:700;font-size:24px;color:#fff;background:rgba(18,17,16,.55);padding:6px 14px;border-radius:999px}}
.tent{{display:flex;flex-direction:column;align-items:center}}
.tentface{{width:470px;background:{LIN};color:{NIGHT};border-radius:26px;padding:34px 40px 38px;text-align:center;clip-path:polygon(6% 0,94% 0,100% 100%,0 100%);box-shadow:0 40px 80px -30px rgba(0,0,0,.8)}}
.tl{{font-family:B;font-weight:800;font-size:44px;letter-spacing:-1px}} .qr{{margin:20px auto 18px;width:210px}} .tb{{font-weight:700;font-size:30px}} .ts{{font-size:26px;color:#4a443b;margin-top:4px}}
.tentbase{{width:560px;height:14px;border-radius:7px;background:{FL};margin-top:-2px}}
.phone{{width:500px;height:auto;background:{N2};border:3px solid {N3};border-radius:64px;padding:70px 34px 30px;position:relative;box-shadow:0 50px 90px -30px rgba(0,0,0,.9)}}
.notch{{position:absolute;top:22px;left:50%;margin-left:-60px;width:120px;height:30px;border-radius:15px;background:{NIGHT}}}
.ph{{font-family:B;font-weight:800;font-size:38px;margin:0 6px 22px}} .pg{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}} .pg .tile{{width:auto!important;height:122px!important;border-radius:14px}}
.pc{{margin:22px 6px 0;color:{FL};font-weight:700;font-size:28px}}
.scatter{{position:relative;width:900px;height:520px}} .scatter>div{{position:absolute}}
.s1{{left:20px;top:80px;transform:rotate(-7deg)}} .s2{{left:300px;top:10px;transform:rotate(3deg);z-index:2}} .s3{{left:580px;top:110px;transform:rotate(9deg)}}
.url{{display:inline-block;margin-top:48px;background:{FL};color:{NIGHT};font-family:B;font-weight:800;font-size:54px;padding:22px 44px;border-radius:999px;letter-spacing:-1px}}
.ctaqr{{position:absolute;right:88px;bottom:170px;background:{LIN};padding:26px;border-radius:26px;text-align:center;color:{NIGHT};font-weight:700;font-size:24px}}
.inc{{list-style:none;padding:0;margin:64px 0 0;font-size:36px;line-height:1.25;max-width:520px}} .inc li{{padding:14px 0 14px 54px;position:relative;border-top:1px solid rgba(245,243,238,.14)}} .inc li:before{{content:'';position:absolute;left:0;top:22px;width:26px;height:26px;border-radius:7px;background:{FL}}}
.items{{list-style:none;padding:0;margin:44px 0 0;font-size:40px;line-height:1.3;max-width:880px}} .items li{{padding:20px 0 20px 64px;position:relative;border-top:1px solid rgba(245,243,238,.14)}} .items li:before{{content:'';position:absolute;left:0;top:30px;width:30px;height:30px;border-radius:8px;background:{FL}}}
.cmp{{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:56px}} .cc{{background:{N2};border:2px solid {N3};border-radius:28px;padding:36px 34px}} .cc.full{{border-color:{FL}}}
.cn{{font-family:B;font-weight:800;font-size:44px;letter-spacing:-1px}} .cp{{font-family:B;font-weight:800;font-size:76px;color:{FL};letter-spacing:-2px;margin:6px 0 18px}}
.cr{{display:flex;justify-content:space-between;gap:12px;padding:14px 0;border-top:1px solid rgba(245,243,238,.14);font-size:28px;color:{SOFT}}} .cr b{{color:{LIN};font-weight:700;text-align:right}}
.pager{{display:flex;gap:10px}} .pager span{{width:12px;height:12px;border-radius:6px;background:rgba(245,243,238,.25)}} .pager span.on{{background:{FL};width:34px}}
.lin .pager span{{background:rgba(23,20,15,.2)}} .lin .pager span.on{{background:{NIGHT}}}
'''
def slide(s,i,n):
    t=s.get("t","hook"); cls=("sl lin" if s.get("light") else "sl")+(" mid" if s.get("v","none")=="none" and t not in ("cta","compare") else "")
    wm='<div class="wm">'+GLYPH.format(s=40)+'<span>Table<b>Pics</b></span></div>'
    pager='<div class="pager">'+"".join(f'<span class="{"on" if k==i else ""}"></span>' for k in range(n))+'</div>'
    foot=f'<div class="foot">{wm}{pager}<span>@tablepix</span></div>'
    body=""
    if s.get("kick"): body+=f'<div class="kick">{s["kick"]}</div>'
    if t=="step": body+=f'<div class="num">{s["n"]}</div><div style="height:40px"></div>'
    body+=f'<h1 style="font-size:{s.get("size",112)}px">{hl(s["h"])}</h1>'
    if s.get("b"): body+=f'<p class="b">{hl(s["b"])}</p>'
    if s.get("items"):
        body+='<ul class="items">'+"".join(f"<li>{hl(x)}</li>" for x in s["items"])+'</ul>'
    if t=="compare":
        def col(name,price,rows,full=False):
            r="".join(f'<div class="cr"><span>{a}</span><b>{b}</b></div>' for a,b in rows)
            return f'<div class="cc{" full" if full else ""}"><div class="cn">{name}</div><div class="cp">{price}</div>{r}</div>'
        body+='<div class="cmp">'+col("Essentials","R299",s["ca"])+col("Full","R499",s["cb"],True)+'</div>'
    if t=="cta":
        body+=f'<div class="url">tablepics.com</div><ul class="inc"><li>Unlimited guests</li><li>Original files, full quality</li><li>QR cards, table tents and a welcome sign</li><li>The whole album as one ZIP</li></ul><div class="ctaqr">{qr_svg("https://tablepics.com",230)}<div style="margin-top:12px">Scan to start</div></div>'
    vis=s.get("v","none"); vh=f'<div class="vis">{VIS[vis]()}</div>' if vis!="none" else ""
    glow='<div class="glow"></div>' if not s.get("light") else ""
    return f'<div class="{cls}">{glow}{body}{vh}{foot}</div>'
def render(posts,outdir):
    os.makedirs(outdir,exist_ok=True)
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1350})
        for key,post in posts.items():
            n=len(post["slides"])
            for i,s in enumerate(post["slides"]):
                pg.set_content(f'<html><head><style>{CSS}</style></head><body>{slide(s,i,n)}</body></html>')
                pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(200)
                pg.screenshot(path=f"{outdir}/{key}_{i+1:02d}.jpg",type="jpeg",quality=92)
        b.close()
if __name__=="__main__":
    import sys
    posts=json.load(open(sys.argv[1])); render(posts,sys.argv[2])
