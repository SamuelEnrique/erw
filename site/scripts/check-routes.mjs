// Energy Research Warehouse (ERW) site: the route check (session 29).
//
//   npm run build && npm start                       (the site on http://localhost:3000)
//   node scripts/check-routes.mjs [base-url] [baseline-url]
//
// GETs every page (never /api/ask, which calls the Claude API) and fails on:
//   1. a status other than 200;
//   2. the word "undefined" in the page's visible text (scripts and tags removed);
//   3. more "no data" blocks (components/NoData.tsx) than the same page shows at baseline-url, the site as it
//      was before a change (default: SITE_URL from the environment or ../.env): a table that is empty where
//      the page showed data before.
// Prints one line per page and a summary; exits 1 if any page fails. Session 29 wrote it for the table
// consolidation, which renamed every table the grid, mix, markets and prices pages read.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  return undefined;
}
const base = process.argv[2] ?? "http://localhost:3000";
const baseline = (process.argv[3] ?? env("SITE_URL") ?? "").replace(/\/$/, "");

const PAGES = [
  "/", "/board", "/prices", "/prices/ercot%3AHB_HUBAVG", "/prices/caiso%3ATH_SP15_GEN-APND", "/prices/miso%3AINDIANA.HUB",
  "/prices/spp%3ASPPSOUTH_HUB", "/prices/nyiso%3AN.Y.C.", "/markets", "/grid", "/mix", "/mix?ba=erco&state=TX",
  "/mix?ba=ciso&state=CA", "/curtailment", "/consumption", "/data", "/data/standard", "/explorer/ercot-peak-premium",
  "/deals", "/map", "/datacenters", "/companies", "/policy", "/digest", "/roundup", "/analysis", "/about", "/terms",
  "/subscribe", "/ask",
];

function visible(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z#0-9]+;/gi, " ");
}
const noData = (html) => (visible(html).match(/\bno data\b/g) ?? []).length;

async function get(url) {
  try {
    const r = await fetch(url, { redirect: "follow" });
    return { status: r.status, html: await r.text() };
  } catch (e) {
    return { status: 0, html: "", error: String(e) };
  }
}

let bad = 0;
for (const page of PAGES) {
  const now = await get(base + page);
  const msgs = [];
  if (now.status !== 200) msgs.push(`status ${now.status}${now.error ? ` (${now.error})` : ""}`);
  const text = visible(now.html);
  const undef = text.match(/.{0,60}\bundefined\b.{0,60}/);
  if (undef) msgs.push(`"undefined" in the page: ...${undef[0].replace(/\s+/g, " ").trim()}...`);
  let before = null;
  if (baseline) {
    const b = await get(baseline + page);
    if (b.status === 200) before = noData(b.html);
  }
  const n = noData(now.html);
  if (before !== null && n > before) msgs.push(`${n} "no data" blocks, ${before} before (${baseline})`);
  bad += msgs.length ? 1 : 0;
  console.log(`${msgs.length ? "FAIL" : "ok  "} ${page}: ${now.status}, ${n} "no data"${before === null ? "" : ` (before ${before})`}`
    + (msgs.length ? `; ${msgs.join("; ")}` : ""));
}
console.log(`route check: ${PAGES.length - bad} of ${PAGES.length} pages pass${baseline ? `, against ${baseline}` : " (no baseline)"}`);
process.exit(bad ? 1 : 0);
