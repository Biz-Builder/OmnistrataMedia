import sys,os,json,base64
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import render as R
from playwright.sync_api import sync_playwright
CSS=R.CSS+'''
.cv{width:1080px;height:1350px;background:#121110;color:#f5f3ee;position:relative;overflow:hidden;font-family:A}
.cv .bg{position:absolute;inset:0;background-size:cover;background-position:center 35%}
.cv .bg:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,17,16,.45) 0%,rgba(18,17,16,0) 16%,rgba(18,17,16,0) 40%,rgba(18,17,16,.82) 66%,#121110 92%)}
.cv .txt{position:absolute;left:88px;right:88px;bottom:170px}
.cv .kick{text-shadow:0 2px 16px rgba(0,0,0,.6)}
.cv h1{font-size:118px;text-wrap:balance;text-shadow:0 4px 30px rgba(0,0,0,.55)}
.cv .foot{z-index:2}
'''
def cover(c,photo,n):
    wm='<div class="wm">'+R.GLYPH.format(s=40)+'<span>Table<b>Pics</b></span></div>'
    pager='<div class="pager">'+"".join(f'<span class="{"on" if k==0 else ""}"></span>' for k in range(n))+'</div>'
    kick=f'<div class="kick">{c["kick"]}</div>' if c.get("kick") else ""
    return f'''<div class="cv"><div class="bg" style="background-image:url(data:image/jpeg;base64,{photo});background-position:{c.get("pos","center 35%")}"></div>
<div class="txt">{kick}<h1>{R.hl(c["head"])}</h1></div>
<div class="foot">{wm}{pager}<span>@tablepix</span></div></div>'''
covers=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1350})
    for k,c in covers.items():
        ph=base64.b64encode(open(c["photo"],"rb").read()).decode()
        pg.set_content(f'<html><head><style>{CSS}</style></head><body style="margin:0">{cover(c,ph,c["n"])}</body></html>')
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
        pg.screenshot(path=f"{out}/{k}.jpg",type="jpeg",quality=90)
    b.close()
