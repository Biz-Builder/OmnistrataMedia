import { chromium } from 'playwright';
import fs from 'fs';
// Capture a CSS-animated page frame by frame by pausing every animation and
// stepping its currentTime, so the output is identical on every run.
function findChrome(){
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  try {
    for (const d of fs.readdirSync(base)) {
      if (d.startsWith('chromium-')) {
        for (const sub of ['chrome-linux', 'chrome-linux64']) {
          const p = `${base}/${d}/${sub}/chrome`;
          if (fs.existsSync(p)) return p;
        }
      }
    }
  } catch (e) {}
  return undefined;
}
const [,, htmlPath, outDir, fpsArg, secArg] = process.argv;
const fps = Number(fpsArg || 30), secs = Number(secArg || 8);
const exe = findChrome();
const b = await chromium.launch(exe ? { executablePath: exe } : {});
const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
await p.goto('file://'+htmlPath);
await p.evaluate(()=>document.fonts.ready);
await p.evaluate(()=>document.getAnimations().forEach(a=>a.pause()));
const total = Math.round(fps*secs);
for (let i=0;i<total;i++){
  const t = i*1000/fps;
  await p.evaluate(t=>document.getAnimations().forEach(a=>{a.currentTime=t;}), t);
  await p.screenshot({ path: `${outDir}/f${String(i).padStart(4,'0')}.png`, clip:{x:0,y:0,width:1080,height:1920} });
}
await b.close();
