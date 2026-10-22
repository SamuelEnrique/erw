// Energy Research Warehouse (ERW), session 585: for each page of the trader path, every heading (h2, h3) with the
// checked figures (data-check, data-n) drawn under it before the next heading, and the source lines in the same span
// (a line beginning "Source", the citation components/Cite.tsx draws, or a "from <file>" line). A span that holds figures
// and no source line is a figure without its source, for docs/reviews/trader-path.md. Read only: it clicks nothing.
//
//   node docs/brand/review-585/sources-585.mjs http://localhost:3585 <out.json> [path ...]
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs (the token posted by the form, never printed).
import fs from "node:fs";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3585").replace(/\/$/, "");
const out = process.argv[3] ?? "sources-585.json";
const pages = process.argv.slice(4).length ? process.argv.slice(4) : [
  "/cost-of-power/seller", "/cost-of-power/seller?iso=caiso&asset=wind", "/cost-of-power/battery",
  "/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100", "/board",
];

const SPANS = `(() => {
  const all = [...document.querySelectorAll("main h2, main h3, main [data-check], main [data-n], main p, main div, main li, main small, main figcaption")];
  const spans = []; let cur = { heading: "(top)", figures: 0, keys: [], sources: [] };
  const isSource = (t) => /^(Source|Sources)\\b/.test(t) || /^(From|Read from|Data:)\\s/.test(t);
  for (const e of all) {
    if (e.tagName === "H2" || e.tagName === "H3") { spans.push(cur); cur = { heading: e.tagName + " " + e.textContent.replace(/\\s+/g, " ").trim().slice(0, 90), figures: 0, keys: [], sources: [] }; continue; }
    if (e.hasAttribute("data-check") || e.hasAttribute("data-n")) { cur.figures += 1; if (cur.keys.length < 3) cur.keys.push(e.getAttribute("data-check") || e.getAttribute("data-n")); continue; }
    if (e.children.length && e.tagName === "DIV") continue;
    const t = e.textContent.replace(/\\s+/g, " ").trim();
    if (isSource(t) && !cur.sources.includes(t.slice(0, 200))) cur.sources.push(t.slice(0, 200));
  }
  spans.push(cur);
  return spans;
})()`;

const res = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await unlock(base);
  const got = {};
  for (const p of pages) {
    await go(base + p);
    await sleep(p.startsWith("/board") ? 5000 : 3000);
    got[p] = await evaluate(SPANS);
    const bare = got[p].filter((s) => s.figures > 0 && s.sources.length === 0);
    console.log(`${p}: ${got[p].length} spans, ${got[p].filter((s) => s.figures).length} with figures, ${bare.length} with figures and no source line${bare.length ? ": " + bare.map((s) => s.heading + " (" + s.figures + ")").join("; ") : ""}`);
  }
  return got;
}, { width: 1280, height: 900 });
if (!res) { console.log("no browser on this machine"); process.exit(1); }
fs.writeFileSync(out, JSON.stringify(res, null, 1));
