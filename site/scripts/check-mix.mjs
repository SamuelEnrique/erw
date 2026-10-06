// Energy Research Warehouse (ERW) site, session 133: the one energy mix page, on the built site.
//
//   npm run build && npx next start -p 3133
//   node --import ./scripts/alias-register.mjs scripts/check-mix.mjs [base-url]      (default http://localhost:3133)
//
// As HTML, in the internal view (the page is in review):
//   views       each of the nine views answers 200 with its own sections, no "undefined", no NaN, no "not held" prose
//   original    the first view is the original page: its two selects, its three sections
//   numbers     figures of the average day, the clean view, the stress view, availability and the long history equal the
//               site's files (data/mix, data/clean, data/stress, data/mixplus, data/mix_history.json)
//   california  the months of the hydro gap are on the page, from CAISO's own data
//   blanked     MISO's price factor reads "paused while terms are reviewed" and PJM's "licensed source needed"
//   no method   the page face carries no methodology words; it names its Method note
//   retired     /mix/v2, /mix/clean and /mix/stress redirect to the view each became, with their grids
//   visitor     without the cookie the page is the in-review page
// In a real browser: every view draws its charts; a chart answers the mouse; "Select grids" adds a second grid beside
// the first and the address holds it.
// Exit 1 on a failure.
import fs from "node:fs";
import { env, withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3133").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => JSON.parse(fs.readFileSync(new URL(`../data/${p}`, import.meta.url), "utf-8"));
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true, redirect = "follow") => { const r = await fetch(base + path, { redirect, headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text(), location: r.headers.get("location") }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const n0 = (v) => Math.round(v).toLocaleString("en-US");
const n1 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

const VIEWS = { now: "today so far", day: "Generation by fuel, by hour", duck: "year after year", records: "the records", clean: "Carbon-free share of generation, by year", stress: "The largest evening ramp of each year",
  supply: "Output as a share of installed capacity, by hour", forecast: "forecast a day ahead against actual", history: "Net generation by fuel, by year since 2001" };
const pages = {};
for (const [view, words] of Object.entries(VIEWS)) {
  const r = await get(view === "now" ? "/mix" : `/mix?view=${view}`);
  pages[view] = r.html;
  const t = text(r.html);
  const face = /\b(methodology|limitations?|disputed)\b|\bnot held\b(?! yet)|no data:/i.exec(t);
  check(r.status === 200 && r.html.includes(`data-mix="${view}"`) && t.includes(words) && !/\bundefined\b|NaN/.test(t) && !face && t.includes("Method, sources and gaps"),
    `${view}: opens, shows "${words}", carries no method${face ? ` (found "${face[0]}")` : ""}`);
}
check(/name="ba"/.test(pages.now) && /name="state"/.test(pages.now) && ["today so far", "hourly mix, last 7 days", "monthly mix since 2001"].every((w) => text(pages.now).includes(w)), "the first view is the original page: its two selects and its three sections");
check(Object.keys(VIEWS).every((v) => pages.now.includes(`data-view="${v}"`)), "the nine views are one click apart on every view");

// numbers against the files
{
  const mix = read("mix/ercot.json");
  const p = mix.months[mix.upto];
  const t = text(pages.day);
  const top = Object.entries(p).filter(([k]) => k.endsWith("_share_pct")).sort((a, b) => b[1] - a[1])[0];
  check(t.includes(`${n1(top[1])}%`) && t.includes(n0(p.natural_gas_mwh)) && t.includes(n0(p.days_held)), `the average day: ERCOT's ${mix.upto} shares and MWh are the file's (${top[0]} ${n1(top[1])}%)`);
  const clean = read("clean/ercot.json");
  const tc = text(pages.clean);
  const years = Object.keys(clean.years).sort();
  const cy = years.filter((y) => clean.years[y].months === 12).at(-1) ?? years.at(-1);
  check(tc.includes(`${n1(clean.years[cy].carbon_free_share_pct)}%`) && tc.includes(`The seven grids, ${cy}`), `how clean: ERCOT's ${cy} carbon-free share is the file's (${n1(clean.years[cy].carbon_free_share_pct)}%)`);
  const stress = read("stress/ercot.json");
  const ts = text(pages.stress);
  const sy = Object.keys(stress.years).sort().filter((y) => stress.years[y].hours_in_year >= 8760).at(-1);
  check(ts.includes(n0(stress.years[sy].peak_demand_mw)) && ts.includes(n0(stress.years[sy].evening_ramp_max_mw_per_h)), `how hard: ERCOT's ${sy} peak demand and largest ramp are the file's`);
  const first = Object.keys(stress.years).sort()[0];
  const sup = text(pages.supply);
  check(stress.from_year === 2019 && sup.includes(`${n1(stress.years[first].tight_natural_gas_share_of_capacity_pct)}%`) && sup.includes(`${n1(stress.years[first].tight_nuclear_share_of_capacity_pct)}%`),
    `availability: gas and nuclear in the tightest hours of ${first} are shown (capacity is held from 2019 now)`);
  const hist = read("mix_history.json");
  const us = hist.states.US;
  const total = (y) => hist.fuels.reduce((a, f) => a + (us[y][f] ?? 0), 0);
  const th = text(pages.history);
  check(th.includes(`${n1((100 * us["2001"].coal) / total("2001"))}%`) && th.includes(n1(us["2001"].coal / 1e6)), `since 2001: the US coal share of 2001 is the file's (${n1((100 * us["2001"].coal) / total("2001"))}%)`);
  const fc = read("mix_forecast.json").grids.caiso.sources.wind;
  check(text(pages.forecast).includes(n0(fc.all.n)) && /NYISO\s+not held yet/.test(text(pages.forecast)) && /MISO\s+paused while terms are reviewed/.test(text(pages.forecast)) && /PJM\s+licensed source needed/.test(text(pages.forecast)),
    "forecasts: CAISO's hours are the file's; the grids with none are listed with their placeholder");
}
{
  const r = await get("/mix?view=day&grids=caiso&period=2020-03");
  const t = text(r.html);
  const c = read("mix/caiso.json").months["2020-03"];
  check(!!c && c.side === "caiso" && t.includes("from CAISO's own data") && t.includes(`${n1(c.hydro_share_pct)}%`), `California, March 2020 (inside the hydro gap): on the page from CAISO's own data, hydro ${c ? n1(c.hydro_share_pct) : "?"}%`);
  const m = text((await get("/mix?view=day&grids=miso,pjm&factor=price")).html);
  check(m.includes("paused while terms are reviewed") && m.includes("licensed source needed"), "the price factor: MISO paused, PJM licensed, in the placeholder's words");
  const four = await get("/mix?view=day&grids=ercot,caiso,pjm,miso,spp");
  check((four.html.match(/data-chart="stack"/g) ?? []).length === 4 && four.html.includes("Up to 4 grids at once"), "five grids asked: four stacks drawn side by side, and the fifth is not offered");
}
for (const [old, want] of [["/mix/v2?grid=caiso&vs=ercot&period=2026-04", ["view=day", "grid=caiso", "vs=ercot", "period=2026-04"]], ["/mix/clean?grid=nyiso&year=2024", ["view=clean", "grid=nyiso", "year=2024"]], ["/mix/stress", ["view=stress"]]]) {
  const r = await get(old, true, "manual");
  const [path, query = ""] = (r.location ?? "").split("?");
  check((r.status === 308 || r.status === 301) && path === "/mix" && want.every((w) => query.split("&").includes(w)), `${old} redirects to its view and carries its query over (${r.status} ${r.location})`);
}
const v = await get("/mix?view=day", false);
check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes('data-chart='), "as a visitor: the in-review page, and nothing of the mix");

const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, errors }) => {
  await open(base);
  for (const [view, kinds] of [["day&grids=ercot,caiso&factor=price", ["stack"]], ["duck&grids=caiso,ercot", ["lines"]], ["clean", ["bars", "heat"]], ["stress&grids=ercot,pjm", ["lines"]], ["supply", ["lines", "stack"]], ["forecast", ["lines", "bars", "heat"]], ["history&states=US,TX", ["lines"]]]) {
    await go(`${base}/mix?view=${view}`);
    await wait(kinds.map((k) => `!!document.querySelector('[data-chart="${k}"] canvas')`).join(" && "), 30000, `the charts of ${view}`);
    check(true, `${view.split("&")[0]}: its charts are drawn (${kinds.join(", ")})`);
  }
  await go(`${base}/mix`);
  await wait(`!!document.querySelector('#hourly canvas, #monthly canvas')`, 30000, "the original view's charts");
  check(true, "now: the original view's charts are drawn");
  // a chart answers the mouse: the tooltip of the first stack names the hour, a source and a value
  await go(`${base}/mix?view=day&grids=ercot`);
  await wait(`!!document.querySelector('[data-chart="stack"] canvas')`, 30000, "the stack");
  // the chart's own tooltip, shown where the mouse would be at the thirteenth hour
  const tip = await evaluate(`(() => { const el = document.querySelector('[data-chart="stack"]'); const chart = window.echarts.getInstanceByDom(el);
    chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 13 });
    return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /Natural gas/.test(t)).sort((x, y) => x.length - y.length)[0] ?? ''), 400)); })()`);
  check(/\d\d:00/.test(tip) && /Natural gas/.test(tip) && /MW/.test(tip), `a chart answers the mouse with the hour, the series and the value ("${tip.replace(/\s+/g, " ").slice(0, 110)}")`);
  await evaluate(`document.querySelector('[data-chip="Select grids:caiso"]').click()`);
  await wait(`location.search.includes('grids=ercot%2Ccaiso') && document.querySelectorAll('[data-chart="stack"]').length === 2`, 15000, "the second grid");
  check(true, "Select grids adds a second grid beside the first, and the address holds it");
  await evaluate(`document.querySelector('[data-chip="Scale:peak"]').click()`);
  await wait(`location.search.includes('norm=peak')`, 15000, "share of peak");
  check((await evaluate(`document.body.innerText`)).includes("Shares of generation by source"), "the share-of-peak switch is in the address and the view stays");
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
  return 0;
});
if (code === null) console.log("not proven here: no browser on this machine (the HTML checks above stand)");
console.log(`${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
