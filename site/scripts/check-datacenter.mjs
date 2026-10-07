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
// In a real browser: the chart is drawn and answers the mouse with the year and its figures; the contract's terms make
// no request, leave the address as it was, write nothing to storage or cookies, and show the result; choosing another
// grid opens that grid with its own regions.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { cleanShare, expandSeries, gpuHour, lastTwelve, monthsOf, monthsRuled, span, two, usdShort } from "../lib/datacenter.ts";

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
  const nyh = (await get("/cost-of-power?grid=nyiso&region=CENTRL&buy=da")).html, mine = q.zones.find((z) => z.zone_name === "CENTRL");
  check(/data-nyload="1"/.test(nyh) && new RegExp(`${mine.mw.toLocaleString("en-US")} MW in ${mine.requests} requests in CENTRL`).test(plain(nyh)) && new RegExp(`${q.total.mw.toLocaleString("en-US")} MW in ${q.total.requests} requests in New York`).test(plain(nyh))
    && q.zones.every((z) => nyh.includes(`data-nyload-zone="${z.zone_name}"`)) && /How long a new large load waits\s+not published anywhere yet/.test(ny),
    `New York's load in line by zone is NYISO's own list: ${mine.mw.toLocaleString("en-US")} MW in ${mine.requests} requests in CENTRL, ${q.total.mw.toLocaleString("en-US")} MW in ${q.total.requests} in all, each zone with its statuses and its source on hover`);
  const inLine = q.rows.filter((r) => r.in_line);
  check(inLine.length === q.total.requests && inLine.every((r) => nyh.includes(`>${r.queue_position}</a>`)) && nyh.includes(q.source.url), `the ${inLine.length} requests in line are listed one by one, each linked to NYISO's workbook with its sheet and row on hover`);
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

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, requests, errors, sleep }) => {
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
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
