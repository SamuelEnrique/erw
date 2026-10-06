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
// Session 67, the release gate (lib/release.ts): the pass above runs with the internal cookie (/internal/unlock with
// INTERNAL_COSTS_TOKEN from the environment, site/.env.local or ../.env), so it still covers every page. A second pass
// runs without it, as a visitor: each live page must open as itself, each page in review must show the in-review page
// (status 200, marked noindex), and the home page's menu must list the pages in review greyed. The API routes are not
// behind the gate; one of them is asked without the cookie to confirm it.
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
const { statusOf, RELEASE } = await import("../lib/release.ts");
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const baseline = (process.argv[3] ?? env("SITE_URL") ?? "").replace(/\/$/, "");

const PAGES = [
  "/deals/v3", "/data/methods/power_deals",  // session 130: the deals tracker, version 3, in review
  "/", "/board", "/emissions", "/storage", "/prices", "/prices/ercot%3AHB_HUBAVG", "/prices/caiso%3ATH_SP15_GEN-APND", "/prices/miso%3AINDIANA.HUB",
  "/prices/spp%3ASPPSOUTH_HUB", "/prices/nyiso%3AN.Y.C.", "/markets", "/grid", "/mix", "/mix?ba=erco&state=TX",
  "/mix?ba=ciso&state=CA", "/curtailment", "/consumption", "/data", "/data/standard", "/explorer/ercot-peak-premium",
  "/deals", "/map", "/datacenters", "/companies", "/policy", "/digest", "/roundup", "/analysis", "/about", "/terms",
  "/subscribe", "/ask",
  "/ask/ercot", "/ask/ercot?from=%2Fshoulder&title=The+shoulder+hours&s_grid=ERCOT&s_month=2025-01",  // session 92: Ask ERCOT, the reference version (the page only: the check never asks the model)
  "/mix/v2", "/mix/v2?grid=caiso&period=2026-04&vs=ercot", "/mix/v2?grid=pjm&period=2024", "/data/methods/generation_mix_hourly",  // session 94: the energy mix, version 2, in review
  "/queues", "/queues?grid=ercot&tech=battery", "/queues?grid=miso&tech=offshore_wind", "/data/methods/interconnection_queue_summary",  // session 95: the interconnection queue explorer, in review
  "/prices/compare", "/prices/compare?period=month&market=rtm&sort=spread", "/data/methods/hub_price_comparison",  // session 96: where power is cheap, in review
  "/demand", "/demand?area=caiso&rank=peak", "/demand?area=us48&rank=ytd", "/data/methods/demand_growth",  // session 97: the demand growth explorer, in review
  "/curtailment/v2", "/curtailment/v2?period=2026-05", "/curtailment/v2?period=2019", "/data/methods/caiso_curtailment_intervals",  // session 98: curtailment, version 2, in review
  // session 35: the seven grid pages
  "/network/v3", "/network/v3?view=day&t=2021-02-15&grid=ERCO&prices=1&trace=1",  // session 93: version 3, in review
  "/network", "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/nyiso", "/grid/isone", "/grid/miso", "/grid/spp",
  // session 36B: the Historical Event Analyzer
  "/events", "/events/uri-2021", "/events/covid-2020",
  "/cost-of-power", "/cost-of-power/seller", "/data/methods/cost_of_power", "/data/methods/event_study",  // the seller's tab: session 51
  // session 67: what a battery earns, its two grids, and the methods pages the live tools link to
  "/cost-of-power/battery", "/cost-of-power/battery?grid=caiso&dur=2&strat=dayahead", "/cost-of-power/battery?grid=ercot&dur=8&strat=foresight",
  "/data/methods/battery_stack", "/data/methods/grid_network", "/data/methods/storage",
  // session 72 (session 69's finish): the storage build-out, in review
  "/storage/buildout", "/storage/buildout?grid=ercot&measure=mwh", "/data/methods/storage_buildout",
  "/shoulder", "/shoulder?grid=caiso&month=2025-07", "/data/methods/shoulder_hours",  // session 75
  "/contracts", "/contracts?product=capacity",  // session 83
  "/storage/owners", "/storage/owners?grid=caiso", "/storage/owners?grid=isone",  // session 87
  "/battery/customer",  // session 88: a static page; scripts/check-no-request.mjs types into it in a real browser
  // session 86: the grids in review on the live battery page (open in the internal view; a visitor gets ERCOT)
  "/cost-of-power/battery?grid=nyiso&dur=4&strat=dayahead", "/cost-of-power/battery?grid=spp&dur=2&strat=foresight",
  "/play/battery", "/play/battery?more=1",  // session 63: the simple page and the full game
  "/tour",  // session 53: the guided tour
  "/data/methods/battery_game",  // session 50
  "/severance", "/severance/lease", "/data/methods/severance",
  "/learn/bill",
  "/learn/problems", "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill", "/learn/problems/when-the-grid-broke", "/learn/problems/storage-and-taxes",
  "/learn/problems/networks-and-money",  // session 55: set E
  "/events/caiso-heat-2020", "/events/elliott-2022", "/events/ercot-heat-2023",
  "/events/caiso-heat-2022",  // session 58
  "/events/cold-2025", "/events/east-heat-2025",  // session 64
  "/grid/caiso/alerts",  // session 60: the Flex Alert scorecard
  "/cost-of-power/battery/awards", "/data/methods/ercot_storage_dam_awards",  // session 115: the storage fleet's day-ahead awards (in review)
  "/data/methods/ercot_storage_dam_offers",  // session 116: what the storage fleet offered day-ahead (in review; the awards page's new section reads it)
  "/data/methods/ercot_storage_realtime",  // session 120: the storage fleet in real time (in review; the awards page's last section reads it)
  "/mix/clean", "/mix/clean?grid=caiso&year=2026", "/mix/clean?grid=nyiso&year=2024", "/data/methods/clean_energy",  // session 122: how clean, and when (in review)
  "/mix/stress", "/mix/stress?grid=caiso&year=2026", "/mix/stress?grid=nyiso&year=2025", "/data/methods/grid_stress",  // session 123: how hard the system works (in review)
];

function visible(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z#0-9]+;/gi, " ");
}
const noData = (html) => (visible(html).match(/\bno data\b/g) ?? []).length;

/** The internal view's cookies from a site's /internal/unlock, as a Cookie header; "" when the site does not accept the token. */
async function unlock(site) {
  const token = env("INTERNAL_COSTS_TOKEN");
  if (!token) return "";
  try {
    const r = await fetch(`${site}/internal/unlock?token=${encodeURIComponent(token)}`, { redirect: "manual" });
    return (r.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  } catch {
    return "";
  }
}

async function get(url, cookie = "") {
  try {
    const r = await fetch(url, { redirect: "follow", headers: cookie ? { Cookie: cookie } : {} });
    return { status: r.status, html: await r.text(), robots: r.headers.get("x-robots-tag") ?? "" };
  } catch (e) {
    return { status: 0, html: "", robots: "", error: String(e) };
  }
}
const inReview = (html) => html.includes('data-in-review="1"');

const cookie = await unlock(base);
if (!cookie) {
  console.log(`route check FAILED: ${base}/internal/unlock did not give the internal cookie (INTERNAL_COSTS_TOKEN missing here, or not the server's): the pages in review cannot be covered`);
  process.exit(1);
}
const baseCookie = baseline ? await unlock(baseline) : "";

let bad = 0;
console.log("== pass 1: every page, with the internal cookie");
for (const page of PAGES) {
  const now = await get(base + page, cookie);
  const msgs = [];
  if (now.status !== 200) msgs.push(`status ${now.status}${now.error ? ` (${now.error})` : ""}`);
  if (inReview(now.html)) msgs.push("the in-review page, although the internal cookie was sent");
  const text = visible(now.html);
  const undef = text.match(/.{0,60}\bundefined\b.{0,60}/);
  if (undef) msgs.push(`"undefined" in the page: ...${undef[0].replace(/\s+/g, " ").trim()}...`);
  let before = null;
  if (baseline) {
    const b = await get(baseline + page, baseCookie);
    // a baseline that shows its in-review page (its gate is on and it did not accept the token) is no baseline for the page
    if (b.status === 200 && !inReview(b.html)) before = noData(b.html);
  }
  const n = noData(now.html);
  if (before !== null && n > before) msgs.push(`${n} "no data" blocks, ${before} before (${baseline})`);
  bad += msgs.length ? 1 : 0;
  console.log(`${msgs.length ? "FAIL" : "ok  "} ${page}: ${now.status}, ${n} "no data"${before === null ? "" : ` (before ${before})`}`
    + (msgs.length ? `; ${msgs.join("; ")}` : ""));
}
console.log(`route check, pass 1: ${PAGES.length - bad} of ${PAGES.length} pages pass${baseline ? `, against ${baseline}` : " (no baseline)"}`);

console.log("== pass 2: as a visitor, without the cookie");
let bad2 = 0, nLive = 0, nReview = 0;
for (const page of PAGES) {
  const want = statusOf(page);
  const now = await get(base + page);
  const msgs = [];
  if (now.status !== 200) msgs.push(`status ${now.status}${now.error ? ` (${now.error})` : ""}`);
  if (want === "live") {
    nLive++;
    if (inReview(now.html)) msgs.push("a live page shows the in-review page");
  } else {
    nReview++;
    if (!inReview(now.html) || !visible(now.html).includes("This tool is in review and will open when it is approved")) msgs.push("a page in review does not show the in-review page");
    if (!/noindex/.test(now.robots) && !/<meta name="robots" content="[^"]*noindex/.test(now.html)) msgs.push("the in-review page is not marked noindex");
    if (/data-check=/.test(now.html)) msgs.push("the in-review page carries a number of the tool");
  }
  bad2 += msgs.length ? 1 : 0;
  console.log(`${msgs.length ? "FAIL" : "ok  "} ${page}: ${want}${msgs.length ? `; ${msgs.join("; ")}` : ""}`);
}
{
  // the menu, as a visitor sees it on the home page: every page of the list is named, the ones in review greyed
  const home = await get(base + "/");
  const { PAGES: LISTED } = await import("../lib/pages.ts");
  const msgs = [];
  for (const p of LISTED) {
    const label = p.label.replace(/&/g, "&amp;").replace(/'/g, "&#x27;");
    if (!home.html.includes(label)) msgs.push(`the menu does not name "${p.label}"`);
  }
  const greyed = (home.html.match(/class="[^"]*gate-review/g) ?? []).length;
  const inMenu = LISTED.filter((p) => statusOf(p.href) === "review").length;
  if (greyed < inMenu) msgs.push(`${greyed} greyed items on the home page, ${inMenu} pages of the menu are in review`);
  const reviewHrefs = new Set(LISTED.filter((p) => statusOf(p.href) === "review").map((p) => p.href));
  const linked = [...home.html.matchAll(/<a [^>]*href="([^"#?]*)/g)].map((m) => m[1]).filter((h) => reviewHrefs.has(h));
  if (linked.length) msgs.push(`a page in review is a link on the home page: ${[...new Set(linked)].join(", ")}`);
  // the API is not behind the gate (the game and the scheduled jobs read it): one read-only route, as a visitor
  const api = await get(base + "/api/play/top");
  if (inReview(api.html)) msgs.push("/api/play/top shows the in-review page: the gate must not cover the API");
  bad2 += msgs.length ? 1 : 0;
  console.log(`${msgs.length ? "FAIL" : "ok  "} the menu and the API as a visitor: ${greyed} greyed items, /api/play/top ${api.status}${msgs.length ? `; ${msgs.join("; ")}` : ""}`);
}
console.log(`route check, pass 2: ${nLive} live pages and ${nReview} pages in review asked as a visitor; ${bad2} failed. The list holds ${Object.values(RELEASE).filter((v) => v === "live").length} live entries.`);
process.exit(bad || bad2 ? 1 : 0);
