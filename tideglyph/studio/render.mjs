import { chromium } from 'playwright';
const [,, htmlPath, out] = process.argv;
const b = await chromium.launch();
const p = await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
await p.goto('file://'+htmlPath);
await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(200);
await p.screenshot({path:out, clip:{x:0,y:0,width:1080,height:1350}});
await b.close();
