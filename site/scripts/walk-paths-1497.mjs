// Energy Research Warehouse (ERW) site, session 1497 (chain 158): a user's path walked step by step on a built site, in
// the internal view (every page is in review): each step's page loaded in a real browser at 1280 by 900 (and the first
// at 390 by 844), a screenshot of the first screen, and what the reader sees there written down: the heading, the
// first checked figures (data-check, data-cell or data-stat, with their raw values), the count of "license needed" and
// "in review" notes, and any error in the page.
//
//   node scripts/walk-paths-1497.mjs <base> <path.json> <out folder>
//
// path.json: { "name": "...", "steps": [{ "id": "01", "what": "...", "url": "/cost-of-power/seller" }, ...] }. Writes
// <out>/<id>-1280.png, <out>/01-390.png and <out>/walk.json. Exit 0 when every step loaded, 1 when one did not, 2 on
// bad input or no browser. It reads only.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./browser.mjs";

const [base, file, out] = process.argv.slice(2);
if (!base || !file || !out) {
  console.error("usage: node scripts/walk-paths-1497.mjs <base> <path.json> <out folder>");
  process.exit(2);
}
const spec = JSON.parse(fs.readFileSync(file, "utf8"));
fs.mkdirSync(out, { recursive: true });

const READ = `(() => {
  const h1 = document.querySelector("h1")?.textContent?.trim() ?? "";
  const figs = [...document.querySelectorAll("[data-check],[data-cell],[data-stat]")].slice(0, 14).map((e) => ({
    key: e.getAttribute("data-check") || e.getAttribute("data-cell") || e.getAttribute("data-stat"),
    shown: (e.textContent || "").trim().slice(0, 40), raw: e.getAttribute("data-raw") }));
  const text = document.body.innerText || "";
  return { h1, figs, licenseNeeded: (text.match(/license needed/gi) || []).length, inReview: (text.match(/in review/gi) || []).length,
           width: document.documentElement.scrollWidth, title: document.title };
})()`;

const code = await withBrowser(async (h) => {
  await h.unlock(base);
  const steps = [];
  let failed = 0;
  for (const s of spec.steps) {
    try {
      await h.go(`${base}${s.url}`);
      await h.sleep(1500);
      const seen = await h.evaluate(READ);
      const shot = await h.send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(out, `${s.id}-1280.png`), Buffer.from(shot.data, "base64"));
      steps.push({ ...s, ...seen, errors: [...h.errors] });
      console.log(`ok   ${s.id} ${s.url} | ${seen.h1} | ${seen.figs.length} checked figures shown first | license needed ${seen.licenseNeeded}`);
    } catch (e) {
      failed += 1;
      steps.push({ ...s, error: String(e.message || e) });
      console.log(`FAIL ${s.id} ${s.url} | ${String(e.message || e).slice(0, 200)}`);
    }
  }
  fs.writeFileSync(path.join(out, "walk.json"), JSON.stringify({ name: spec.name, base, at: new Date().toISOString(), steps }, null, 1));
  return failed ? 1 : 0;
});
if (code === null) {
  console.error("no browser on this machine: not walked");
  process.exit(2);
}
// the first step at a phone's width, its own browser
if (spec.steps.length) {
  await withBrowser(async (h) => {
    await h.unlock(base);
    // a phone by the device metrics, as check-explorers.mjs does: a headless window alone does not go under about
    // 480 px, so its scroll width is no phone's (the first walk of session 1497 read 481 so, and was wrong)
    await h.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await h.go(`${base}${spec.steps[0].url}`);
    await h.sleep(1500);
    const shot = await h.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(out, `${spec.steps[0].id}-390.png`), Buffer.from(shot.data, "base64"));
    const w = await h.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]");
    console.log(`ok   ${spec.steps[0].id} at 390: scroll width ${w[0]}, client width ${w[1]}`);
    return 0;
  }, { width: 390, height: 844 });
}
process.exit(code);
