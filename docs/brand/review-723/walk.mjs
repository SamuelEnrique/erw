// Chain 062: walk a list of addresses in the internal view; for each, a screenshot and the visible text of the page's
// main area (and of a chosen element), so a session can read what the page said at each step.
//   node walk.mjs <site-dir> <base> <steps.json> <out-dir>
// steps.json: [{ "name": "s1", "path": "/cost-of-power?...", "w": 1280, "h": 900, "sel": "optional css", "focus": "optional css" }]
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
const [siteDir, base, stepsFile, outDir] = process.argv.slice(2);
const B = await import(pathToFileURL(path.join(path.resolve(siteDir), "scripts", "browser.mjs")).href);
const steps = JSON.parse(fs.readFileSync(stepsFile, "utf-8"));
fs.mkdirSync(outDir, { recursive: true });
const code = await B.withBrowser(async ({ go, wait, unlock, send, sleep, evaluate }) => {
  await unlock(base);
  for (const s of steps) {
    const w = s.w ?? 1280, h = s.h ?? 900;
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 600 });
    await go(base + s.path);
    try { await wait(`!!document.querySelector(${JSON.stringify(s.sel ?? "main")})`, 30000, s.sel ?? "main"); } catch (e) { console.log(`${s.name}: ${e.message}`); }
    await sleep(1500);
    if (s.focus) await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(s.focus)}); if (e) { e.scrollIntoView({ block: "center" }); e.focus(); } return !!e; })()`);
    else if (s.scroll) await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(s.scroll)}); if (e) e.scrollIntoView({ block: "start" }); return !!e; })()`);
    await sleep(500);
    const shot = await send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(outDir, `${s.name}_${w}.png`), Buffer.from(shot.data, "base64"));
    const text = await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(s.sel ?? "main")}) ?? document.body; return e.innerText; })()`);
    const extra = await evaluate(`JSON.stringify({ wide: document.documentElement.scrollWidth, high: document.documentElement.scrollHeight, title: document.title, bytes: document.documentElement.outerHTML.length })`);
    fs.writeFileSync(path.join(outDir, `${s.name}_${w}.txt`), `${base}${s.path}\n${extra}\n\n${text}`);
    console.log(`${s.name} ${w}: ${extra}`);
  }
  return 0;
});
process.exitCode = code === 0 ? 0 : 1;
