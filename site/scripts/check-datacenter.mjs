// Energy Research Warehouse (ERW) site, session 138: "What a datacenter pays" (/cost-of-power), on the built site.
//
//   npm run build && npx next start -p 3138
//   node scripts/check-datacenter.mjs [base-url]      (default http://localhost:3138)
//
// As HTML, in the internal view (the page is in review):
//   opens      200, its title, the three tabs, the four questions, no "undefined", no NaN; it names its Method note
//   numbers    the summary sentence's figures equal the arithmetic of lib/datacenter.ts over the site's own files, for
//              a flat load, a load off in 100 hours a year bought day-ahead, and a shifting load in California
//   uneven     a zone held for weeks reads "not held yet" with the date it is held from on hover, and no number
//   blank      MISO reads "paused while terms are reviewed" and PJM "licensed source needed", neither selectable; an
//              address that names one opens the default grid
//   nowhere    large load in line by region, and how long a new large load waits: "not published anywhere yet"
//   view       ?view=grids is what the tab showed before: its ranking, ERCOT since 2018, the hours of the day, cost
//              against carbon and the calculator
//   visitor    without the cookie the page is the in-review page
// In a real browser: the chart is drawn and answers the mouse with the year and its figures; the contract's terms make
// no request, leave the address as it was, write nothing to storage or cookies, and show the result; choosing another
// grid opens that grid with its own regions.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";
import { gpuHour, lastTwelve, monthsOf, span, two, usdShort } from "../lib/datacenter.ts";

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
  ["/cost-of-power", "ercot", "HB_HUBAVG", "rt", { run: "flat", n: 0, pct: 0, shift: 0 }],
  ["/cost-of-power?grid=ercot&region=HB_WEST&mw=250&run=hours&n=100&buy=da", "ercot", "HB_WEST", "da", { run: "hours", n: 100, pct: 0, shift: 0 }],
  ["/cost-of-power?grid=caiso&run=shift&shift=20&buy=rt", "caiso", index.grids.caiso.main, "rt", { run: "shift", n: 0, pct: 0, shift: 20 }],
]) {
  const h = (await get(q)).html;
  const mw = Number(/[?&]mw=(\d+)/.exec(q)?.[1] ?? 100);
  const s = span(lastTwelve(monthsOf(files(grid), region, buy, x)));
  const want = { l12_per: two(s.per), l12_cost: usdShort(s.cost * mw), gpu_hour: gpuHour(s.per, 1.3, 1.56).toFixed(4), ...(x.run === "flat" ? {} : { l12_saved: two(s.flat - s.per) }) };
  const got = Object.fromEntries(Object.keys(want).map((k) => [k, stat(h, k)]));
  check(JSON.stringify(got) === JSON.stringify(want), `${grid} ${region}, ${x.run}, ${buy}, ${mw} MW: USD ${want.l12_per} per MWh over the last twelve months, USD ${want.l12_cost} in all, USD ${want.gpu_hour} per GPU-hour${want.l12_saved ? `, USD ${want.l12_saved} saved` : ""}${JSON.stringify(got) === JSON.stringify(want) ? "" : ` (the page says ${JSON.stringify(got)})`}`);
}
{
  const zone = index.grids.nyiso.regions.find((r) => r.id !== index.grids.nyiso.main).id;
  const h = face((await get(`/cost-of-power?grid=nyiso&region=${encodeURIComponent(zone)}&buy=da`)).html);
  const sum = /data-summary="1"[\s\S]*?<\/p>/.exec(h)?.[0] ?? "";
  check(/data-missing="1"/.test(sum) && /title="[^"]*held from[^"]*"/.test(sum) && plain(sum).includes("not held yet") && !/data-stat=/.test(sum), `a zone held for weeks (NYISO ${zone}) reads "not held yet" with the date it is held from on hover, and no number`);
  const m = face((await get("/cost-of-power?grid=miso")).html);
  check(/<input[^>]*checked=""[^>]*value="ercot"|value="ercot"[^>]*checked=""/.test(m), "an address that names MISO opens the default grid, ERCOT");
  const other = face((await get("/cost-of-power?grid=caiso")).html);
  check(/Delivery charges\s+not held yet/.test(plain(other)), 'another grid shows "delivery charges: not held yet"');
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
  check(/2021/.test(tip) && /Flat load: [\d,.]+ USD\/MWh/.test(tip) && /This load: [\d,.]+ USD\/MWh/.test(tip) && /off in 100 hours/.test(tip), `the chart answers the mouse with the year and its figures ("${tip.replace(/\s+/g, " ").slice(0, 140)}")`);
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
