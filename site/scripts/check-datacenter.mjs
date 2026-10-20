// Energy Research Warehouse (ERW) site, session 138: "What a datacenter pays" (/cost-of-power), on the built site.
//
//   npm run build && npx next start -p 3138
//   node scripts/check-datacenter.mjs [base-url]      (default http://localhost:3138)
//
// Session 370: the page as it stands now. Session 213 put the page on the battery page's questions and moved what the
// grid sections drew (the tight hours, demand by region, the carbon-free share, the large load in line, how long a
// load waits, the rules in motion, the tariff lines) into its download, /cost-of-power/tables.csv; sessions 228, 236,
// 265, 280 and 317 changed the rest (the four questions' titles, the delivery table by component, the Commission's
// rate per MWh with the rate as printed on hover, a line for a grid the address names and the page does not hold, the
// chart in SVG). Each assertion of session 138 below either follows the page as it stands now (and reads the download
// where the figure moved there) or was retired with the block it described: the standalone contract panel (its
// terms are two scenario assumptions since session 213, held by check-datacenter-scenarios.mjs), and the block
// "Rules in motion" with its rows, hovers, fold and seven choices (undrawn since session 213: its rows are the table
// "rules" of the download, its count a figure of "How soon?"). archive/sessions/SESSION_370_REPORT.md lists each.
//
// As HTML, in the internal view (the page is in review):
//   opens      200, its title, the three tabs, the four questions (What will it pay? Will the power be there? How
//              clean? How soon?), no "undefined", no NaN; it names its Method note and links the note's list of what
//              the model cannot see
//   numbers    the summary sentence's figures equal the arithmetic of lib/datacenter.ts over the site's own files, for
//              a flat load, a load off in 100 hours a year bought day-ahead, and a shifting load in California
//   uneven     a region with no price in the market named reads "not held yet" with its reason on hover, and no number
//   forecast   (session 140) a flexible load's figures are the forecast rule's (lib/datacenter.ts monthsRuled), with the
//              same load "if perfectly foreseen" beside them; a load zone shows its trading hub beside it
//   new york   (session 149) New York's load in line is not shown (NYISO's terms): the download says so with the reason
//   blank      MISO reads "paused while terms are reviewed" and PJM "licensed source needed", neither selectable; an
//              address that names one opens the default grid and says so in one line
//   download   (session 370) the tables session 213 moved: the large load in line "not published anywhere yet", how
//              long a load waits "not measured here" for ERCOT; ERCOT's tight hours (the file's count) and the hours a
//              flexible load was off in them (the library's); ERCOT's eight weather zones with their growth; the
//              load's own hours against the grid's carbon-free share (the library's); ISO-NE's demand held internally
//              and none of it shown; SPP's tight hours not held; every tariff line with its page, date and address
//   delivery   Texas: the four wires utilities as the columns of a table by component, transmission and distribution
//              apart, each figure's hover naming the tariff lines it sums as printed; the Commission's wholesale
//              transmission rate as a row of its own, per MWh, with the rate as printed on hover; another grid "not
//              held yet"
//   rules      for each of the seven grids an address can name, "How soon?" counts the file's rows (lib/rules.ts) with
//              the newest, or MISO's pause; the download's table "rules" holds exactly the file's rows and federal rows
//   view       ?view=grids is what the tab showed before: its ranking, ERCOT since 2018, the hours of the day, cost
//              against carbon and the calculator
//   visitor    without the cookie the page is the in-review page
// In a real browser: the chart is drawn and answers the mouse with the year and its figures; ERCOT's regions are load
// zones, then trading hubs; choosing another grid opens that grid with its own regions; no script error.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser, unlockPost } from "./browser.mjs";
import { cleanShare, expandSeries, gpuHour, lastTwelve, monthsOf, monthsRuled, span, two, usdShort } from "../lib/datacenter.ts";
import { MUNICIPAL, PAUSED_WORDS, RULE_GRIDS, blockOf, fileOf } from "../lib/rules.ts";
import { conditionOf, deliveryOf, kindOf, slugOf, utilitiesOf } from "../lib/datacenter/delivery.ts";

const base = (process.argv[2] ?? "http://localhost:3138").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = new URL("../data/datacenter/", import.meta.url);
const index = JSON.parse(fs.readFileSync(new URL("index.json", dir), "utf-8"));
const files = (g) => index.grids[g].years.map((y) => JSON.parse(fs.readFileSync(new URL(`${g}_${y}.json`, dir), "utf-8")));
const unlock = await unlockPost(base, env("INTERNAL_COSTS_TOKEN") ?? "");
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
const stat = (html, k) => new RegExp(`data-stat="${k}"[^>]*>([^<]*)<`).exec(html)?.[1] ?? null;
const decode = (t) => t.replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16))).replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d))).replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const attrs = (tag) => Object.fromEntries([...tag.matchAll(/([a-zA-Z_:-]+)="([^"]*)"/g)].map((m) => [m[1], decode(m[2])]));
const titles = (h) => [...h.matchAll(/\btitle="([^"]*)"/g)].map((m) => decode(m[1]));
// session 370: the page's download, tables.csv (table,row,column,value,note), where session 213 moved the grid sections
function csvRows(t) {
  const out = [];
  for (const line of t.split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    const cells = [];
    let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
      else if (ch === '"') q = true;
      else if (ch === ",") { cells.push(cur); cur = ""; }
      else cur += ch;
    }
    cells.push(cur);
    out.push(cells);
  }
  return out.slice(1).map(([table, row, column, value, note]) => ({ table, row, column, value: value ?? "", note: note ?? "" }));
}
const tablesOf = async (q = "") => csvRows((await get(`/cost-of-power/tables.csv${q}`)).html);
const cell = (rows, table, row, column) => rows.find((r) => r.table === table && r.row === row && r.column === column) ?? null;

const page = await get("/cost-of-power");
const html = face(page.html), text = plain(html);
const T = await tablesOf();
check(page.status === 200 && text.includes("What a datacenter pays") && !/\bundefined\b|NaN/.test(text), '/cost-of-power opens as "What a datacenter pays", with no "undefined" and no NaN');
check(["What a datacenter pays", "What a generator earns", "What a battery earns"].every((t) => plain(/<nav[^>]*aria-label="Cost of power"[\s\S]*?<\/nav>/.exec(page.html)?.[0] ?? "").includes(t)), "the three tabs: What a datacenter pays, What a generator earns, What a battery earns");
// session 213 named the first question for a buyer ("What will it pay?"); session 228 answered the other three, as questions
check(["What will it pay?", "Will the power be there?", "How clean?", "How soon?"].every((t) => html.includes(`>${t}</h2>`)), "the four questions are four sections: What will it pay? Will the power be there? How clean? How soon? (sessions 213 and 228)");
// session 190 linked the page's own note (datacenter_pays_algorithm); session 213 gave the three tools one line of what the model cannot see, linked to the note
check(page.html.includes("/data/methods/datacenter_pays_algorithm") && page.html.includes("datacenter_pays_algorithm#cannot-see") && (text.match(/cannot see/g) ?? []).length === 1 && !/upper bound|Wholesale energy only|limitation/i.test(text),
  "the page names its Method note (datacenter_pays_algorithm) and its one line of what the model cannot see links the note's list; no other method prose on its face");
check(/data-grid="miso"[^>]*data-open="0"[\s\S]{0,400}?paused while terms are reviewed/.test(html) && /data-grid="pjm"[^>]*data-open="0"[\s\S]{0,400}?licensed source needed/.test(html)
  && /<input[^>]*disabled=""[^>]*value="miso"|value="miso"[^>]*disabled=""/.test(html), 'MISO reads "paused while terms are reviewed" and PJM "licensed source needed"; neither can be chosen');
check(["ercot", "caiso", "nyiso", "isone", "spp"].every((g) => new RegExp(`data-grid="${g}"[^>]*data-open="1"`).test(html)), "the five public grids can each be chosen");
{
  // session 163's two lines, in the download since session 213
  const inLine = cell(T, "how_soon", "large_load_in_line", "mw"), waits = cell(T, "waits", "state", "words");
  check(!!inLine && inLine.value === "" && inLine.note.startsWith("not published anywhere yet") && waits?.value === "not measured here",
    'large load in line by region reads "not published anywhere yet" and how long a new large load waits "not measured here" for ERCOT (the download, tables.csv)');
}

for (const [q, grid, region, buy, x] of [
  ["/cost-of-power", "ercot", index.grids.ercot.main, "rt", { run: "flat", n: 0, pct: 0, shift: 0 }],
  ["/cost-of-power?grid=ercot&region=HB_WEST&mw=250&run=hours&n=100&buy=da", "ercot", "HB_WEST", "da", { run: "hours", n: 100, pct: 0, shift: 0 }],
  ["/cost-of-power?grid=caiso&run=shift&shift=20&buy=rt", "caiso", index.grids.caiso.main, "rt", { run: "shift", n: 0, pct: 0, shift: 20 }],
]) {
  const h = (await get(q)).html;
  const mw = Number(/[?&]mw=(\d+)/.exec(q)?.[1] ?? 100);
  // session 140: the page's figure for a flexible load is the forecast rule's; the foreseen figure stands beside it
  const s = span(lastTwelve(monthsRuled(files(grid), region, buy, x, "forecast").months));
  const hs = span(lastTwelve(monthsRuled(files(grid), region, buy, x, "hindsight").months));
  const want = { l12_per: two(s.per), l12_cost: usdShort(s.cost * mw), gpu_hour: gpuHour(s.per, 1.3, 1.56).toFixed(4), ...(x.run === "flat" ? {} : { l12_saved: two(s.flat - s.per), l12_saved_foreseen: two(hs.flat - hs.per) }) };
  if (x.run !== "flat") check(s.per >= hs.per - 1e-9, `${grid} ${region}, ${x.run}, ${buy}: the forecast rule (USD ${two(s.per)}) never pays less than the same load perfectly foreseen (USD ${two(hs.per)})`);
  const got = Object.fromEntries(Object.keys(want).map((k) => [k, stat(h, k)]));
  check(JSON.stringify(got) === JSON.stringify(want), `${grid} ${region}, ${x.run}, ${buy}, ${mw} MW: USD ${want.l12_per} per MWh over the last twelve months, USD ${want.l12_cost} in all, USD ${want.gpu_hour} per GPU-hour${want.l12_saved ? `, USD ${want.l12_saved} saved` : ""}${JSON.stringify(got) === JSON.stringify(want) ? "" : ` (the page says ${JSON.stringify(got)})`}`);
}
{
  // a region with no price in the market named: ERCOT's four municipal and cooperative load zones hold day-ahead only
  const short = index.grids.ercot.regions.find((r) => r.kind === "zone" && !r.rt && r.da);
  if (short) {
    const h = face((await get(`/cost-of-power?grid=ercot&region=${short.id}&buy=rt`)).html);
    check(/data-missing="1"/.test(h) && /title="No real time price is held[^"]*"/.test(h) && !/data-stat="l12_per"/.test(h), `a region with no real-time price (ERCOT ${short.id}) reads "not held yet" with its reason on hover, and no number`);
    const d = (await get(`/cost-of-power?grid=ercot&region=${short.id}`)).html;
    const sd = span(lastTwelve(monthsOf(files("ercot"), short.id, "da", { run: "flat", n: 0, pct: 0, shift: 0 })));
    check(stat(d, "l12_per") === two(sd.per) && /buying day-ahead/.test(plain(face(d))), `the same region with no market named shows its day-ahead price, USD ${two(sd.per)} per MWh`);
  } else check(false, "ERCOT holds a load zone with day-ahead prices only");
  const m = face((await get("/cost-of-power?grid=miso")).html);
  check(/<input[^>]*checked=""[^>]*value="ercot"|value="ercot"[^>]*checked=""/.test(m), "an address that names MISO opens the default grid, ERCOT");
  const q = JSON.parse(fs.readFileSync(new URL("../nyiso_load_queue.json", dir), "utf-8"));
  const nyh = (await get("/cost-of-power?grid=nyiso&region=CENTRL&buy=da")).html;
  if (q.shown === false) {
    // Session 149 (the owner's ruling of 7 October 2026: the rows are shown only if NYISO's terms allow it; by their
    // words they do not). Since session 213 the placeholder is the download's row, with the reason beside it, and the
    // waits New York's own copies measure are there too
    const TN = await tablesOf("?grid=nyiso");
    const line = cell(TN, "how_soon", "large_load_in_line", "mw");
    check(!!line && line.value === "" && line.note.startsWith(`${q.words}: ${q.why.slice(0, 60)}`) && TN.some((r) => r.table === "waits" && r.column === "measured_here" && r.value),
      `New York's load in line reads "${q.words}", with the reason beside it, and its waits are measured (the download, tables.csv)`);
    check(!("rows" in q) && !("zones" in q) && !("total" in q) && !/New York(&#x27;|')s load in line, request by request/.test(nyh) && !/data-nyload-zone=/.test(nyh),
      "no request, zone or megawatt of NYISO's load queue is on the page or in its file");
  } else check(false, "data/nyiso_load_queue.json says NYISO's rows may be shown: this check describes the page that does not show them (session 149)");
  const other = face((await get("/cost-of-power?grid=caiso")).html);
  check(/Delivery charges\s+not held yet/.test(plain(other)), 'another grid shows "delivery charges: not held yet"');
}
{
  // Texas: delivery by component (session 236), only what the tariffs state (session 265), and the tight hours
  const d = JSON.parse(fs.readFileSync(new URL("texas_delivery.json", dir), "utf-8"));
  const e = (await get("/cost-of-power?grid=ercot&run=hours&n=100")).html, et = plain(face(e));
  const TH = await tablesOf("?grid=ercot&run=hours&n=100");
  const utilities = utilitiesOf(d.rows);
  const oncor = deliveryOf(d.rows, "Oncor", 100).components.find((c) => c.kind === "transmission");
  const block = e.slice(e.indexOf('data-delivery="1"'), e.indexOf('data-delivery-note="1"'));
  const tips = titles(block).join(" || ");
  const inTotals = d.rows.filter((r) => conditionOf(r) !== "tariff");
  const firstT = /data-delivery-kind="transmission"[^>]*>[\s\S]*?data-check="dcd\|100\|oncor:transmission"[^>]*>([^<]*)</.exec(block)?.[1];
  check(utilities.length === 4 && d.withheld.length === 0 && et.includes(`Component ${utilities.join(" ")}`) && utilities.every((u) => block.includes(`data-delivery-total="${slugOf(u)}"`))
    && inTotals.every((r) => tips.includes(`${r.charge.trim()}:${r.value_as_written} ${r.unit}`)) && firstT === two(oncor.perMwh),
    `the four utilities are the columns of the delivery table (${utilities.join(", ")}); each figure's hover names the tariff lines it sums as printed (${inTotals.length} of ${d.rows.length}; the others apply only to some loads and are named under it); Oncor's transmission is USD ${two(oncor.perMwh)} per MWh for a flat 100 MW load (sessions 236 and 265)`);
  const lines = TH.filter((r) => r.table === "delivery" && r.column === "line_read"), docs = TH.filter((r) => r.table === "delivery" && r.column === "document");
  check(lines.length === d.rows.length && d.rows.every((r) => r.sentence && lines.some((l) => l.value.trim() === r.sentence.trim()) && docs.some((x) => x.note.includes(r.url) && x.note.includes(`page ${r.page}`) && x.note.includes(String(r.effective)))),
    `every tariff line (${d.rows.length}) carries the line it was read from, its page, its date and its address, in the download's table "delivery" (session 236: none is on the page)`);
  check(utilities.every((u) => ["transmission", "distribution"].every((k) => d.rows.some((r) => r.utility === u && kindOf(r) === k))) && (e.match(/data-delivery-kind="transmission"/g) ?? []).length === 4
    && (e.match(/data-delivery-kind="distribution"/g) ?? []).length === 4, "each utility's row shows transmission and distribution apart");
  const rate = d.matrix.find((r) => r.quantity === "postage_stamp_rate" && r.year === "2025");
  const rateTip = attrs(/<a[^>]*data-matrix-rate="2025"[^>]*>/.exec(e)?.[0] ?? "").title ?? "";
  const perMwh = two((rate.value * 1000) / 8760);
  check(/data-matrix="1"/.test(e) && new RegExp(`2025\\s*:\\s*USD ${perMwh.replace(".", "\\.")} per MWh, a flat load\\s+approved`).test(et) && /2026\s*:\s*USD [\d.,]+ per MWh, a flat load\s+filed, not approved/.test(et)
    && rateTip.startsWith(`USD ${rate.value.toFixed(6)} per kW of four-peak demand a year, as printed`) && rateTip.includes(rate.sentence.slice(0, 30)),
    `the Commission's wholesale transmission rate is a row of its own: USD ${perMwh} per MWh for a flat load in 2025 (approved), USD ${rate.value.toFixed(6)} per kW a year as printed on hover with its line (session 236); 2026 is marked filed, not approved`);
  const E = index.grids.ercot, yrs = Object.keys(E.demand).filter((y) => E.demand[y].whole && E.demand[y].tight_hours !== undefined).sort(), y = yrs.at(-1);
  const f = files("ercot").find((k) => String(k.year) === y);
  const X100 = { run: "hours", n: 100, pct: 0, shift: 0 }, main = E.main;
  const ruled = monthsRuled(files("ercot"), main, "rt", X100, "forecast"), p = ruled.prices.get(Number(y)), w = ruled.weights.get(Number(y));
  const off = f.tight.filter((i) => p[i] !== null && w[i] === 0).length;
  const tight = cell(TH, "power_there", `hours_tight_${y}`, "hours"), offIn = cell(TH, "power_there", `hours_tight_${y}`, "this_load_off_in");
  check(Number(tight?.value) === E.demand[y].tight_hours && tight.value !== "" && Number(offIn?.value) === off && offIn.value !== "",
    `ERCOT was tight in ${E.demand[y].tight_hours} hours of ${y} (the file's count), and a load off in the year's 100 dearest hours was off in ${off} of them (the download)${tight ? "" : " (no row)"}`);
  const zones = TH.filter((r) => r.table === "power_there" && r.row.startsWith("demand_by_region_") && r.column === "change_pct" && r.value !== "");
  check(zones.length === 8 && zones.some((r) => r.row === "demand_by_region_FWEST"), `demand by region: ERCOT's eight weather zones, each with its growth (the download: ${zones.length})`);
  // session 140: the hub beside the load zone, the foreseen row
  const region = E.regions.find((r) => r.id === main);
  const l12 = lastTwelve(ruled.months), refMs = monthsOf(files("ercot"), region.ref, "rt", { run: "flat", n: 0, pct: 0, shift: 0 }).filter((r) => r.m >= l12[0].m && r.m <= l12[11].m);
  const refHub = /data-ref-hub="1"[^>]*>([^<]*)</.exec(e)?.[1];
  check(region.kind === "zone" && refHub === two(span(refMs).flat) && et.includes(`The hub beside it, ${region.ref}, a flat load`), `ERCOT's default region is a load zone (${main}); its trading hub ${region.ref} stands beside it at USD ${two(span(refMs).flat)} per MWh over the same twelve months`);
  const hind = span(lastTwelve(monthsRuled(files("ercot"), main, "rt", X100, "hindsight").months));
  check(new RegExp(`This load, if perfectly foreseen\\s+${two(hind.per).replace(".", "\\.")}`).test(et) && /title="[^"]*8th dearest hourly day-ahead price of the prior 30 days[^"]*"/.test(e) && !/8th dearest/.test(et),
    `the same load if perfectly foreseen (USD ${two(hind.per)}) stands beside the forecast figure; the rule is stated on hover and not on the face`);
  // the load's own hours against the grid's carbon-free share: the download's row (session 213), the library's figure
  const own = TH.find((r) => r.table === "how_clean" && /^this_loads_own_hours_\d{4}$/.test(r.row) && r.column === "pct");
  const cyear = own ? Number(own.row.slice(-4)) : NaN;
  const cf = files("ercot").find((k) => k.year === cyear);
  const lib = cf ? cleanShare(expandSeries(cf.clean, cf.hours), ruled.prices.get(cyear), ruled.weights.get(cyear)) : null;
  check(!!lib && own.value === two(lib.load) && own.note.includes(`a flat load over the same hours ${two(lib.flat)}`),
    `this load's own hours met ${lib ? two(lib.load) : "?"} percent carbon-free generation in ${cyear} (a flat load over the same hours: ${lib ? two(lib.flat) : "?"}), in the download${lib && own.value !== two(lib.load) ? ` (the download says ${own.value})` : ""}`);
  const TI = await tablesOf("?grid=isone&buy=da");
  const neT = cell(TI, "power_there", "hours_tight", "hours"), neD = cell(TI, "power_there", "demand_by_region", "average_mw");
  check(!!neT && !!neD && neT.value === "" && neD.value === "" && [neT, neD].every((r) => /held internally and nothing of it is shown/.test(r.note)) && !("demand" in index.grids.isone && Object.keys(index.grids.isone.demand).length),
    "ISO-NE's demand is held internally: the download's rows say so and state no figure, and the site's files hold none of it");
  const TS = await tablesOf("?grid=spp");
  const spT = cell(TS, "power_there", "hours_tight", "hours");
  check(!!spT && spT.value === "" && /not held for SPP/.test(spT.note), "SPP, whose hourly demand was not pulled: its tight hours are not counted, and the download says so");
}
{
  const g = await get("/cost-of-power?view=grids");
  const t = plain(face(g.html));
  check(g.status === 200 && ["Load-weighted real-time price by ISO", "ERCOT since 2018", "When is power cheap", "Cost against carbon", "The compute calculator", "Your own inputs"].every((w) => t.includes(w)) && /data-check="cop\|flat_cost\|/.test(g.html),
    "the view Grid by grid holds what the tab showed before: the ranking, ERCOT since 2018, the hours of the day, cost against carbon and the calculator");
  const v = await get("/cost-of-power", false);
  check(!v.html.includes('data-summary="1"') && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page");
}

// ---------------------------------------------------------------------------------------------------------------------
// The rules in motion (session 154's block; since session 228 a count in "How soon?" and the rows in the download)
// ---------------------------------------------------------------------------------------------------------------------
const rulesAt = new URL("rules.json", dir);
const RULES = fs.existsSync(rulesAt) ? fileOf(JSON.parse(fs.readFileSync(rulesAt, "utf-8"))) : null;
const NAMES = { ...Object.fromEntries(Object.entries(index.blank).map(([k, v]) => [k, v.name])), ...Object.fromEntries(Object.entries(index.grids).map(([k, v]) => [k, v.name])) };
const RULE_PAGES = {};
let municipalFound = "";
for (const g of RULE_GRIDS) {
  const r = await get(`/cost-of-power?grid=${g}`);
  RULE_PAGES[g] = r.html;
  const want = blockOf(RULES, g), t = plain(face(r.html));
  // the count stands in the row "Rules in motion for a large load" where the grid has large load reports, else as a sentence
  const said = /\d+ proceedings and orders on large loads are in motion for [^.]*?each is in the download, with its document|No proceeding or order on large loads is held[^.]*|paused while terms are reviewed/.exec(t)?.[0] ?? "";
  const TG = await tablesOf(`?grid=${g}`);
  const ids = [...new Set(TG.filter((x) => x.table === "rules").map((x) => x.row))].filter((x) => x !== "file" && x !== "state").sort();
  // the download names a row by its group: the grid's name or "federal", then the file's id
  const strip = (x) => x.replace(/^(federal|[A-Z][A-Z_-]*)_(?=[a-z])/, "");   // "ERCOT_txpuc:...", "ISO_NE_ferc:...", "federal_ferc:..."
  const got = JSON.stringify([ids.filter((x) => !x.startsWith("federal_")).map(strip).sort(), ids.filter((x) => x.startsWith("federal_")).map(strip).sort()]);
  const fileIds = JSON.stringify([want.rows.map((x) => String(x.id)).sort(), want.federal.map((x) => String(x.id)).sort()]);
  let ok, what;
  if (want.state === "paused") {
    ok = r.status === 200 && t.includes(`Rules in motion for a large load 0 ${PAUSED_WORDS}`) && ids.length === 0 && cell(TG, "rules", "state", "words")?.value === PAUSED_WORDS;
    what = `${NAMES[g]}: "How soon?" counts no rule and reads "${PAUSED_WORDS}"; the download holds no row of it`;
  } else if (want.state === "shown" && want.rows.length) {
    const newest = want.rows[0];
    ok = r.status === 200 && t.includes(`${want.rows.length} proceedings and orders on large loads are in motion for ${NAMES[g]} in the public dockets held, the newest `)
      && t.includes(`(${newest.date}); each is in the download, with its document`) && got === fileIds;
    what = `${NAMES[g]}: "How soon?" counts the file's ${want.rows.length} rows, the newest of ${newest.date}; the download's table "rules" holds exactly the file's ${want.rows.length} rows and ${want.federal.length} federal (${ids.length})`;
  } else {
    ok = r.status === 200 && /Rules in motion for a large load 0 No proceeding or order on large loads is held/.test(t) && got === fileIds;
    what = `${NAMES[g]}: "How soon?" counts no row of its own (the file's state: ${want.state}), and the download holds the federal rows alone (${ids.length})`;
  }
  check(ok, what);
  const hit = MUNICIPAL.find((w) => said.toLowerCase().includes(w));
  if (hit) municipalFound += ` ${g}: "${hit}"`;
}
check(!municipalFound, `the count's line holds none of the words ${MUNICIPAL.map((w) => `"${w}"`).join(", ")} for any of the seven addresses${municipalFound ? ` (found:${municipalFound})` : ""}`);
{
  // session 265: an address that names a grid the page does not hold says so in one line and shows the default grid;
  // the rules count follows the grid the address names (session 228). Outside those two the page is the default's.
  const outside = (h) => plain(face(h)).replace(/Grid: "[a-z]+" is not held here, so ERCOT is shown\.?/, " ")
    .replace(/Rules in motion for a large load .*?(each is in the download, with its document\.?|paused while terms are reviewed\.?|in the public dockets read\.?)/, " ").replace(/\s+/g, " ");
  const pjm = RULE_PAGES.pjm ?? "", miso = RULE_PAGES.miso ?? "";
  check(outside(pjm) === outside(page.html) && /Grid: "pjm" is not held here, so ERCOT is shown/.test(plain(face(pjm))) && /data-grid="pjm"[^>]*data-open="0"[\s\S]{0,400}?licensed source needed/.test(pjm),
    'an address that names PJM says "Grid: "pjm" is not held here, so ERCOT is shown", and outside that line and the rules count shows what the default address shows; PJM\'s prices still read "licensed source needed"');
  check(outside(miso) === outside(page.html) && /Grid: "miso" is not held here, so ERCOT is shown/.test(plain(face(miso))),
    "an address that names MISO says so in one line, and outside that line and the rules count shows what the default address shows");
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, send, errors, sleep }) => {
  await open(base);
  await go(`${base}/cost-of-power?grid=ercot&run=hours&n=100`);
  // session 317: the chart is the shared SVG set's (components/svgchart.tsx); its card answers the mouse
  await wait(`!!document.querySelector('[data-year-cost] svg text')`, 40000, "the chart");
  await sleep(2000);   // the page hydrates before the chart answers the mouse
  const at = await evaluate(`(() => { const s = document.querySelector('[data-year-cost] svg'); s.scrollIntoView({ block: 'center', behavior: 'instant' });
    const label = [...s.querySelectorAll('text')].find((t) => t.textContent === '2021'); if (!label) return null;
    const r = s.getBoundingClientRect(), k = r.width / s.viewBox.baseVal.width;
    return { x: r.left + Number(label.getAttribute('x')) * k, y: r.top + r.height / 2 }; })()`);
  let tip = "";
  if (at) {
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: at.x, y: at.y });
    await sleep(400);
    tip = await evaluate(`document.querySelector('[data-year-cost] [data-chart-card]')?.innerText ?? ''`);
  }
  const t1 = tip.replace(/\s+/g, " ");
  check(/2021/.test(t1) && /Flat load: [\d,.]+ USD\/MWh/.test(t1) && /This load: [\d,.]+ USD\/MWh/.test(t1) && /off in [\d,]+ hours/.test(t1) && /If perfectly foreseen: [\d,.]+ USD\/MWh/.test(t1),
    `the chart answers the mouse with the year, the load under the rule and the load if perfectly foreseen ("${t1.slice(0, 190)}")`);
  check(await evaluate(`[...document.querySelectorAll('[data-region] optgroup')].map((o) => o.label).join('|').includes('Load zones')`), "ERCOT's regions are listed as load zones, then trading hubs");
  await sleep(1500);
  await evaluate(`document.querySelector('[data-grid="caiso"] input').click()`);
  await wait(`location.search.includes('grid=caiso') && [...document.querySelectorAll('[data-region] option')].some((o) => o.value.includes('SP15'))`, 20000, "CAISO's regions");
  check(!(await evaluate(`[...document.querySelectorAll('[data-region] option')].some((o) => o.value.startsWith('HB_'))`)), "choosing another grid opens it with its own regions");
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
