// Energy Research Warehouse (ERW) site, session 138: "What a datacenter pays" (/cost-of-power), on the built site.
//
//   npm run build && npx next start -p 3138
//   node scripts/check-datacenter.mjs [base-url]      (default http://localhost:3138)
//
// As HTML, in the internal view (the page is in review):
//   opens      200, its title, the three tabs, the four questions, no "undefined", no NaN; it names its Method note
//   numbers    the summary sentence's figures equal the arithmetic of lib/datacenter.ts over the site's own files, for
//              a flat load, a load off in 100 hours a year bought day-ahead, and a shifting load in California
//   uneven     a region with no price in the market named reads "not held yet" with its reason on hover, and no number
//   forecast   (session 140) a flexible load's figures are the forecast rule's (lib/datacenter.ts monthsRuled), with the
//              same load "if perfectly foreseen" beside them; a load zone shows its trading hub beside it; the load's
//              own hours against the grid's carbon-free share are the library's figure
//   new york   (session 140) New York's load in line by zone, from NYISO's queue workbook, and request by request
//   blank      MISO reads "paused while terms are reviewed" and PJM "licensed source needed", neither selectable; an
//              address that names one opens the default grid
//   nowhere    large load in line by region, and how long a new large load waits: "not published anywhere yet"
//   delivery   Texas (session 140, the owner's ruling): the four wires utilities' charges, each a row of its own with
//              transmission and distribution apart, each charge as the tariff prints it with its line; the Commission's
//              wholesale transmission rate as a row of its own; another grid "not held yet"
//   there      ERCOT's tight hours are the file's count, and the hours a flexible load was off in are the library's;
//              ISO-NE's demand, held internally, reads "licensed source needed"; SPP's "not held yet"
//   view       ?view=grids is what the tab showed before: its ranking, ERCOT since 2018, the hours of the day, cost
//              against carbon and the calculator
//   visitor    without the cookie the page is the in-review page
//   rules      (session 154) "Rules in motion" in the section "How soon", for each of the seven grids an address can name:
//              the block is there; every row shown is a row of data/datacenter/rules.json in the order of lib/rules.ts,
//              with its date, its status, a link whose address is the file's and whose hover holds the file's sentence
//              (or, where the file does not copy a regulator's text, the file's phrase in its place and the status's
//              class: never neither, never a sentence the file does not hold),
//              and a read marked as a model's or the placeholder "no read yet"; eight rows of a group stand before its
//              fold; MISO shows the fixed words and no row; PJM shows the file's rows, and the rest of its address is
//              what the default address shows; the block holds no municipal word, on its face or on hover; its face
//              holds no sentence of the Method note. Before the file exists the block reads "not held yet".
// In a real browser: the chart is drawn and answers the mouse with the year and its figures; the contract's terms make
// no request, leave the address as it was, write nothing to storage or cookies, and show the result; choosing another
// grid opens that grid with its own regions. Session 154: the rows of "Rules in motion" carry the file's address and
// sentence in the page as the browser holds it, a row's link takes the keyboard's focus, and a fold opens to a real
// click and to the Enter key.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { cleanShare, expandSeries, gpuHour, lastTwelve, monthsOf, monthsRuled, span, two, usdShort } from "../lib/datacenter.ts";
import { MUNICIPAL, NO_READ, NO_READ_WHY, PAUSED_WORDS, PAUSE_WHY, RULE_GRIDS, SHOWN, blockOf, dayWords, docketTip, docketWords, fileOf, linkOf, readOf, statusOf } from "../lib/rules.ts";

const base = (process.argv[2] ?? "http://localhost:3138").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const dir = new URL("../data/datacenter/", import.meta.url);
const index = JSON.parse(fs.readFileSync(new URL("index.json", dir), "utf-8"));
const files = (g) => index.grids[g].years.map((y) => JSON.parse(fs.readFileSync(new URL(`${g}_${y}.json`, dir), "utf-8")));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
const stat = (html, k) => new RegExp(`data-stat="${k}"[^>]*>([^<]*)<`).exec(html)?.[1] ?? null;

const page = await get("/cost-of-power");
const html = face(page.html), text = plain(html);
check(page.status === 200 && text.includes("What a datacenter pays") && !/\bundefined\b|NaN/.test(text), '/cost-of-power opens as "What a datacenter pays", with no "undefined" and no NaN');
check(["What a datacenter pays", "What a generator earns", "What a battery earns"].every((t) => plain(/<nav[^>]*aria-label="Cost of power"[\s\S]*?<\/nav>/.exec(page.html)?.[0] ?? "").includes(t)), "the three tabs: What a datacenter pays, What a generator earns, What a battery earns");
check(["What will it cost", "Will the power be there", "How clean", "How soon"].every((t) => html.includes(`>${t}</h2>`)), "the four questions are four sections");
check(page.html.includes("/data/methods/datacenter_cost") && !/upper bound|Wholesale energy only|cannot see|limitation/i.test(text), "the page names its Method note and carries no method prose on its face");
check(/data-grid="miso"[^>]*data-open="0"[\s\S]{0,400}?paused while terms are reviewed/.test(html) && /data-grid="pjm"[^>]*data-open="0"[\s\S]{0,400}?licensed source needed/.test(html)
  && /<input[^>]*disabled=""[^>]*value="miso"|value="miso"[^>]*disabled=""/.test(html), 'MISO reads "paused while terms are reviewed" and PJM "licensed source needed"; neither can be chosen');
check(["ercot", "caiso", "nyiso", "isone", "spp"].every((g) => new RegExp(`data-grid="${g}"[^>]*data-open="1"`).test(html)), "the five public grids can each be chosen");
check((text.match(/not published anywhere yet/g) ?? []).length === 2 && /Large load in line, by region\s+not published anywhere yet/.test(text) && /How long a new large load waits\s+not published anywhere yet/.test(text),
  'large load in line by region, and how long a new large load waits, read "not published anywhere yet"');

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
  const ny = plain(face((await get("/cost-of-power?grid=nyiso")).html));
  const q = JSON.parse(fs.readFileSync(new URL("../nyiso_load_queue.json", dir), "utf-8"));
  const nyh = (await get("/cost-of-power?grid=nyiso&region=CENTRL&buy=da")).html;
  if (q.shown === false) {
    // Session 149 (the owner's ruling of 7 October 2026: the rows are shown only if NYISO's terms allow it; by their
    // words they do not): the megawatts in line and the fold of requests have left the face; a placeholder with its
    // reason on hover stands where they stood, and the page's file holds no request
    check(/data-nyload-held="1"/.test(nyh) && !/data-nyload="1"/.test(nyh) && plain(nyh).includes(`Large load in line, by region ${q.words}`)
      && nyh.includes(`title="${q.why.replace(/'/g, "&#x27;")}"`) && /How long a new large load waits\s+not published anywhere yet/.test(ny),
      `New York's load in line reads "${q.words}", with the reason on hover`);
    check(!("rows" in q) && !("zones" in q) && !("total" in q) && !/New York(&#x27;|')s load in line, request by request/.test(nyh) && !/data-nyload-zone=/.test(nyh),
      "no request, zone or megawatt of NYISO's load queue is on the page or in its file");
  } else {
    const mine = q.zones.find((z) => z.zone_name === "CENTRL");
    check(/data-nyload="1"/.test(nyh) && new RegExp(`${mine.mw.toLocaleString("en-US")} MW in ${mine.requests} requests in CENTRL`).test(plain(nyh)) && new RegExp(`${q.total.mw.toLocaleString("en-US")} MW in ${q.total.requests} requests in New York`).test(plain(nyh))
      && q.zones.every((z) => nyh.includes(`data-nyload-zone="${z.zone_name}"`)) && /How long a new large load waits\s+not published anywhere yet/.test(ny),
      `New York's load in line by zone is NYISO's own list: ${mine.mw.toLocaleString("en-US")} MW in ${mine.requests} requests in CENTRL, ${q.total.mw.toLocaleString("en-US")} MW in ${q.total.requests} in all, each zone with its statuses and its source on hover`);
    const inLine = q.rows.filter((r) => r.in_line);
    check(inLine.length === q.total.requests && inLine.every((r) => nyh.includes(`>${r.queue_position}</a>`)) && nyh.includes(q.source.url), `the ${inLine.length} requests in line are listed one by one, each linked to NYISO's workbook with its sheet and row on hover`);
  }
  const other = face((await get("/cost-of-power?grid=caiso")).html);
  check(/Delivery charges\s+not held yet/.test(plain(other)), 'another grid shows "delivery charges: not held yet"');
}
{
  // Texas: delivery as rows of its own, shown only where the utility's terms allow, and the tight hours
  const d = JSON.parse(fs.readFileSync(new URL("texas_delivery.json", dir), "utf-8"));
  const e = (await get("/cost-of-power?grid=ercot&run=hours&n=100")).html, et = plain(face(e));
  const utilities = [...new Set(d.rows.map((r) => r.utility))];
  const tcrf = d.rows.find((r) => r.utility === "Oncor" && /TCRF/.test(r.charge));
  const per = two((tcrf.value * 12000) / 8760);
  check(utilities.length === 4 && d.withheld.length === 0 && utilities.every((u) => new RegExp(`Delivery and transmission, ${u}`).test(et)) && et.includes(`The transmission factor alone, a flat load: USD ${per} per MWh`)
    && d.rows.every((r) => e.includes(r.value_as_written.replace(/^\$\s*/, "").replace(/^\(\s*\$?\s*/, "("))),
    `the four utilities' ${d.rows.length} delivery charges are rows of their own (${utilities.join(", ")}), each as the tariff prints it; Oncor's transmission factor alone is USD ${per} per MWh for a flat load`);
  check(d.rows.every((r) => r.sentence && r.url.startsWith("http") && r.page && r.effective && e.includes(r.sentence.slice(0, 30).replace(/&/g, "&amp;").replace(/"/g, "&quot;"))), "every charge shown carries the line it was read from, its page, its date and its address");
  check(utilities.every((u) => ["transmission", "distribution"].every((k) => d.rows.some((r) => r.utility === u && r.kind === k))) && (e.match(/data-delivery-kind="transmission"/g) ?? []).length === 4
    && (e.match(/data-delivery-kind="distribution"/g) ?? []).length === 4, "each utility's row shows transmission and distribution apart");
  const rate = d.matrix.find((r) => r.quantity === "postage_stamp_rate" && r.year === "2025");
  check(/data-matrix="1"/.test(e) && et.includes(`2025: USD ${rate.value.toFixed(6)} per kW of four-peak demand a year`) && et.includes(`USD ${two((rate.value * 1000) / 8760)} per MWh, a flat load`) && /filed, not approved/.test(et)
    && e.includes(rate.sentence.slice(0, 30)), `the Commission's wholesale transmission rate is a row of its own: USD ${rate.value.toFixed(6)} per kW a year in 2025 (approved), USD ${two((rate.value * 1000) / 8760)} per MWh for a flat load; 2026 is marked filed, not approved`);
  const E = index.grids.ercot, yrs = Object.keys(E.demand).filter((y) => E.demand[y].whole && E.demand[y].tight_hours !== undefined).sort(), y = yrs.at(-1);
  const f = files("ercot").find((k) => String(k.year) === y);
  const X100 = { run: "hours", n: 100, pct: 0, shift: 0 }, main = E.main;
  const ruled = monthsRuled(files("ercot"), main, "rt", X100, "forecast"), p = ruled.prices.get(Number(y)), w = ruled.weights.get(Number(y));
  const off = f.tight.filter((i) => p[i] !== null && w[i] === 0).length;
  check(new RegExp(`Hours the grid was tight, ${y}\\s+${E.demand[y].tight_hours} hours`).test(et) && new RegExp(`this load was off in\\s+${off} of ${E.demand[y].tight_hours}`).test(et),
    `ERCOT was tight in ${E.demand[y].tight_hours} hours of ${y} (the file's count), and a load off in the year's 100 dearest hours was off in ${off} of them`);
  check(/data-zone="FWEST"/.test(e) && /Demand by region[\s\S]{0,200}FWEST \+/.test(et), "demand by region: ERCOT's eight weather zones, each with its growth");
  // session 140: the hub beside the load zone, the foreseen row, and the load's own hours against clean generation
  const region = E.regions.find((r) => r.id === main);
  const l12 = lastTwelve(ruled.months), refMs = monthsOf(files("ercot"), region.ref, "rt", { run: "flat", n: 0, pct: 0, shift: 0 }).filter((r) => r.m >= l12[0].m && r.m <= l12[11].m);
  const refHub = /data-ref-hub="1"[^>]*>([^<]*)</.exec(e)?.[1];
  check(region.kind === "zone" && refHub === two(span(refMs).flat) && et.includes(`The hub beside it, ${region.ref}, a flat load`), `ERCOT's default region is a load zone (${main}); its trading hub ${region.ref} stands beside it at USD ${two(span(refMs).flat)} per MWh over the same twelve months`);
  const hind = span(lastTwelve(monthsRuled(files("ercot"), main, "rt", X100, "hindsight").months));
  check(new RegExp(`This load, if perfectly foreseen\\s+${two(hind.per).replace(".", "\\.")}`).test(et) && /title="[^"]*8th dearest hourly day-ahead price of the prior 30 days[^"]*"/.test(e) && !/8th dearest/.test(et),
    `the same load if perfectly foreseen (USD ${two(hind.per)}) stands beside the forecast figure; the rule is stated on hover and not on the face`);
  const cy = /data-stat="own_clean"[^>]*>([^<]*)</.exec(e)?.[1];
  const cyear = Number(/hours of (\d{4}) in which the price and the share are both held/.exec(e)?.[1]);
  const cf = files("ercot").find((k) => k.year === cyear);
  const own = cf ? cleanShare(expandSeries(cf.clean, cf.hours), ruled.prices.get(cyear), ruled.weights.get(cyear)) : null;
  check(own && cy === two(own.load) && et.includes(`against ${two(own.flat)} for a flat load`), `this load's own hours met ${own ? two(own.load) : "?"} percent carbon-free generation in ${cyear} (a flat load over the same hours: ${own ? two(own.flat) : "?"})${own && cy !== two(own.load) ? ` (the page says ${cy})` : ""}`);
  const ne = plain(face((await get("/cost-of-power?grid=isone&buy=da")).html));
  check(/Hours the grid was tight\s+licensed source needed/.test(ne) && /Demand by region\s+licensed source needed/.test(ne) && !("demand" in index.grids.isone && Object.keys(index.grids.isone.demand).length),
    'ISO-NE\'s demand is held internally: its rows read "licensed source needed" and the site\'s files hold none of it');
  const sp = plain(face((await get("/cost-of-power?grid=spp")).html));
  check(/Hours the grid was tight\s+not held yet/.test(sp), 'SPP, whose hourly demand was not pulled, reads "not held yet"');
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
// session 154: "Rules in motion", read against the one file the block reads
// ---------------------------------------------------------------------------------------------------------------------
const rulesAt = new URL("rules.json", dir);
const RULES = fs.existsSync(rulesAt) ? fileOf(JSON.parse(fs.readFileSync(rulesAt, "utf-8"))) : null;
const NAMES = { ...Object.fromEntries(Object.entries(index.blank).map(([k, v]) => [k, v.name])), ...Object.fromEntries(Object.entries(index.grids).map(([k, v]) => [k, v.name])) };
const decode = (t) => t.replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16))).replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d))).replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const attrs = (tag) => Object.fromEntries([...tag.matchAll(/([a-zA-Z_:-]+)="([^"]*)"/g)].map((m) => [m[1], decode(m[2])]));
const firstTag = (h, re) => { const m = h.match(re); return m ? attrs(m[0]) : {}; };
const words = (h) => decode(h.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
/** The block's HTML: from its own element to the end of the section "How soon", of which it is the last part. */
const blockOfPage = (h) => { const i = h.indexOf('data-rules="1"'); if (i < 0) return null; const from = h.lastIndexOf("<div", i), to = h.indexOf("</section>", i); return h.slice(from, to < 0 ? undefined : to); };
/** The heading of the section the block stands in. */
const lastHeading = (f) => { const pre = f.slice(0, f.indexOf('data-rules="1"')); return words(pre.slice(pre.lastIndexOf("<h2")).match(/<h2[^>]*>[\s\S]*?<\/h2>/)?.[0] ?? ""); };
const norm = (t) => String(t).replace(/\s+/g, " ").trim();
/** The page's face outside the block, as text. */
const outside = (h) => { const f = face(h), b = blockOfPage(f); return plain(b ? f.replace(b, " ") : f); };
/** The rows the block shows, in the page's order: what a reader sees and what each hover says. */
function rowsOfPage(b) {
  const out = [];
  for (const m of b.matchAll(/<span[^>]*\bdata-rule="[^"]*"[^>]*>/g)) {
    const a = attrs(m[0]);
    const end = b.indexOf("</tr>", m.index), row = b.slice(m.index, end < 0 ? undefined : end);
    const cells = row.split(/<\/t[hd]>/);
    const linkTag = cells[2]?.match(/<a[^>]*\bdata-rule-link="[^"]*"[^>]*>/), link = linkTag ? attrs(linkTag[0]) : null;
    const linkWords = linkTag ? words(cells[2].slice(linkTag.index + linkTag[0].length, cells[2].indexOf("</a>", linkTag.index))) : null;
    const mark = firstTag(cells[3] ?? "", /<span[^>]*\bdata-rule-mark="model"[^>]*>/), gap = firstTag(cells[3] ?? "", /<span[^>]*\bdata-missing="1"[^>]*>/);
    out.push({ id: a["data-rule"], group: a["data-rule-group"], date: a["data-rule-date"], dateWords: words(cells[0] ?? ""), status: words(cells[1] ?? ""), linkId: link?.["data-rule-link"] ?? null, hover: link?.["data-rule-hover"] ?? null, href: link?.href ?? null, tip: link?.title ?? null, linkWords,
      read: words(cells[3] ?? ""), marked: "data-rule-mark" in mark, markTip: mark.title ?? null, gapTip: gap.title ?? null, folded: b.lastIndexOf("<details", m.index) > b.lastIndexOf("</details>", m.index) });
  }
  return out;
}
const RULE_PAGES = {};
let noMunicipal = true, municipalFound = "", foldsRight = true, shownTotal = 0, foldGrid = null, rowsWrong = 0;
const hovers = { sentence: 0, withheld: 0, neither: 0 };
for (const g of RULE_GRIDS) {
  const r = await get(`/cost-of-power?grid=${g}`);
  const b = blockOfPage(face(r.html));
  RULE_PAGES[g] = r.html;
  const want = blockOf(RULES, g), expect = [...want.rows.map((x) => ({ x, group: "grid" })), ...want.federal.map((x) => ({ x, group: "federal" }))];
  if (!b) { check(false, `${NAMES[g]}: the block "Rules in motion" is in the section "How soon"`); continue; }
  const head = attrs(b.slice(0, b.indexOf(">") + 1)), got = rowsOfPage(b), text = words(b);
  const there = r.status === 200 && head["data-rules-for"] === g && head["data-rules-state"] === want.state && words(b.match(/<h3[^>]*>[\s\S]*?<\/h3>/)?.[0] ?? "").replace(/ ,/g, ",") === `Rules in motion, ${NAMES[g]}`
    && RULE_GRIDS.every((k) => b.includes(`data-rules-choice="${k}"`)) && lastHeading(face(r.html)) === "How soon";
  const wrong = [];
  if (!there) wrong.push(`the block is not as the file says (for ${head["data-rules-for"]}, state ${head["data-rules-state"]}; the file gives ${want.state}), or its heading, its seven choices or its section is not`);
  if (got.length !== expect.length) wrong.push(`${got.length} rows on the page, ${expect.length} in the file`);
  expect.forEach(({ x, group }, i) => {
    const p = got[i], st = statusOf(x), rd = readOf(x);
    if (!p || p.id !== String(x.id) || p.group !== group) { if (wrong.length < 4) wrong.push(`row ${i + 1} is ${p?.id ?? "missing"}, not ${x.id}`); return; }
    const bad = [];
    if (p.dateWords !== (dayWords(x.date) ?? "not stated")) bad.push("date");
    if (!st.words || p.status !== norm(st.words)) bad.push("status");
    if (p.linkId !== p.id || p.href !== x.url || p.href !== linkOf(x) || p.linkWords !== norm(docketWords(x))) bad.push("link");
    // the docket's hover leads with the file's sentence, in quotes, or, where the file does not copy the regulator's text,
    // with the file's phrase in its place; after it stand only the page, the topic and the tags as the file has them:
    // never neither, and never a sentence the file does not hold
    const s = typeof x.sentence === "string" ? x.sentence.trim() : "", w = typeof x.sentence_withheld === "string" ? x.sentence_withheld.trim() : "";
    const lead = s ? `"${s}"` : w, after = lead && typeof p.tip === "string" && p.tip.startsWith(lead) ? p.tip.slice(lead.length).replace(/^\.?\s*/, "") : null;
    const tail = [s && x.sentence_from ? `Sentence from: ${x.sentence_from}.` : "", x.page !== null && x.page !== undefined && String(x.page).trim() ? `Page ${String(x.page).trim()} of the document.` : "", x.topic ? `Topic: ${x.topic}.` : "",
      Array.isArray(x.tags) && x.tags.length ? `Tags: ${x.tags.join(", ")}.` : ""].filter(Boolean).join(" ");
    if (!lead) bad.push("neither a sentence nor the phrase in its place");
    else if (after !== tail || p.tip !== docketTip(x) || p.hover !== (s ? "sentence" : "withheld")) bad.push(s ? "sentence on hover" : "the phrase in place of the sentence on hover");
    if (!s && w && (p.status !== (["open", "decided", "closed"].includes(x.status_class) ? x.status_class : "not stated") || (x.status_as_worded && p.status === norm(x.status_as_worded)))) bad.push("the status's class in place of its wording");
    hovers[s ? "sentence" : w ? "withheld" : "neither"] += 1;
    if (rd.line ? !(p.marked && p.read === `${norm(rd.line)} model's read` && p.markTip === rd.why && x.read_by === "model") : !(p.read === NO_READ && !p.marked && p.gapTip === NO_READ_WHY)) bad.push("read");
    if (bad.length) rowsWrong += 1;
    if (bad.length && wrong.length < 4) wrong.push(`${x.id}: ${bad.join(", ")}`);
  });
  // the fold: eight rows of a group stand before it, the rest inside it
  for (const group of ["grid", "federal"]) {
    const all = got.filter((p) => p.group === group), open = all.filter((p) => !p.folded).length;
    if (open !== Math.min(all.length, SHOWN) || (all.length > SHOWN) !== b.includes(`data-rules-fold="${group}"`)) foldsRight = false;
    if (all.length > SHOWN && !foldGrid) foldGrid = { g, group, folded: all.length - SHOWN };
  }
  shownTotal += got.length;
  const withRead = expect.filter(({ x }) => readOf(x).line).length;
  const gapTip = firstTag(b, /<span[^>]*\bdata-missing="1"[^>]*>/).title;
  if (g === "miso") {
    check(there && want.state === "paused" && got.length === 0 && !/<table|<details|data-rule=/.test(b) && /data-rules-paused="1"/.test(b) && text.endsWith(PAUSED_WORDS) && gapTip === PAUSE_WHY,
      `MISO: the block reads "${PAUSED_WORDS}", with the pause's reason on hover, and shows no row, federal ones included`);
  } else if (want.state === "shown") {
    check(!wrong.length, `${NAMES[g]}: ${want.rows.length} rows and ${want.federal.length} federal, newest first, each with its date, its status, a link to the file's address with the file's sentence on hover, and a read marked as a model's (${withRead}) or "${NO_READ}" (${expect.length - withRead})${wrong.length ? `: ${wrong.join("; ")}` : ""}`);
  } else {
    check(!wrong.length && b.includes(`data-rules-empty="${want.state}"`) && text.includes(want.state === "none" ? want.words : "not held yet") && !!gapTip && (want.state !== "none" || gapTip === want.why),
      `${NAMES[g]}: ${want.state === "none" ? `no row of its own ("${want.words}", with the file's reason on hover)` : `"not held yet" with its reason on hover (${RULES ? "the file holds no entry for it" : "data/datacenter/rules.json is not there yet"})`}${RULES ? `, and ${want.federal.length} federal rows (${withRead} with a read marked as a model's)` : ""}${wrong.length ? `: ${wrong.join("; ")}` : ""}`);
  }
  // no municipal word in anything the block shows: its text and every hover (an address is not a word of the block)
  const said = `${text} ${[...b.matchAll(/\btitle="([^"]*)"/g)].map((m) => decode(m[1])).join(" ")}`.toLowerCase().replace(/\s+/g, " ");
  const hit = MUNICIPAL.find((w) => said.includes(w));
  if (hit) { noMunicipal = false; municipalFound += ` ${g}: "${hit}"`; }
}
{
  const held = Array.isArray(RULES?.grids?.pjm?.rows) ? RULES.grids.pjm.rows.length : 0, kept = blockOf(RULES, "pjm").rows.length;
  const shown = rowsOfPage(blockOfPage(face(RULE_PAGES.pjm ?? "")) ?? "").filter((p) => p.group === "grid").length;
  check(held > 0 ? shown > 0 && shown === kept : shown === 0, held > 0 ? `PJM shows rows: ${shown} of the ${held} the file holds for it` : `PJM: the file holds no row for it${RULES ? "" : " (it is not there yet)"}, and the block shows none`);
  check(outside(RULE_PAGES.pjm ?? "") === outside(page.html) && /data-grid="pjm"[^>]*data-open="0"[\s\S]{0,400}?licensed source needed/.test(RULE_PAGES.pjm ?? ""),
    'an address that names PJM shows, outside the block, what the default address shows: ERCOT, and PJM\'s prices still read "licensed source needed"');
  check(outside(RULE_PAGES.miso ?? "") === outside(page.html), "an address that names MISO shows, outside the block, what the default address shows");
  check(hovers.neither === 0 && rowsWrong === 0, `every row shown has on its docket's hover either the file's sentence (${hovers.sentence} over the seven addresses) or, where the file does not copy the regulator's text, the file's phrase in its place with the status's class (${hovers.withheld}); neither: ${hovers.neither}; and nothing else but the page, the topic and the tags`);
  check(foldsRight, `eight rows of a group stand before its fold and the rest inside it (${shownTotal} rows over the seven addresses${foldGrid ? "" : "; no group holds more than eight, so no fold is drawn"})`);
  check(noMunicipal, `the block holds none of the words ${MUNICIPAL.map((w) => `"${w}"`).join(", ")}, on its face or on hover${municipalFound ? ` (found:${municipalFound})` : ""}`);
  // the face holds no sentence of the Method note
  const note = new URL("../../docs/methods/datacenter_cost.md", import.meta.url);
  if (fs.existsSync(note)) {
    const sentences = [...new Set(fs.readFileSync(note, "utf-8").split(/\r?\n/).filter((l) => !/^\s*(\||#|```)/.test(l)).join(" ").replace(/[*_`]/g, "").replace(/\[([^\]]*)\]\([^)]*\)/g, "$1").split(/(?<=[.!?])\s+/).map((t) => t.replace(/\s+/g, " ").trim()).filter((t) => t.length >= 40))];
    const faces = RULE_GRIDS.map((g) => plain(blockOfPage(face(RULE_PAGES[g] ?? "")) ?? ""));
    const on = sentences.find((t) => faces.some((f) => f.includes(t)));
    check(sentences.length > 20 && !on, `the block's face holds no sentence of the Method note (${sentences.length} sentences of docs/methods/datacenter_cost.md, seven addresses)${on ? `: "${on.slice(0, 120)}"` : ""}`);
  } else check(false, "docs/methods/datacenter_cost.md is beside the site, so the block's face can be read against it");
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, send, requests, errors, sleep }) => {
  await open(base);
  await go(`${base}/cost-of-power?grid=ercot&run=hours&n=100`);
  await wait(`!!document.querySelector('[data-year-cost] canvas')`, 40000, "the chart");
  const tip = await evaluate(`(() => { const el = document.querySelector('[data-year-cost]'); const chart = window.echarts.getInstanceByDom(el);
    chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 6 });
    return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /Flat load/.test(t)).sort((x, y) => x.length - y.length)[0] ?? ''), 400)); })()`);
  check(/2021/.test(tip) && /Flat load: [\d,.]+ USD\/MWh/.test(tip) && /This load: [\d,.]+ USD\/MWh/.test(tip) && /off in \d+ hours/.test(tip) && /If perfectly foreseen: [\d,.]+ USD\/MWh/.test(tip), `the chart answers the mouse with the year, the load under the rule and the load if perfectly foreseen ("${tip.replace(/\s+/g, " ").slice(0, 190)}")`);
  check(await evaluate(`[...document.querySelectorAll('[data-region] optgroup')].map((o) => o.label).join('|').includes('Load zones')`), "ERCOT's regions are listed as load zones, then trading hubs");
  await sleep(1500);
  const before = requests.length, address = await evaluate("location.href");
  await evaluate(`(() => { const set = (sel, v) => { const el = document.querySelector(sel); const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, v); el.dispatchEvent(new Event('input', { bubbles: true })); };
    set('[data-contract="share"]', '40'); set('[data-contract="price"]', '45'); })()`);
  await wait(`!!document.querySelector('[data-contract-result="shown"]')`, 10000, "the contract result");
  await sleep(1500);
  const shown = await evaluate(`document.querySelector('[data-contract-result="shown"]').innerText`);
  check(/With the contract/.test(shown) && /40 percent of [\d,]+ MWh at USD 45 per MWh/.test(shown) && /per MWh/.test(shown), "the contract's result is shown from the two terms typed");
  const sent = requests.slice(before);
  check(sent.length === 0 && (await evaluate("location.href")) === address, `typing the contract's terms makes no request and leaves the address as it was${sent.length ? ` (${sent.length} requests: ${sent[0].url.slice(0, 100)})` : ""}`);
  check(await evaluate(`(() => { const all = JSON.stringify(Object.entries(localStorage)) + JSON.stringify(Object.entries(sessionStorage)) + document.cookie; return !/45/.test(all.replace(/erw_[a-z]+=[^;]*/g, '')); })()`), "nothing of the contract is in storage or in a cookie");
  await evaluate(`document.querySelector('[data-grid="caiso"] input').click()`);
  await wait(`location.search.includes('grid=caiso') && [...document.querySelectorAll('[data-region] option')].some((o) => o.value.includes('SP15'))`, 20000, "CAISO's regions");
  check(!(await evaluate(`[...document.querySelectorAll('[data-region] option')].some((o) => o.value.startsWith('HB_'))`)), "choosing another grid opens it with its own regions");
  check(await evaluate(`document.querySelector('[data-contract="share"]').value === '40'`), "the contract's terms survive the change of grid");
  {
    // session 154: the rows as the browser holds them, the keyboard, and the fold
    const g = foldGrid?.g ?? "pjm", want = blockOf(RULES, g), all = [...want.rows, ...want.federal];
    await go(`${base}/cost-of-power?grid=${g}`);
    await wait(`!!document.querySelector('[data-rules="1"]')`, 20000, "the block Rules in motion");
    const dom = await evaluate(`[...document.querySelectorAll('[data-rules="1"] a[data-rule-link]')].map((a) => ({ id: a.dataset.ruleLink, href: a.getAttribute('href'), title: a.title, tab: a.tabIndex }))`);
    check(dom.length === all.length && all.every((x, i) => dom[i].id === String(x.id) && dom[i].href === x.url && dom[i].title === docketTip(x) && dom[i].tab === 0),
      all.length ? `in the browser, ${NAMES[g]}: the ${all.length} rows' links carry the file's addresses, and each hover is the file's sentence with its page and topic` : `in the browser, ${NAMES[g]}: no row is in the file, and no row's link is on the page`);
    if (all.length) {
      check(await evaluate(`(() => { const a = document.querySelector('[data-rules="1"] a[data-rule-link]'); a.focus(); const m = document.querySelector('[data-rules="1"] [data-rule-mark], [data-rules="1"] [data-rule-read] [data-missing]'); return document.activeElement === a && !!a.title && !!m && !!m.title; })()`),
        "a row's link takes the keyboard's focus, and its hover and the read's are the elements' titles");
    } else console.log("note: the file holds no row for this grid yet; the keyboard's focus on a row's link was not tried");
    if (foldGrid) {
      const sel = `[data-rules-fold="${foldGrid.group}"]`;
      const seen = `(() => { const d = document.querySelector('${sel}'); const rows = [...d.querySelectorAll('[data-rule]')]; return { open: d.open, rows: rows.length, seen: rows.filter((r) => (r.checkVisibility ? r.checkVisibility() : r.getClientRects().length > 0)).length }; })()`;  // a closed details keeps its rows' boxes and does not draw them: checkVisibility says which
      const before = await evaluate(seen);
      // the summary is brought into the window at once (the site scrolls smoothly by default), then measured where it rests
      await evaluate(`document.querySelector('${sel} summary').scrollIntoView({ block: 'center', behavior: 'instant' })`);
      await sleep(400);
      const at = await evaluate(`(() => { const r = document.querySelector('${sel} summary').getBoundingClientRect(); return { x: r.left + 12, y: r.top + r.height / 2 }; })()`);
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: at.x, y: at.y });
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x: at.x, y: at.y, button: "left", clickCount: 1 });
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: at.x, y: at.y, button: "left", clickCount: 1 });
      await sleep(300);
      const clicked = await evaluate(seen);
      check(!before.open && before.rows === foldGrid.folded && before.seen === 0 && clicked.open && clicked.seen === foldGrid.folded, `the fold opens to a click: ${foldGrid.folded} earlier rows of ${NAMES[g]}'s ${foldGrid.group === "grid" ? "own" : "federal"} group, hidden before it and shown after${clicked.open && before.seen === 0 && !before.open ? "" : ` (before: ${JSON.stringify(before)}; after the click at ${Math.round(at.x)}, ${Math.round(at.y)}: ${JSON.stringify(clicked)})`}`);
      await evaluate(`(() => { const d = document.querySelector('${sel}'); d.open = false; d.querySelector('summary').focus(); })()`);
      await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13, text: "\r" });
      await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13, nativeVirtualKeyCode: 13 });
      await sleep(300);
      const keyed = await evaluate(seen);
      check(keyed.open && keyed.seen === foldGrid.folded, "the fold opens to the keyboard: Enter on its summary");
    } else console.log("note: no group of the file holds more than eight rows, so the page draws no fold; it was not opened here (the fold's rule is tested in scripts/test-rules.mjs)");
    // the seven choices of the block: links that name each grid; MISO's opens the pause, PJM's opens PJM's rules
    await wait(`document.querySelectorAll('[data-rules-nav] [data-rules-choice] a').length === ${RULE_GRIDS.length}`, 20000, "the block's seven choices as links");
    const choices = await evaluate(`[...document.querySelectorAll('[data-rules-nav] [data-rules-choice]')].map((s) => ({ id: s.dataset.rulesChoice, href: s.querySelector('a').getAttribute('href'), tab: s.querySelector('a').tabIndex }))`);
    await evaluate(`document.querySelector('[data-rules-choice="miso"] a').click()`);
    await wait(`document.querySelector('[data-rules="1"]')?.dataset.rulesFor === 'miso'`, 20000, "MISO's block");
    const miso = await evaluate(`(() => { const b = document.querySelector('[data-rules="1"]'); const m = b.querySelector('[data-rules-paused] [data-missing]'); return { words: m?.innerText ?? '', why: m?.title ?? '', rows: b.querySelectorAll('[data-rule], table, details').length, ercot: document.querySelector('[data-grid="ercot"] input').checked }; })()`);
    await evaluate(`document.querySelector('[data-rules-choice="pjm"] a').click()`);
    await wait(`document.querySelector('[data-rules="1"]')?.dataset.rulesFor === 'pjm'`, 20000, "PJM's block");
    const pjm = await evaluate(`({ rows: document.querySelectorAll('[data-rules="1"] [data-rule]').length, ercot: document.querySelector('[data-grid="ercot"] input').checked, chosen: document.querySelector('[data-rules-choice="pjm"]').dataset.rulesChosen })`);
    const pjmWant = blockOf(RULES, "pjm");
    check(choices.length === RULE_GRIDS.length && choices.every((c, i) => c.id === RULE_GRIDS[i] && c.href.includes(`grid=${c.id}`) && c.tab === 0) && miso.words === PAUSED_WORDS && miso.why === PAUSE_WHY && miso.rows === 0 && miso.ercot
      && pjm.rows === pjmWant.rows.length + pjmWant.federal.length && pjm.ercot && pjm.chosen === "1",
      `the block's seven choices are links a keyboard reaches; MISO's opens "${PAUSED_WORDS}" and no row, PJM's opens PJM's block (${pjmWant.rows.length} rows and ${pjmWant.federal.length} federal), and the rest of the page stays ERCOT`);
  }
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
