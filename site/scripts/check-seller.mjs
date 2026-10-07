// Energy Research Warehouse (ERW) site, session 145: "What a generator earns" (/cost-of-power/seller), on the built site.
//
//   npm run build && npx next start -p 3145
//   node --import ./scripts/alias-register.mjs scripts/check-seller.mjs [base-url]      (default http://localhost:3145)
//
// As HTML, in the internal view (the page is in review):
//   opens      200, its title, the three tabs, every section, no "undefined", no NaN, no em dash; it names its Method
//              note and carries no method prose on its face
//   kept       what the seller's tab and its version 2 showed is on the one page: the months and the bad months, debt
//              coverage, the stress days, every month, the spans beside the long-run averages, the fleet's hours
//   numbers    every number of the model equals lib/merchant.ts over the snapshot (its check key); the headline figures equal the arithmetic of lib/seller2.ts over the model's snapshot and of
//              lib/capture.ts over data/seller/capture.json; every cell of the capture table equals the file's figure
//   blank      MISO reads "paused while terms are reviewed" and PJM "licensed source needed", neither selectable; an
//              address that names one opens ERCOT; New York's solar is a placeholder with its reason, and no number
//   hybrid     the battery's figure is the battery page's own, and the combined figure is the sum of its two parts; a
//              grid the battery model does not cover reads "not modeled for this grid"
//   redirect   /cost-of-power/seller/v2 redirects to /cost-of-power/seller and carries its query
//   visitor    without the cookie the page is the in-review page
// In a real browser: each of the four charts is drawn and answers the mouse; the contract's terms make no request,
// leave the address as it was, write nothing to storage or cookies, and show revenue with and without, equal to the
// library's; the link to the curtailment page's free energy carries the grid and the hub; choosing another grid opens
// it with its own hubs.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import * as C from "../lib/capture.ts";
import { contractResult } from "../lib/datacenter.ts";
import * as M from "../lib/merchant.ts";
import * as S from "../lib/seller2.ts";

const base = (process.argv[2] ?? "http://localhost:3145").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const FILE = JSON.parse(fs.readFileSync(new URL("../data/seller/capture.json", import.meta.url), "utf-8"));
const SNAP = JSON.parse(fs.readFileSync(new URL("../data/merchant_snapshot.json", import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {}, redirect: "manual" }); return { status: r.status, html: await r.text(), location: r.headers.get("location") }; };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const face = (html) => { const i = html.indexOf("<h1"); return i < 0 ? "" : html.slice(i); };
const stat = (html, k) => new RegExp(`data-stat="${k}"[^>]*>(?:<span[^>]*>)?([^<]*)<`).exec(html)?.[1] ?? null;
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const METHOD_WORDS = /upper bound|merchant only|does not tell|how it is measured|how a lender|not a site|limitation|cannot see|assum/i;

const page = await get("/cost-of-power/seller");
const html = face(page.html), text = plain(html);
check(page.status === 200 && text.includes("What a generator earns") && !/\bundefined\b|NaN/.test(text) && !page.html.includes(String.fromCharCode(0x2014)), '/cost-of-power/seller opens as "What a generator earns", with no "undefined", no NaN and no em dash');
check(["What a datacenter pays", "What a generator earns", "What a battery earns"].every((t) => plain(/<nav[^>]*aria-label="Cost of power"[\s\S]*?<\/nav>/.exec(page.html)?.[0] ?? "").includes(t)), "the three tabs: What a datacenter pays, What a generator earns, What a battery earns");
check(["capture", "capture-years", "spans", "contract", "hybrid", "months", "coverage"].every((id) => html.includes(`<section id="${id}"`)) && html.includes('data-summary="1"') && (html.match(/class="border-t-2 border-accent pt-2"/g) ?? []).length === 3,
  "the battery page's layout: the summary sentence, three headline numbers, and the sections capture, by year, spans, contract, hybrid, months and coverage");
check(page.html.includes("/data/methods/cost_of_power") || text.includes("Method note"), "the page names its Method note");
check(!METHOD_WORDS.test(text), `no method prose on the page face${METHOD_WORDS.test(text) ? ` (found "${METHOD_WORDS.exec(text)[0]}")` : ""}`);
check(["the median month earned", "10th-percentile month", "The worst three months", "Over trailing twelve months, coverage was", "Stress days: Uri, Elliott and the 2023 heat", "Winter Storm Uri", "Every month: revenue, energy, capture price and rate, coverage",
  "Hours above installed nameplate", "Hours EIA reports negative", "Annual debt payments, USD", "Fixed O&M, USD per kW a year"].every((w) => text.includes(w)) && /data-check="mr\|iso=ercot&amp;asset=solar[^"]*\|median"/.test(html) && /data-check="mr\|[^"]*\|stress_total:uri_2021"/.test(html),
  "what the seller's tab showed is here: the months held, the median and the bad months, debt coverage, the stress days, every month, the fleet's hours, with their check keys");
check((text.match(/Long-run average, a year/g) ?? []).length === 2 && text.includes("Last twelve months") && ["revenue", "energy", "capture", "flat", "rate"].every((k) => html.includes(`data-seller2="twelve|${k}"`)) && text.includes("Revenue by year, USD per kW") && text.includes("Incomplete year"),
  "what version 2 showed is here: the last twelve months beside the two long-run averages, row by row, and revenue by year");
check(/data-grid="miso"[^>]*data-open="0"[\s\S]{0,500}?paused while terms are reviewed/.test(html) && /data-grid="pjm"[^>]*data-open="0"[\s\S]{0,500}?licensed source needed/.test(html)
  && /<input[^>]*disabled=""[^>]*value="miso"|value="miso"[^>]*disabled=""/.test(html) && !/INDIANA|Indiana Hub/.test(page.html), 'MISO reads "paused while terms are reviewed" and PJM "licensed source needed"; neither can be chosen and no MISO hub is named');
check(["ercot", "caiso", "nyiso", "isone", "spp"].every((g) => new RegExp(`data-grid="${g}"[^>]*data-open="1"`).test(html)), "the five public grids can each be chosen");

// every number of the model carries its check key (mr|<inputs>|<stat>) and equals lib/merchant.ts over the snapshot, as
// scripts/check-values.mjs recomputes it, for the four views that script reads
for (const q of ["/cost-of-power/seller", "/cost-of-power/seller?asset=battery", "/cost-of-power/seller?asset=peaker", "/cost-of-power/seller?iso=spp&asset=wind"]) {
  const h = (await get(q)).html;
  let keys = 0, wrong = 0, first = "";
  for (const m of h.matchAll(/data-check="mr\|([^"|]*)\|([^"]*)" data-raw="(-?[\d.e+-]+)"/g)) {
    keys += 1;
    const want = M.stat(SNAP, M.parseKey(m[1].replace(/&amp;/g, "&")), m[2]);
    if (want === null || Math.abs(want - Number(m[3])) > 1e-6 * Math.max(1, Math.abs(want))) { wrong += 1; first ||= `${m[2]}: the page ${m[3]}, the library ${want}`; }
  }
  check(keys > 50 && wrong === 0, `${q}: each of the ${keys} numbers of the model equals the library's over the snapshot${wrong ? ` (${wrong} differ; ${first})` : ""}`);
}

// the headline numbers against the libraries, over the site's own files
for (const [q, grid, hubId, asset] of [
  ["/cost-of-power/seller", "ercot", "HB_HUBAVG", "solar"],
  ["/cost-of-power/seller?iso=ercot&asset=wind&hub=HB_WEST&mw=250", "ercot", "HB_WEST", "wind"],
  ["/cost-of-power/seller?iso=caiso&asset=solar&hub=TH_NP15_GEN-APND", "caiso", "TH_NP15_GEN-APND", "solar"],
  ["/cost-of-power/seller?iso=isone&asset=solar", "isone", ".H.INTERNAL_HUB", "solar"],
  ["/cost-of-power/seller?iso=spp&asset=solar", "spp", "SPPNORTH_HUB", "solar"],
]) {
  const h = (await get(q)).html;
  const hub = C.hubOf(FILE, grid, hubId);
  const market = C.twelve(hub.rt?.[asset], FILE.near) ? "rt" : "da";
  const c = C.twelve(hub[market][asset], FILE.near);
  const s = S.spans(S.monthsOf(SNAP, { grid, asset }));
  const want = { cap_price: C.two(c.price), cap_premium: C.signed(c.premium), cap_pct: C.signed(c.pct, 1), cap_flat: C.two(c.flat), ...(s.twelve ? { l12_kw: S.usd(s.twelve.revenue_kw) } : {}) };
  const got = Object.fromEntries(Object.keys(want).map((k) => [k, stat(h, k)]));
  check(JSON.stringify(got) === JSON.stringify(want) && plain(face(h)).includes(`${C.MARKETS[market].toLowerCase()}, ${C.monthName(c.from)} to ${C.monthName(c.to)}`),
    `${grid} ${hubId}, ${asset}, ${C.MARKETS[market].toLowerCase()}: USD ${want.cap_price} per MWh received, ${want.cap_premium} (${want.cap_pct} percent) against a flat ${want.cap_flat}${want.l12_kw ? `; the model's USD ${want.l12_kw} per kW` : "; the model holds no twelve months"}${JSON.stringify(got) === JSON.stringify(want) ? "" : ` (the page says ${JSON.stringify(got)})`}`);
}
for (const [grid, q] of [["ercot", "/cost-of-power/seller"], ["caiso", "/cost-of-power/seller?iso=caiso"], ["spp", "/cost-of-power/seller?iso=spp&asset=wind"]]) {
  const h = face((await get(q)).html);
  let cells = 0, wrong = 0, blank = 0;
  for (const hub of FILE.grids[grid].hubs) for (const m of ["rt", "da"]) for (const fuel of C.FUELS) {
    const c = C.twelve(hub[m]?.[fuel], FILE.near);
    const cellOf = (what) => new RegExp(`data-cap="${esc(`${hub.id}|${m}|${fuel}|${what}`)}"[^>]*>([^]*?)</span>`).exec(h)?.[1].replace(/<!-- -->/g, "") ?? null;
    const shown = cellOf("price"), prem = cellOf("premium");
    if (!c) { if (shown !== null || prem !== null) wrong += 1; else blank += 1; continue; }
    cells += 1;
    if (shown !== C.two(c.price) || prem !== `${C.signed(c.premium)} (${C.signed(c.pct, 1)} percent)`) wrong += 1;
  }
  check(cells > 0 && wrong === 0, `${grid}: each of the ${cells} figures of the capture table equals the file's, and the ${blank} series without twelve months show no number`);
}
{
  const ny = face((await get("/cost-of-power/seller?iso=nyiso&asset=solar")).html);
  check(/data-seller2-none="1"/.test(ny) && !/data-stat="cap_price"/.test(ny) && !/data-cap="N\.Y\.C\.\|(rt|da)\|solar/.test(ny) && /title="[^"]*EIA-930 itemizes no solar generation for New York[^"]*"/.test(ny) && /data-cap="N\.Y\.C\.\|da\|wind\|price"/.test(ny),
    "New York's solar is a placeholder with its reason on hover and no number; its wind, day-ahead, is shown");
  check(/data-hybrid="none"[\s\S]{0,400}?not modeled for this grid/.test(ny) && /title="[^"]*in review[^"]*"/.test(ny), 'a grid the battery model does not cover reads "not modeled for this grid", with the reason on hover');
  const m = face((await get("/cost-of-power/seller?iso=miso&asset=wind")).html);
  check(/<input[^>]*checked=""[^>]*value="ercot"|value="ercot"[^>]*checked=""/.test(m) && /data-check="mr\|iso=ercot&amp;asset=wind/.test(m), "an address that names MISO opens the default grid, ERCOT");
  const p = plain(face((await get("/cost-of-power/seller?asset=peaker&hr=9.5&vom=3")).html));
  check(p.includes("Heat rate, MMBtu per MWh") && p.includes("Variable O&M, USD per MWh") && p.includes("Margin over fuel, last twelve months") && p.includes("Price while running"), "the gas peaker keeps its inputs, the heat rate and the variable cost, and its margin over fuel");
  const b = plain(face((await get("/cost-of-power/seller?asset=battery")).html));
  check(b.includes("Energy, MWh") && b.includes("Energy alone") && /With your contract\s+not held yet/.test(b), "the battery keeps its energy input, says it is energy alone, and its contract is a placeholder");
}
{
  // the hybrid: the battery page's own figure, and a sum
  for (const [grid, dur, strat, bmw] of [["ercot", 4, "foresight", 100], ["caiso", 8, "dayahead", 50]]) {
    const h = face((await get(`/cost-of-power/seller?iso=${grid}&asset=solar&bmw=${bmw}&dur=${dur}&strat=${strat}`)).html);
    const raw = (k) => { const v = new RegExp(`data-hybrid="${k}" data-raw="(-?[\\d.]+)"`).exec(h)?.[1]; return v === undefined ? null : Number(v); };
    const bp = (await get(`/cost-of-power/battery?grid=${grid}&dur=${dur}&strat=${strat}&mw=${bmw}`, false)).html;
    const theirs = Number(new RegExp(`data-check="bs\\|[^"]*\\|l12:total" data-raw="(-?[\\d.]+)"`).exec(bp)?.[1] ?? NaN);
    check(raw("battery") !== null && raw("battery") === theirs && raw("plant") !== null && raw("combined") === C.combined(raw("plant"), raw("battery")),
      `${grid}, ${bmw} MW ${dur}-hour battery, ${strat}: the battery's USD ${raw("battery")?.toLocaleString("en-US")} is the battery page's own figure, and with the solar plant's USD ${raw("plant")?.toLocaleString("en-US")} the combined figure is their sum, USD ${raw("combined")?.toLocaleString("en-US")}`);
  }
  const w = plain(face((await get("/cost-of-power/seller?asset=wind")).html));
  check(/With a battery beside it\s+A solar plant with a 2, 4 or 8 hour battery/.test(w), "for another asset the hybrid section points to solar");
}
{
  const r = await get("/cost-of-power/seller/v2?iso=caiso&asset=wind");
  check([301, 308].includes(r.status) && r.location?.endsWith("/cost-of-power/seller?iso=caiso&asset=wind"), `/cost-of-power/seller/v2 redirects to /cost-of-power/seller and carries its query (${r.status} ${r.location})`);
  const v = await get("/cost-of-power/seller", false);
  check(!v.html.includes('data-summary="1"') && !/data-stat=/.test(v.html) && /in review/i.test(plain(v.html)), "without the cookie a visitor gets the in-review page");
}

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, requests, errors, sleep }) => {
  await open(base);
  await go(`${base}/cost-of-power/seller?iso=ercot&asset=solar&hub=HB_WEST`);
  await wait(`['premium','years','months','coverage'].every((k) => !!document.querySelector('[data-chart="' + k + '"] canvas'))`, 40000, "the four charts");
  const tip = (k, i, re) => evaluate(`(() => { const el = document.querySelector('[data-chart="${k}"]'); const chart = window.echarts.getInstanceByDom(el);
    chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: ${i} });
    return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => ${re}.test(t)).sort((x, y) => x.length - y.length)[0] ?? ''), 400)); })()`);
  const t1 = await tip("premium", 2, "/Solar:/");
  check(/2021/.test(t1) && /Solar: [\d,.]+ USD\/MWh received, [+-][\d,.]+ \([+-][\d,.]+ percent\) against a flat [\d,.]+, [\d,]+ hours/.test(t1) && /Wind: /.test(t1) && /West hub/.test(t1), `the capture chart answers the mouse with the year, the hub and both fuels ("${t1.replace(/\s+/g, " ").slice(0, 150)}")`);
  const t2 = await tip("years", 3, "/USD per kW/");
  check(/2021/.test(t2) && /Revenue: [\d,.]+ USD per kW/.test(t2), `the chart of revenue by year answers the mouse ("${t2.replace(/\s+/g, " ").slice(0, 80)}")`);
  const t3 = await tip("months", 5, "/Revenue:/");
  check(/\d{4}-\d{2}/.test(t3) && /Revenue: [\d,.]+( million)? USD/.test(t3), `the chart of the months answers the mouse ("${t3.replace(/\s+/g, " ").slice(0, 100)}")`);
  const t4 = await tip("coverage", 5, "/Coverage:/");
  check(/The twelve months to \d{4}-\d{2}/.test(t4) && /Coverage: -?[\d.]+ times/.test(t4), `the chart of debt coverage answers the mouse ("${t4.replace(/\s+/g, " ").slice(0, 80)}")`);
  const link = await evaluate(`document.querySelector('[data-free-energy] a')?.getAttribute('href') ?? null`);
  check(link === C.freeEnergyHref("ercot", "HB_WEST"), `the link to the curtailment page's free energy carries the grid and the hub (${link})`);
  await sleep(1500);
  const before = requests.length, address = await evaluate("location.href");
  await evaluate(`(() => { const set = (sel, v) => { const el = document.querySelector(sel); const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, v); el.dispatchEvent(new Event('input', { bubbles: true })); };
    set('[data-contract="share"]', '40'); set('[data-contract="price"]', '45'); })()`);
  await wait(`!!document.querySelector('[data-contract-result="shown"]')`, 10000, "the contract result");
  await sleep(1500);
  const shown = await evaluate(`document.querySelector('[data-contract-result="shown"]').innerText`);
  const attrs = await evaluate(`(() => { const el = document.querySelector('[data-contract-result="shown"]'); return [Number(el.getAttribute('data-contract-with')), Number(el.getAttribute('data-contract-without'))]; })()`);
  // the same from the files: the model's energy over the capture price's twelve months, at the hub's price
  const hub = C.hubOf(FILE, "ercot", "HB_WEST"), months = hub.rt.solar, win = C.lastTwelve(months, FILE.near), cap = C.twelve(months, FILE.near);
  const ms = S.monthsOf(SNAP, { grid: "ercot", asset: "solar" });
  const energy = win.reduce((e, m) => e + ms.find((r) => r.m === m).energy, 0);
  const want = contractResult(C.contractSpan(energy, cap.price), 100, { share: 40, price: 45 });
  check(/Revenue with the contract/.test(shown) && /Revenue without it/.test(shown) && /40 percent of [\d,]+ MWh at USD 45 per MWh/.test(shown) && attrs[0] === Math.round(want.total) && attrs[1] === Math.round(want.without),
    `the contract shows revenue with (USD ${attrs[0].toLocaleString("en-US")}) and without (USD ${attrs[1].toLocaleString("en-US")}), equal to the library's over the site's files`);
  const sent = requests.slice(before);
  check(sent.length === 0 && (await evaluate("location.href")) === address, `typing the contract's terms makes no request and leaves the address as it was${sent.length ? ` (${sent.length} requests: ${sent[0].url.slice(0, 100)})` : ""}`);
  check(await evaluate(`(() => { const all = JSON.stringify(Object.entries(localStorage)) + JSON.stringify(Object.entries(sessionStorage)) + document.cookie; return !/45/.test(all.replace(/erw_[a-z]+=[^;]*/g, '')); })()`), "nothing of the contract is in storage or in a cookie");
  check(await evaluate(`!document.querySelector('[data-contract-inputs] input[name]') && !document.querySelector('[data-contract-inputs]').closest('form')`), "the contract's fields have no name and stand in no form");
  await evaluate(`document.querySelector('[data-grid="caiso"] input').click()`);
  await wait(`location.search.includes('iso=caiso') && [...document.querySelectorAll('[data-hub] option')].some((o) => o.value.includes('SP15'))`, 20000, "CAISO's hubs");
  check(!(await evaluate(`[...document.querySelectorAll('[data-hub] option')].some((o) => o.value.startsWith('HB_'))`)), "choosing another grid opens it with its own hubs");
  check(await evaluate(`document.querySelector('[data-contract="share"]').value === '40'`), "the contract's terms survive the change of grid");
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
