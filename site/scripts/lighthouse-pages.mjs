// Energy Research Warehouse (ERW) site, session 411 (21 October 2026): Lighthouse on every visitor page, at 1280 and
// 390 px, on a local production build only, the internal view open, one run at a time.
//
//   node scripts/lighthouse-pages.mjs <base> <out.json> [page ...]
//   e.g. node scripts/lighthouse-pages.mjs http://localhost:3411 ../runs/chain_oct21/s411/before.json
//
// The pages: the 25 addresses of scripts/snapshot-live.mjs and the tool pages that are not among them (TOOL_PAGES).
// Every page is in review, so the internal view is opened first: the token is posted to /internal/unlock in the body
// (browser.mjs unlockPost, never in an address) and the two cookies it answers are set in the browser for the local
// host only (never sent as a header to every host). Lighthouse keeps cookies between runs (its storage reset leaves
// them), and each run is checked: a page that answered the in-review curtain is marked `curtain` and not scored.
//
// Lighthouse is the npm package lighthouse 13.4.1 with the puppeteer-core it installs, in a folder of its own outside
// the repository named by LIGHTHOUSE_DIR (npm install lighthouse@13.4.1 --ignore-scripts there). The copy bundled in the
// installed chrome-devtools-mcp (docs/tooling.md, 1.10.1) was tried first and is not used: its performance audits are
// shims ("This audit was filtered out and is not available in this bundle"), so its performance score is a constant
// 100. A report whose first-contentful-paint is such a shim is refused here. The machine's own Chrome runs headless
// with a fresh profile and is closed at the end, whatever happens.
//
// The two forms: 1280 by 800, desktop, Lighthouse's desktop throttling (40 ms, 10 Mbit/s, no CPU slowdown); 390 by 844,
// mobile, Lighthouse's default mobile throttling (simulated slow 4G, CPU 4x). The four categories: performance,
// accessibility, best practices, SEO. A run against anything but localhost is refused: never production.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { browserPath, env, unlockPost } from "./browser.mjs";
import { LIVE_PAGES } from "./snapshot-live.mjs";

// The five tool pages of the chain of 20 October (session 401): /cost-of-power/battery and /cost-of-power/seller are
// among the 25; /analysis redirects to /research (next.config.ts), /network to /grid?view=network.
export const TOOL_PAGES = ["/cost-of-power", "/research", "/grid"];
export const PAGES = [...LIVE_PAGES, ...TOOL_PAGES.filter((p) => !LIVE_PAGES.includes(p))];
export const CATEGORIES = ["performance", "accessibility", "best-practices", "seo"];

const DESKTOP_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36";
const MOBILE_UA = "Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36";
export const FORMS = {
  1280: { formFactor: "desktop", screenEmulation: { mobile: false, width: 1280, height: 800, deviceScaleFactor: 1, disabled: false }, emulatedUserAgent: DESKTOP_UA,
    throttling: { rttMs: 40, throughputKbps: 10 * 1024, cpuSlowdownMultiplier: 1, requestLatencyMs: 0, downloadThroughputKbps: 0, uploadThroughputKbps: 0 } },
  390: { formFactor: "mobile", screenEmulation: { mobile: true, width: 390, height: 844, deviceScaleFactor: 2, disabled: false }, emulatedUserAgent: MOBILE_UA },
};

export function lighthouseDir() {
  const d = process.env.LIGHTHOUSE_DIR;
  return d && fs.existsSync(path.join(d, "node_modules", "lighthouse", "core", "index.js")) ? d : null;
}

function cookiesOf(res) {
  return res.headers.getSetCookie().map((c) => {
    const [pair] = c.split(";");
    const i = pair.indexOf("=");
    return { name: pair.slice(0, i).trim(), value: pair.slice(i + 1).trim() };
  });
}

async function main() {
  const [base, out, ...only] = process.argv.slice(2);
  if (!base || !out) { console.error("usage: node scripts/lighthouse-pages.mjs <base> <out.json> [page ...]"); return 2; }
  const host = new URL(base).hostname;
  if (host !== "localhost" && host !== "127.0.0.1") { console.error(`${base}: Lighthouse runs on a local build only, never production`); return 2; }
  const dir = lighthouseDir();
  if (!dir) { console.error("LIGHTHOUSE_DIR does not name a folder holding node_modules/lighthouse (npm install lighthouse@13.4.1 there)"); return 2; }
  const exe = browserPath();
  if (!exe) { console.error("no Chrome or Edge on this machine"); return 2; }
  const token = env("INTERNAL_COSTS_TOKEN");
  if (!token) { console.error("INTERNAL_COSTS_TOKEN is not set: the pages in review cannot be opened"); return 2; }
  const res = await unlockPost(base, token);
  const cookies = cookiesOf(res);
  if (res.status !== 303 || !cookies.length) { console.error(`the internal view did not open (${res.status})`); return 1; }
  const lighthouse = (await import(pathToFileURL(path.join(dir, "node_modules", "lighthouse", "core", "index.js")).href)).default;
  const puppeteer = (await import(pathToFileURL(path.join(dir, "node_modules", "puppeteer-core", "lib", "puppeteer", "puppeteer-core.js")).href)).default;

  const pages = only.length ? only : PAGES;
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-lighthouse-"));
  const browser = await puppeteer.launch({ executablePath: exe, headless: true, userDataDir: profile,
    args: ["--no-first-run", "--no-default-browser-check", "--disable-background-networking", "--disable-component-update", "--disable-sync", "--disable-extensions"] });
  const results = [];
  let failed = 0;
  try {
    const domain = host;
    const jar = cookies.map((c) => ({ ...c, domain, path: "/" }));
    if (typeof browser.setCookie === "function") await browser.setCookie(...jar);
    for (const page of pages) {
      for (const width of [1280, 390]) {
        const t0 = Date.now();
        const tab = await browser.newPage();
        if (typeof browser.setCookie !== "function") await tab.setCookie(...jar);
        const row = { page, width };
        try {
          const r = await lighthouse(`${base}${page}`, { onlyCategories: CATEGORIES, maxWaitForLoad: 60000, ...FORMS[width] }, undefined, tab);
          const lhr = r.lhr;
          if (/shim/i.test(lhr.audits["first-contentful-paint"]?.title ?? "")) throw new Error("the performance audits are shims: not a real Lighthouse");
          const curtain = await tab.evaluate(() => !!document.querySelector("[data-in-review]")).catch(() => null);
          row.final = lhr.finalDisplayedUrl.replace(base, "");
          row.curtain = curtain;
          row.scores = Object.fromEntries(CATEGORIES.map((c) => [c, lhr.categories[c]?.score == null ? null : Math.round(lhr.categories[c].score * 100)]));
          const a = lhr.audits;
          if (process.env.LIGHTHOUSE_KEEP) {   // the whole report of each run, for the detail of an audit
            fs.mkdirSync(process.env.LIGHTHOUSE_KEEP, { recursive: true });
            fs.writeFileSync(path.join(process.env.LIGHTHOUSE_KEEP, `${width}${page.replace(/[^A-Za-z0-9]+/g, "_")}.json`), JSON.stringify(lhr));
          }
          row.metrics = { fcp_ms: a["first-contentful-paint"]?.numericValue, lcp_ms: a["largest-contentful-paint"]?.numericValue, tbt_ms: a["total-blocking-time"]?.numericValue,
            cls: a["cumulative-layout-shift"]?.numericValue, si_ms: a["speed-index"]?.numericValue, bytes: a["total-byte-weight"]?.numericValue };
          row.failing = Object.values(a).filter((x) => x.score !== null && x.score < 0.9 && x.scoreDisplayMode !== "informative" && x.scoreDisplayMode !== "notApplicable" && x.scoreDisplayMode !== "manual")
            .map((x) => ({ id: x.id, score: x.score, value: x.displayValue ?? null })).sort((p, q) => p.score - q.score);
          row.runtimeError = lhr.runtimeError?.code ?? null;
          row.version = lhr.lighthouseVersion;
          if (curtain) failed += 1;
        } catch (e) {
          row.error = String(e?.message ?? e).slice(0, 300);
          failed += 1;
        } finally {
          await tab.close().catch(() => {});
        }
        row.seconds = Math.round((Date.now() - t0) / 1000);
        results.push(row);
        const s = row.scores ? CATEGORIES.map((c) => row.scores[c]).join(" ") : `error: ${row.error}`;
        console.log(`${width} ${page}: ${s}${row.curtain ? " CURTAIN" : ""} (${row.seconds} s)`);
        fs.writeFileSync(out, JSON.stringify({ base, taken_utc: new Date().toISOString(), lighthouse: "lighthouse 13.4.1 (npm)", results }, null, 1));
      }
    }
  } finally {
    await browser.close().catch(() => {});
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch { /* the browser still holds a file */ }
  }
  console.log(`${results.length} runs, ${failed} failed or curtained -> ${out}`);
  return failed ? 1 : 0;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) process.exitCode = await main();
