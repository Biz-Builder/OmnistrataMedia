import { chromium } from 'playwright';
import fs from 'fs';
// Use the container's preinstalled Chromium regardless of the installed
// playwright version, so the studio renders anywhere without downloading.
function findChrome(){
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  try {
    for (const d of fs.readdirSync(base)) {
      if (d.startsWith('chromium-')) {
        const p = `${base}/${d}/chrome-linux/chrome`;
        if (fs.existsSync(p)) return p;
      }
    }
  } catch (e) {}
  return undefined;
}
const [,, htmlPath, out] = process.argv;
const exe = findChrome();
const b = await chromium.launch(exe ? { executablePath: exe } : {});
const p = await b.newPage({ viewport:{width:1080,height:1350}, deviceScaleFactor:1 });
await p.goto('file://'+htmlPath);
await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(200);
await p.screenshot({ path: out, clip:{x:0,y:0,width:1080,height:1350} });
await b.close();
