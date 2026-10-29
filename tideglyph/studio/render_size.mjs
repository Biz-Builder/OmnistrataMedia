import { chromium } from 'playwright';
import fs from 'fs';
// Like render.mjs, but the viewport size comes from the command line,
// so the same studio can render 1080x1350 posts and 1080x1920 Stories.
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
const [,, htmlPath, out, wArg, hArg] = process.argv;
const W = Number(wArg || 1080), H = Number(hArg || 1350);
const exe = findChrome();
const b = await chromium.launch(exe ? { executablePath: exe } : {});
const p = await b.newPage({ viewport:{width:W,height:H}, deviceScaleFactor:1 });
await p.goto('file://'+htmlPath);
await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(200);
await p.screenshot({ path: out, clip:{x:0,y:0,width:W,height:H} });
await b.close();
