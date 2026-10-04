// Energy Research Warehouse (ERW) site, session 97: the demand growth explorer, on the built site.
//
//   npm run build && npx next start -p 3097
//   node --import ./scripts/alias-loader.mjs scripts/check-demand.mjs [base-url]      (default http://localhost:3097)
//
// The page is drawn on the server, so it is read as HTML, in the internal view (it is in review):
//   numbers   every number the page marks (data-n) equals the site's copy of eia930_demand_growth
//             (data/demand_growth.json), for every area
//   charts    a bar per whole year; a cell per month and hour the table holds; twelve months and 24 hours of change
//   ranking   the areas in the order of the measure asked for, an area that lacks it last
//   weather   "weather is not removed" is on the page, above the tool
//   peaks     each year's peak with its local date; the Lower 48 with no peak, and the reason
//   break     California's check across December 2025, with its rows, on California's page only
//   visitor   without the cookie the page is the in-review page and carries no number
// Exit 1 on a failure.
import fs from "node:fs";
import { env } from "./browser.mjs";
import * as g from "../lib/demandgrowth.ts";

const base = (process.argv[2] ?? "http://localhost:3097").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const file = JSON.parse(fs.readFileSync(new URL("../data/demand_growth.json", import.meta.url), "utf-8"));

const token = env("INTERNAL_COSTS_TOKEN");
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (path, withCookie = true) => { const r = await fetch(base + path, { headers: withCookie ? { Cookie: cookie } : {} }); return { status: r.status, html: await r.text() }; };
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const marked = (html) => Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [x[1], x[2]]));

async function view(slug, rankSlug) {
  const path = g.href(slug, rankSlug);
  const { status, html } = await get(path);
  const tag = `${path}:`;
  check(status === 200 && !html.includes('data-in-review="1"'), `${tag} opens in the internal view`);
  const { ba, rank } = g.choices({ area: slug, rank: rankSlug });
  const a = file.areas[ba], got = marked(html), ys = g.wholeYears(a), first = ys[0], last = ys.at(-1), ytd = g.yearToDate(file, a);
  const wrong = [];
  const want = (k, val) => { if (got[k] !== val) wrong.push(`${k}: page ${got[k]}, copy ${val}`); };
  const maybe = (k, v, f) => { if (v === undefined) { if (k in got) wrong.push(`${k}: on the page, not in the copy`); } else want(k, f(v)); };
  want("sum|avg0", g.whole(first.row.avg_demand_mw));
  want("sum|avg1", g.whole(last.row.avg_demand_mw));
  want("sum|avg_growth", g.signed(last.row.avg_demand_growth_since_2019_pct));
  want("head|avg_growth", g.signed(last.row.avg_demand_growth_since_2019_pct));
  maybe("sum|peak1", last.row.peak_demand_mw, g.whole);
  maybe("head|peak_growth", last.row.peak_demand_growth_since_2019_pct, g.signed);
  want("sum|ytd_growth", g.signed(ytd.row.ytd_avg_demand_growth_since_2019_pct));
  want("head|ytd1", g.whole(ytd.row.ytd_avg_demand_mw));
  want("head|ytd0", g.whole(ytd.base.ytd_avg_demand_mw));
  for (const { year, row } of ys) {
    want(`y|${year}|avg`, g.whole(row.avg_demand_mw));
    maybe(`y|${year}|avg_growth`, row.avg_demand_growth_since_2019_pct, g.signed);
    maybe(`y|${year}|yoy`, row.avg_demand_growth_yoy_pct, g.signed);
    maybe(`y|${year}|peak`, row.peak_demand_mw, g.whole);
    maybe(`y|${year}|peak_growth`, row.peak_demand_growth_since_2019_pct, g.signed);
    want(`y|${year}|hours`, g.whole(row.hours_used));
  }
  want("ytd|avg", g.whole(ytd.row.ytd_avg_demand_mw));
  maybe("ytd|peak", ytd.row.ytd_peak_demand_mw, g.whole);
  const cs = g.cells(file, a), ex = g.extremes(cs);
  want("cell|most|pct", g.signed(ex.most.pct));
  want("cell|least|pct", g.signed(ex.least.pct));
  const ranked = g.ranking(file, rank);
  for (const r of ranked) { maybe(`rank|${r.ba}|avg`, r.avg, g.signed); maybe(`rank|${r.ba}|peak`, r.peak, g.signed); maybe(`rank|${r.ba}|ytd`, r.ytd, g.signed); }
  check(wrong.length === 0, `${tag} every marked number is the copy's (${Object.keys(got).length} on the page)${wrong.length ? `: ${wrong.slice(0, 5).join("; ")}` : ""}`);
  const bars = [...html.matchAll(/data-year="(\d{4})"/g)].map((x) => x[1]);
  const drawn = [...html.matchAll(/data-cell="(\d+\|\d+)"/g)].length;
  check(bars.join() === ys.map((y) => y.year).join() && drawn === cs.length && html.includes('data-chart="by month"') && html.includes('data-chart="by hour"'),
    `${tag} ${bars.length} years drawn, ${drawn} month-and-hour cells, and the change by month and by hour`);
  const order = [...html.matchAll(/data-ranked="(\d+)\|([A-Z0-9]+)"/g)].map((x) => x[2]);
  check(order.join() === ranked.map((r) => r.ba).join(), `${tag} the ranking by ${rank.slug}: ${order.join(", ")}`);
  const t = text(html);
  check(html.includes('data-weather="1"') && t.includes("Weather is not removed.") && t.indexOf("Weather is not removed.") < t.indexOf("Year by year"), `${tag} "weather is not removed", above the tool`);
  const peak = a.at[last.year]?.peak_demand_mw;
  check(peak ? t.includes(g.localHour(peak, a.tz)) : t.includes("No peak is given for the Lower 48"), `${tag} ${peak ? `the peak of ${last.year} is dated ${g.localHour(peak, a.tz)}` : "no peak for the Lower 48, and the reason"}`);
  check((ba === "CISO") === html.includes('data-break="1"'), `${tag} the check across December 2025 is ${ba === "CISO" ? "shown" : "not shown"}`);
  if (ba === "CISO") {
    const bw = [];
    for (const r of file.caiso_break.rows) { if (got[`break|${r.year}|ratio`] !== r.ratio.toFixed(4)) bw.push(r.year); if (got[`break|${r.year}|before`] !== g.whole(r.before_mw)) bw.push(r.year); }
    check(bw.length === 0 && t.includes("California's demand does not step at the break"), `${tag} the break check's ${file.caiso_break.rows.length} rows are the copy's, and its sentence`);
  }
  check(!/\bundefined\b|NaN/.test(t), `${tag} no "undefined" and no NaN in the text`);
}

for (const slug of Object.keys(g.SLUGS)) await view(slug, "avg");
await view("ercot", "peak");
await view("pjm", "ytd");
{
  const d = await get("/demand?area=mars&rank=luck");
  check(d.status === 200 && marked(d.html)["sum|avg1"] === g.whole(g.wholeYears(file.areas.ERCO).at(-1).row.avg_demand_mw), "an address it does not understand opens ERCOT, ranked by average demand");
  const v = await get(g.href("ercot", "avg"), false);
  check(v.status === 200 && v.html.includes('data-in-review="1"') && !v.html.includes("data-n="), "as a visitor: the in-review page, and no number of the tool");
}
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
